from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from ...models.response import AIResponse
from ...models.request import ReviewType
from ..base import ReportSection, ReviewReport


@dataclass
class TemplateVariable:
    """Definition of a template variable."""
    name: str
    description: str
    required: bool = True
    default: Any = None


class ReportTemplate(ABC):
    """Base class for report templates."""

    @property
    @abstractmethod
    def template_id(self) -> str:
        """Unique identifier for the template."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the template."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this template produces."""
        pass

    @property
    @abstractmethod
    def variables(self) -> Dict[str, TemplateVariable]:
        """Variables required by this template."""
        pass

    @abstractmethod
    def render(self, context: Dict[str, Any]) -> List[ReportSection]:
        """Render the template with the given context."""
        pass

    def validate_context(self, context: Dict[str, Any]) -> bool:
        """Validate that all required variables are present."""
        for var_name, var_def in self.variables.items():
            if var_def.required and var_name not in context:
                return False
        return True


class TemplateRegistry:
    """Registry of available report templates."""

    def __init__(self):
        self._templates: Dict[str, ReportTemplate] = {}

    def register(self, template: ReportTemplate):
        """Register a new template."""
        self._templates[template.template_id] = template

    def get_template(self, template_id: str) -> Optional[ReportTemplate]:
        """Get a template by ID."""
        return self._templates.get(template_id)

    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates."""
        return [
            {
                "id": t.template_id,
                "name": t.name,
                "description": t.description
            }
            for t in self._templates.values()
        ]

    def get_template_info(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a template."""
        template = self.get_template(template_id)
        if not template:
            return None

        return {
            "id": template.template_id,
            "name": template.name,
            "description": template.description,
            "variables": {
                name: {
                    "description": var.description,
                    "required": var.required,
                    "default": var.default
                }
                for name, var in template.variables.items()
            }
        }
