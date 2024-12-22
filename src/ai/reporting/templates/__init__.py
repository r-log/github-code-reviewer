"""Report templates for different types of code reviews."""

from .base import ReportTemplate, TemplateRegistry, TemplateVariable
from .standard import ExecutiveSummaryTemplate, SecurityAuditTemplate, PerformanceReportTemplate

# Initialize global template registry
registry = TemplateRegistry()

# Register standard templates
registry.register(ExecutiveSummaryTemplate())
registry.register(SecurityAuditTemplate())
registry.register(PerformanceReportTemplate())

__all__ = [
    'ReportTemplate',
    'TemplateRegistry',
    'TemplateVariable',
    'ExecutiveSummaryTemplate',
    'SecurityAuditTemplate',
    'PerformanceReportTemplate',
    'registry'
]
