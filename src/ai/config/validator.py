import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import jsonschema


class ConfigValidator:
    """Configuration validator using JSON Schema."""

    def __init__(self, schema_path: Optional[str] = None):
        if schema_path is None:
            schema_path = str(
                Path(__file__).parent.parent.parent.parent / "config" / "schema.json")

        with open(schema_path) as f:
            self.schema = json.load(f)

    def validate(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate configuration against schema.
        Returns a list of validation errors, empty if valid.
        """
        try:
            jsonschema.validate(instance=config, schema=self.schema)
            return []
        except jsonschema.exceptions.ValidationError as e:
            return [self._format_error(e)]
        except jsonschema.exceptions.SchemaError as e:
            return [f"Schema error: {str(e)}"]

    def validate_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration and fill in defaults from schema."""
        errors = self.validate(config)
        if errors:
            raise ValueError(
                f"Configuration validation failed: {'; '.join(errors)}")

        return self._apply_defaults(config, self.schema)

    def _format_error(self, error: jsonschema.exceptions.ValidationError) -> str:
        """Format a validation error message."""
        path = " -> ".join(str(p) for p in error.path)
        return f"At {path}: {error.message}"

    def _apply_defaults(self, config: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively apply defaults from schema to config."""
        if not isinstance(config, dict) or not isinstance(schema, dict):
            return config

        result = config.copy()
        properties = schema.get("properties", {})

        for key, value_schema in properties.items():
            if key not in result and "default" in value_schema:
                result[key] = value_schema["default"]
            elif key in result and "properties" in value_schema:
                result[key] = self._apply_defaults(result[key], value_schema)

        return result

    def generate_example_config(self) -> Dict[str, Any]:
        """Generate an example configuration with all defaults."""
        return self._generate_from_schema(self.schema)

    def _generate_from_schema(self, schema: Dict[str, Any]) -> Any:
        """Recursively generate configuration from schema."""
        if "default" in schema:
            return schema["default"]

        if schema.get("type") == "object" and "properties" in schema:
            return {
                key: self._generate_from_schema(prop_schema)
                for key, prop_schema in schema["properties"].items()
            }

        if schema.get("type") == "array":
            return []

        type_defaults = {
            "string": "",
            "integer": 0,
            "number": 0.0,
            "boolean": False,
            "null": None
        }

        return type_defaults.get(schema.get("type", "null"), None)
