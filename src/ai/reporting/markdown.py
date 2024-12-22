from typing import List, Dict, Any, Optional
from datetime import datetime
import statistics
from collections import Counter

from .base import ReportGenerator, ReviewReport, ReportSection
from .templates import registry
from .templates.standard import ExecutiveSummaryTemplate, SecurityAuditTemplate, PerformanceReportTemplate
from ..models.response import AIResponse
from ..models.request import ReviewType
from ..storage.base import ReviewRecord


class MarkdownReportGenerator(ReportGenerator):
    """Generate reports in Markdown format."""

    def __init__(self, include_metrics: bool = True):
        self.include_metrics = include_metrics

        # Register standard templates
        registry.register(ExecutiveSummaryTemplate())
        registry.register(SecurityAuditTemplate())
        registry.register(PerformanceReportTemplate())

    def _format_severity(self, severity: str) -> str:
        """Format severity level with emoji."""
        severity_icons = {
            "error": "🔴",
            "warning": "🟡",
            "suggestion": "🔵",
            "praise": "💚"
        }
        return f"{severity_icons.get(severity, '•')} {severity.title()}"

    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics as a Markdown table."""
        if not metrics:
            return ""

        table = "| Metric | Value |\n|--------|-------|\n"
        for key, value in metrics.items():
            if isinstance(value, float):
                value = f"{value:.2f}"
            table += f"| {key} | {value} |\n"
        return table

    def _calculate_review_metrics(self, review: AIResponse) -> Dict[str, Any]:
        """Calculate metrics for a single review."""
        if not self.include_metrics:
            return {}

        severity_counts = Counter(c.severity for c in review.comments)
        category_counts = Counter(c.category for c in review.comments)

        return {
            "Total Comments": len(review.comments),
            "Errors": severity_counts["error"],
            "Warnings": severity_counts["warning"],
            "Suggestions": severity_counts["suggestion"],
            "Praise": severity_counts["praise"],
            "Quality Score": review.score if review.score is not None else "N/A"
        }

    async def generate_file_report(
        self,
        review: AIResponse,
        file_path: str,
        review_type: ReviewType,
        include_code: bool = False,
        template_id: Optional[str] = None
    ) -> ReviewReport:
        """Generate a Markdown report for a single file review."""
        if template_id:
            template = registry.get_template(template_id)
            if template:
                context = {
                    "review": review,
                    "file_path": file_path,
                    "review_type": review_type,
                    "include_code": include_code
                }
                if template.validate_context(context):
                    sections = template.render(context)
                    return ReviewReport(
                        title=f"{template.name}: {file_path}",
                        summary=review.summary,
                        sections=sections,
                        metadata={
                            "template_id": template_id,
                            "file_path": file_path,
                            "review_type": review_type.value
                        }
                    )

        # Fall back to default report format
        metrics = self._calculate_review_metrics(review)

        # Overview section
        overview = ReportSection(
            title="Overview",
            content=f"""## Review Summary
{review.summary}

### File Information
- **File:** `{file_path}`
- **Review Type:** {review_type.value}
- **Timestamp:** {datetime.utcnow().isoformat()}

{self._format_metrics(metrics) if metrics else ""}""",
            metrics=metrics
        )

        # Comments by severity
        severity_sections = []
        for severity in ["error", "warning", "suggestion", "praise"]:
            comments = review.get_comments_by_severity(severity)
            if not comments:
                continue

            content = f"## {self._format_severity(severity)} Comments\n\n"
            for comment in comments:
                content += f"### {'Line ' + str(comment.line_number) if comment.line_number else 'General'}\n"
                content += f"{comment.content}\n\n"
                if comment.suggested_fix and include_code:
                    content += f"**Suggested Fix:**\n```\n{comment.suggested_fix}\n```\n\n"

            severity_sections.append(ReportSection(
                title=f"{severity.title()} Comments",
                content=content,
                severity=severity,
                metrics={"count": len(comments)}
            ))

        return ReviewReport(
            title=f"Code Review: {file_path}",
            summary=review.summary,
            sections=[overview] + severity_sections,
            metadata={
                "file_path": file_path,
                "review_type": review_type.value,
                "metrics": metrics
            }
        )

    async def generate_multi_file_report(
        self,
        reviews: Dict[str, AIResponse],
        review_type: ReviewType,
        include_code: bool = False,
        template_id: Optional[str] = None
    ) -> ReviewReport:
        """Generate a Markdown report for multiple file reviews."""
        all_metrics = {}
        file_sections = []
        total_issues = 0

        # Generate individual file reports
        for file_path, review in reviews.items():
            report = await self.generate_file_report(
                review,
                file_path,
                review_type,
                include_code,
                template_id
            )
            metrics = self._calculate_review_metrics(review)
            all_metrics[file_path] = metrics
            total_issues += len(review.comments)

            # Add file section
            file_content = f"## {file_path}\n\n{report.summary}\n\n"
            file_content += self._format_metrics(metrics) if metrics else ""
            file_sections.append(ReportSection(
                title=file_path,
                content=file_content,
                metrics=metrics
            ))

        # Calculate overall metrics
        overall_metrics = {
            "Total Files": len(reviews),
            "Total Issues": total_issues,
            "Average Issues per File": total_issues / len(reviews) if reviews else 0,
            "Average Quality Score": statistics.mean(
                [r.score for r in reviews.values() if r.score is not None]
            ) if any(r.score is not None for r in reviews.values()) else None
        }

        # Create overview section
        overview = ReportSection(
            title="Overview",
            content=f"""# Multi-File Review Report

## Summary
- Reviewed {len(reviews)} files
- Found {total_issues} total issues
- Review Type: {review_type.value}
- Generated: {datetime.utcnow().isoformat()}

{self._format_metrics(overall_metrics)}""",
            metrics=overall_metrics
        )

        return ReviewReport(
            title="Multi-File Code Review Report",
            summary=f"Review of {len(reviews)} files",
            sections=[overview] + file_sections,
            metadata={
                "review_type": review_type.value,
                "file_count": len(reviews),
                "metrics": overall_metrics,
                "template_id": template_id
            }
        )

    async def generate_historical_report(
        self,
        reviews: List[ReviewRecord],
        file_path: Optional[str] = None,
        review_type: Optional[ReviewType] = None
    ) -> ReviewReport:
        """Generate a Markdown report analyzing review history."""
        if not reviews:
            return ReviewReport(
                title="Historical Review Analysis",
                summary="No review history available",
                sections=[]
            )

        # Calculate historical metrics
        review_counts = len(reviews)
        quality_scores = [
            r.review_response.score for r in reviews if r.review_response.score is not None]
        avg_score = statistics.mean(quality_scores) if quality_scores else None

        metrics = {
            "Total Reviews": review_counts,
            "Average Quality Score": f"{avg_score:.2f}" if avg_score is not None else "N/A",
            "First Review": min(r.timestamp for r in reviews).isoformat(),
            "Latest Review": max(r.timestamp for r in reviews).isoformat()
        }

        # Create overview section
        overview = ReportSection(
            title="Historical Analysis Overview",
            content=f"""# Code Review History Report
{f'## File: `{file_path}`' if file_path else '## All Files'}
{f'Review Type: {review_type.value}' if review_type else ''}

{self._format_metrics(metrics)}""",
            metrics=metrics
        )

        # Create trend analysis section
        trend_content = "## Quality Score Trend\n\n"
        if quality_scores:
            trend_content += "Quality scores over time:\n\n"
            for review in sorted(reviews, key=lambda r: r.timestamp):
                if review.review_response.score is not None:
                    trend_content += f"- {review.timestamp.isoformat()}: {review.review_response.score:.2f}\n"
        else:
            trend_content += "No quality scores available for trend analysis.\n"

        trend_section = ReportSection(
            title="Trend Analysis",
            content=trend_content
        )

        return ReviewReport(
            title="Historical Review Analysis",
            summary=f"Analysis of {review_counts} reviews",
            sections=[overview, trend_section],
            metadata={
                "file_path": file_path,
                "review_type": review_type.value if review_type else None,
                "metrics": metrics
            }
        )

    async def generate_trend_report(
        self,
        reviews: List[ReviewRecord],
        start_time: datetime,
        end_time: datetime,
        review_type: Optional[ReviewType] = None
    ) -> ReviewReport:
        """Generate a Markdown report analyzing review trends over time."""
        if not reviews:
            return ReviewReport(
                title="Review Trend Analysis",
                summary="No reviews available for trend analysis",
                sections=[]
            )

        # Calculate trend metrics
        reviews_by_date = {}
        for review in reviews:
            date = review.timestamp.date()
            if date not in reviews_by_date:
                reviews_by_date[date] = []
            reviews_by_date[date].append(review)

        daily_metrics = []
        for date, day_reviews in sorted(reviews_by_date.items()):
            scores = [
                r.review_response.score for r in day_reviews if r.review_response.score is not None]
            daily_metrics.append({
                "date": date.isoformat(),
                "review_count": len(day_reviews),
                "avg_score": statistics.mean(scores) if scores else None
            })

        # Create overview section
        overview = ReportSection(
            title="Trend Analysis Overview",
            content=f"""# Review Trend Analysis
## Time Period: {start_time.date().isoformat()} to {end_time.date().isoformat()}
{f'Review Type: {review_type.value}' if review_type else ''}

### Overall Statistics
- Total Reviews: {len(reviews)}
- Days with Reviews: {len(reviews_by_date)}
- Average Reviews per Day: {len(reviews) / len(reviews_by_date):.2f}""",
            metrics={
                "total_reviews": len(reviews),
                "days_with_reviews": len(reviews_by_date),
                "avg_reviews_per_day": len(reviews) / len(reviews_by_date)
            }
        )

        # Create daily breakdown section
        daily_content = "## Daily Breakdown\n\n"
        daily_content += "| Date | Reviews | Avg Score |\n|------|----------|------------|\n"
        for metric in daily_metrics:
            score = f"{metric['avg_score']:.2f}" if metric['avg_score'] is not None else "N/A"
            daily_content += f"| {metric['date']} | {metric['review_count']} | {score} |\n"

        daily_section = ReportSection(
            title="Daily Breakdown",
            content=daily_content
        )

        return ReviewReport(
            title="Review Trend Analysis",
            summary=f"Analysis of {len(reviews)} reviews over {len(reviews_by_date)} days",
            sections=[overview, daily_section],
            metadata={
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "review_type": review_type.value if review_type else None,
                "daily_metrics": daily_metrics
            }
        )
