from typing import Dict, Any, List
from datetime import datetime

from .base import ReportTemplate, TemplateVariable, ReportSection
from ...models.response import AIResponse
from ...models.request import ReviewType


class ExecutiveSummaryTemplate(ReportTemplate):
    """A concise executive summary template."""

    @property
    def template_id(self) -> str:
        return "executive-summary"

    @property
    def name(self) -> str:
        return "Executive Summary"

    @property
    def description(self) -> str:
        return "A concise summary focusing on key findings and recommendations"

    @property
    def variables(self) -> Dict[str, TemplateVariable]:
        return {
            "review": TemplateVariable(
                name="review",
                description="The review response object",
                required=True
            ),
            "file_path": TemplateVariable(
                name="file_path",
                description="Path to the reviewed file",
                required=True
            ),
            "review_type": TemplateVariable(
                name="review_type",
                description="Type of review performed",
                required=True
            )
        }

    def render(self, context: Dict[str, Any]) -> List[ReportSection]:
        review: AIResponse = context["review"]
        file_path: str = context["file_path"]
        review_type: ReviewType = context["review_type"]

        # Calculate metrics
        critical_issues = len(review.get_comments_by_severity("error"))
        warnings = len(review.get_comments_by_severity("warning"))
        suggestions = len(review.get_comments_by_severity("suggestion"))

        # Create summary section
        summary = ReportSection(
            title="Executive Summary",
            content=f"""# Executive Summary

## Overview
- **File:** `{file_path}`
- **Review Type:** {review_type.value}
- **Quality Score:** {review.score if review.score is not None else 'N/A'}
- **Review Date:** {datetime.utcnow().strftime('%Y-%m-%d')}

## Key Findings
- Critical Issues: {critical_issues}
- Warnings: {warnings}
- Suggestions: {suggestions}

## Summary
{review.summary}""",
            metrics={
                "critical_issues": critical_issues,
                "warnings": warnings,
                "suggestions": suggestions,
                "quality_score": review.score
            }
        )

        # Create critical issues section if any
        sections = [summary]
        if critical_issues > 0:
            critical_content = "## Critical Issues\n\n"
            for comment in review.get_comments_by_severity("error"):
                critical_content += f"- **{comment.category}** (Line {comment.line_number or 'N/A'}):\n  {comment.content}\n\n"

            sections.append(ReportSection(
                title="Critical Issues",
                content=critical_content,
                severity="error"
            ))

        return sections


class SecurityAuditTemplate(ReportTemplate):
    """A detailed security audit template."""

    @property
    def template_id(self) -> str:
        return "security-audit"

    @property
    def name(self) -> str:
        return "Security Audit Report"

    @property
    def description(self) -> str:
        return "A comprehensive security audit report with detailed findings"

    @property
    def variables(self) -> Dict[str, TemplateVariable]:
        return {
            "review": TemplateVariable(
                name="review",
                description="The review response object",
                required=True
            ),
            "file_path": TemplateVariable(
                name="file_path",
                description="Path to the reviewed file",
                required=True
            ),
            "include_code": TemplateVariable(
                name="include_code",
                description="Whether to include code snippets",
                required=False,
                default=False
            )
        }

    def render(self, context: Dict[str, Any]) -> List[ReportSection]:
        review: AIResponse = context["review"]
        file_path: str = context["file_path"]
        include_code: bool = context.get("include_code", False)

        # Overview section
        overview = ReportSection(
            title="Security Audit Overview",
            content=f"""# Security Audit Report

## File Information
- **File:** `{file_path}`
- **Audit Date:** {datetime.utcnow().strftime('%Y-%m-%d')}
- **Security Score:** {review.score if review.score is not None else 'N/A'}

## Summary
{review.summary}""",
            metrics={
                "security_score": review.score
            }
        )

        # Categorize security issues
        sections = [overview]
        security_comments = [
            c for c in review.comments if c.category == "security"]

        if security_comments:
            by_severity = {
                "error": [],
                "warning": [],
                "suggestion": []
            }
            for comment in security_comments:
                if comment.severity in by_severity:
                    by_severity[comment.severity].append(comment)

            # Create sections for each severity
            for severity, comments in by_severity.items():
                if not comments:
                    continue

                content = f"## {severity.title()} Level Security Issues\n\n"
                for comment in comments:
                    content += f"### Issue at Line {comment.line_number or 'N/A'}\n"
                    content += f"{comment.content}\n\n"
                    if comment.suggested_fix and include_code:
                        content += f"**Suggested Fix:**\n```\n{comment.suggested_fix}\n```\n\n"

                sections.append(ReportSection(
                    title=f"{severity.title()} Security Issues",
                    content=content,
                    severity=severity,
                    metrics={"count": len(comments)}
                ))

        return sections


class PerformanceReportTemplate(ReportTemplate):
    """A performance analysis report template."""

    @property
    def template_id(self) -> str:
        return "performance-report"

    @property
    def name(self) -> str:
        return "Performance Analysis Report"

    @property
    def description(self) -> str:
        return "A detailed performance analysis with optimization recommendations"

    @property
    def variables(self) -> Dict[str, TemplateVariable]:
        return {
            "review": TemplateVariable(
                name="review",
                description="The review response object",
                required=True
            ),
            "file_path": TemplateVariable(
                name="file_path",
                description="Path to the reviewed file",
                required=True
            ),
            "include_metrics": TemplateVariable(
                name="include_metrics",
                description="Whether to include detailed metrics",
                required=False,
                default=True
            )
        }

    def render(self, context: Dict[str, Any]) -> List[ReportSection]:
        review: AIResponse = context["review"]
        file_path: str = context["file_path"]
        include_metrics: bool = context.get("include_metrics", True)

        # Overview section
        overview = ReportSection(
            title="Performance Analysis Overview",
            content=f"""# Performance Analysis Report

## File Information
- **File:** `{file_path}`
- **Analysis Date:** {datetime.utcnow().strftime('%Y-%m-%d')}
- **Performance Score:** {review.score if review.score is not None else 'N/A'}

## Summary
{review.summary}""",
            metrics={
                "performance_score": review.score
            }
        )

        sections = [overview]

        # Performance issues section
        perf_comments = [
            c for c in review.comments if c.category == "performance"]
        if perf_comments:
            content = "## Performance Issues\n\n"
            for comment in perf_comments:
                content += f"### {comment.severity.title()} Priority Issue"
                if comment.line_number:
                    content += f" (Line {comment.line_number})"
                content += f"\n{comment.content}\n\n"
                if comment.suggested_fix:
                    content += f"**Optimization Suggestion:**\n```\n{comment.suggested_fix}\n```\n\n"

            sections.append(ReportSection(
                title="Performance Issues",
                content=content,
                metrics={"total_issues": len(
                    perf_comments)} if include_metrics else None
            ))

        return sections
