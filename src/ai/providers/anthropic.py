from typing import Dict, Optional, List
import json
import re
from anthropic import Anthropic

from .base import BaseProvider
from ..models.request import AIRequest
from ..models.response import AIResponse, ReviewComment
from ..exceptions import ProviderError, ReviewError


class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider for code review."""

    DEFAULT_MODEL = "claude-3-sonnet-20240229"
    DEFAULT_SYSTEM_PROMPT = """You are an expert code reviewer with deep knowledge of software engineering principles, design patterns, and security best practices. Your task is to provide comprehensive, actionable code reviews that help improve code quality and maintainability.

Your response MUST be in the following JSON format:

{
    "summary": "Brief overall summary of the code review, highlighting the most critical findings",
    "score": float between 0-1 representing overall code quality (0.0 = poor, 1.0 = excellent),
    "comments": [
        {
            "line_number": integer or null if general comment,
            "content": "Detailed explanation of the issue or praise",
            "severity": one of ["error", "warning", "suggestion", "praise"],
            "category": one of ["security", "performance", "style", "logic", "documentation", "best_practices"],
            "suggested_fix": "Code snippet or description of fix" or null
        }
    ]
}

Review Guidelines:

1. Code Quality and Best Practices:
   - Clean Code principles (SOLID, DRY, KISS)
   - Design patterns and their appropriate usage
   - Code organization and structure
   - Naming conventions and readability
   - Error handling and edge cases

2. Security Analysis:
   - Common vulnerabilities (OWASP Top 10 if applicable)
   - Input validation and sanitization
   - Authentication and authorization issues
   - Secure coding practices
   - Sensitive data handling

3. Performance Considerations:
   - Algorithmic efficiency and complexity
   - Resource usage (memory, CPU, network)
   - Caching opportunities
   - Database query optimization (if applicable)
   - Concurrency and threading issues

4. Maintainability:
   - Code documentation and comments
   - Test coverage and testability
   - Modularity and coupling
   - Code duplication
   - Future scalability concerns

5. Language-Specific Best Practices:
   - Utilize language idioms appropriately
   - Follow community style guides
   - Use modern language features when beneficial
   - Proper dependency management

Severity Levels:
- error: Critical issues that must be fixed (bugs, security vulnerabilities)
- warning: Important issues that should be addressed (performance, maintainability)
- suggestion: Minor improvements that would enhance the code
- praise: Exemplary code that follows best practices

Categories:
- security: Security vulnerabilities and risks
- performance: Performance implications and optimizations
- style: Code style, formatting, and naming
- logic: Business logic and algorithmic issues
- documentation: Comments, docstrings, and documentation
- best_practices: General coding best practices and patterns

Be thorough but concise. Each comment should:
1. Clearly identify the issue or praise
2. Explain why it matters
3. Provide a specific, actionable solution
4. Include code examples in suggested_fix when applicable

For line-specific comments, always include the line_number. For general patterns or issues, use null for line_number."""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = Anthropic(api_key=api_key)
        self.model = kwargs.get('model', self.DEFAULT_MODEL)
        self.system_prompt = kwargs.get(
            'system_prompt', self.DEFAULT_SYSTEM_PROMPT)

    async def generate_review(self, request: AIRequest) -> AIResponse:
        """Generate a code review using Claude."""
        try:
            if not request.validate():
                raise ProviderError("Invalid request parameters")

            prompt = self._build_review_prompt(request)

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=request.max_tokens or 4096,
                temperature=request.temperature,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )

            return self._parse_response(response.content)

        except Exception as e:
            raise ProviderError(f"Failed to generate review: {str(e)}")

    def _build_review_prompt(self, request: AIRequest) -> str:
        """Build the review prompt from the request."""
        context = request.code_context

        # Get specialized prompt based on review type
        specialized_prompt = self._get_specialized_prompt(request)

        prompt = f"""Please review the following code from file: {context.file_path}
        
Language: {context.language or 'Unknown'}
Review Type: {request.review_type.value}
{f'Author: {context.author}' if context.author else ''}
{f'Commit: {context.commit_hash}' if context.commit_hash else ''}

{specialized_prompt}

Code to review:
```
{context.content}
```
"""
        if context.diff:
            prompt += f"\nChanges made:\n```\n{context.diff}\n```"

        # Add review settings if present
        if request.settings:
            prompt += "\nReview Settings:"
            if request.settings.max_comments:
                prompt += f"\n- Maximum comments: {request.settings.max_comments}"
            if request.settings.min_severity:
                prompt += f"\n- Minimum severity: {request.settings.min_severity}"
            if request.settings.focus_areas:
                prompt += f"\n- Focus areas: {', '.join(request.settings.focus_areas)}"
            if request.settings.ignore_patterns:
                prompt += f"\n- Ignore patterns: {', '.join(request.settings.ignore_patterns)}"

        return prompt

    def _get_specialized_prompt(self, request: AIRequest) -> str:
        """Get specialized prompt based on review type."""
        prompts = {
            "security": """Focus on security vulnerabilities and best practices:
- Identify potential security risks and vulnerabilities
- Check for proper input validation and sanitization
- Review authentication and authorization mechanisms
- Assess data protection and privacy concerns
- Evaluate secure coding practices
Pay special attention to:
- OWASP Top 10 vulnerabilities
- Sensitive data handling
- Security configurations
- Cryptographic implementations""",

            "performance": """Focus on performance optimization and efficiency:
- Analyze algorithmic complexity and efficiency
- Identify performance bottlenecks
- Review resource usage patterns
- Check for optimization opportunities
Pay special attention to:
- Time and space complexity
- Resource utilization
- Caching strategies
- Query optimization
- Concurrency issues""",

            "maintainability": """Focus on code maintainability and quality:
- Evaluate code organization and structure
- Check for proper design patterns usage
- Review code modularity and reusability
- Assess technical debt
Pay special attention to:
- SOLID principles
- Code coupling and cohesion
- Documentation quality
- Test coverage
- Code duplication""",

            "style": """Focus on code style and formatting:
- Check adherence to language style guides
- Review naming conventions
- Assess code formatting
- Evaluate code readability
Pay special attention to:
- Consistent formatting
- Clear and descriptive names
- Code organization
- Comment quality
- Language idioms""",

            "documentation": """Focus on documentation quality:
- Review code comments and docstrings
- Check API documentation
- Assess usage examples
- Evaluate documentation completeness
Pay special attention to:
- Function/method documentation
- Class/module documentation
- Code examples
- Architecture documentation
- Implementation notes""",

            "quick": """Perform a quick review focusing on critical issues:
- Identify major bugs or issues
- Spot significant security vulnerabilities
- Note obvious performance problems
- Flag maintainability concerns
Focus only on high-impact issues that require immediate attention."""
        }

        # Get specialized prompt or use default for 'full' review
        specialized_prompt = prompts.get(request.review_type.value, "")

        # Add security-focused instructions if code is security-sensitive
        if request.is_security_sensitive and request.review_type.value != "security":
            specialized_prompt += "\n\nNote: This code contains security-sensitive patterns. Please include security considerations in the review."

        # Add performance-focused instructions if code is performance-critical
        if request.is_performance_critical and request.review_type.value != "performance":
            specialized_prompt += "\n\nNote: This code contains performance-critical patterns. Please include performance considerations in the review."

        return specialized_prompt

    def _parse_response(self, content: str) -> AIResponse:
        """Parse Claude's response into structured format."""
        try:
            # Extract JSON from the response
            json_match = re.search(r'\{[\s\S]*\}', content)
            if not json_match:
                raise ReviewError("Could not find JSON in Claude's response")

            json_str = json_match.group(0)
            review_data = json.loads(json_str)

            # Validate required fields
            required_fields = ['summary', 'comments']
            if not all(field in review_data for field in required_fields):
                raise ReviewError("Missing required fields in review response")

            # Parse comments
            comments = []
            for comment_data in review_data['comments']:
                try:
                    # Validate severity and category
                    severity = comment_data['severity'].lower()
                    if severity not in ['error', 'warning', 'suggestion', 'praise']:
                        severity = 'suggestion'  # Default to suggestion if invalid

                    category = comment_data['category'].lower()
                    valid_categories = [
                        'security', 'performance', 'style', 'logic', 'documentation', 'best_practices']
                    if category not in valid_categories:
                        category = 'best_practices'  # Default if invalid

                    comments.append(ReviewComment(
                        line_number=comment_data.get('line_number'),
                        content=comment_data['content'],
                        severity=severity,
                        category=category,
                        suggested_fix=comment_data.get('suggested_fix')
                    ))
                except KeyError as e:
                    # Skip malformed comments but continue processing
                    continue

            # Create response object
            return AIResponse(
                comments=comments,
                summary=review_data['summary'],
                score=review_data.get('score'),
                metadata={
                    "model": self.model,
                    "total_comments": len(comments)
                }
            )

        except json.JSONDecodeError as e:
            raise ReviewError(f"Failed to parse JSON response: {str(e)}")
        except Exception as e:
            raise ReviewError(f"Failed to parse review response: {str(e)}")

    async def validate_configuration(self) -> bool:
        """Validate the provider configuration."""
        try:
            # Test API key with a minimal request
            await self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False

    def get_token_limit(self) -> int:
        """Get the maximum token limit for the model."""
        # Claude 3 Sonnet token limit
        return 200000

    def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in the given text."""
        # Rough estimation: 1 token ≈ 4 characters for English text
        return len(text) // 4

    @property
    def provider_name(self) -> str:
        return "anthropic"
