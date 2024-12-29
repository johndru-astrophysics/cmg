"""Validates a schema against a set of rules"""

from abc import ABC
from dataclasses import dataclass
from typing import List, Sequence

from cmg.schema import Schema


@dataclass
class RuleError:
    """
    Represents a rule error

    Attributes:
        message: The error message
    """

    message: str


@dataclass
class BaseRule(ABC):
    """
    Base class for all rules

    Attributes:
        name: The name of the rule
        description: The description of the rule
    """

    name: str
    description: str

    def validate(self, schema: Schema) -> List[RuleError]:
        """
        Validates a schema against a rule

        Args:
            schema: The schema to validate

        Returns:
            A list of errors
        """

        raise NotImplementedError


class RuleSet:
    """
    Represents a set of rules

    Attributes:
        rules: The list of rules
    """

    def __init__(self, rules: Sequence[BaseRule]):
        self.rules = rules

    def validate(self, schema) -> List[RuleError]:
        """
        Validates a schema against a set of rules

        Args:
            schema: The schema to validate

        Returns:
            A list of errors
        """

        errors = []

        for rule in self.rules:
            errors += rule.validate(schema)

        return errors


class FieldsHaveValidTypeRules(BaseRule):
    """
    Rule that checks if all fields have a valid type

    Attributes:
        name: The name of the rule
        description: The description of the rule
    """

    def validate(self, schema) -> List[RuleError]:
        # Valid primitive types
        valid_types = ["str", "int", "bool", "double", "float"]

        # Valid class types
        valid_types.extend([klass.name for klass in schema.classes])

        errors = []
        for klass in schema.classes:
            for field in klass.fields:
                if field.type in valid_types:
                    continue
                errors.append(
                    RuleError(
                        f"Field {field.name} in klass {klass.name} has an invalid type {field.type}"
                    )
                )
        return errors


class FieldExampleMatchesTypeRule(BaseRule):
    """
    Rule that checks if the example matches the field type

    Attributes:
        name: The name of the rule
        description: The description of the rule
    """

    def validate(self, schema) -> List[RuleError]:
        errors = []
        for klass in schema.classes:
            for field in klass.fields:
                has_error = False
                if field.type == "str" and not isinstance(field.example, str):
                    has_error = True
                elif field.type == "int" and not isinstance(field.example, int):
                    has_error = True
                elif field.type == "bool" and not isinstance(field.example, bool):
                    has_error = True
                elif field.type == "double" and not isinstance(field.example, float):
                    has_error = True
                elif field.type == "float" and not isinstance(field.example, float):
                    has_error = True

                if has_error:
                    errors.append(
                        RuleError(
                            f"Field {field.name} in klass {klass.name} has an example {field.example} that does not match the type {field.type}"
                        )
                    )
        return errors


class FieldDefaultMatchesTypeRule(BaseRule):
    """
    Rule that checks if the default value matches the field type

    Attributes:
        name: The name of the rule
        description: The description of the rule
    """

    def validate(self, schema) -> List[RuleError]:
        errors = []
        for klass in schema.classes:
            for field in klass.fields:
                if field.default is None:
                    continue
                has_error = False
                if field.type == "str" and not isinstance(field.default, str):
                    has_error = True
                elif field.type == "int" and not isinstance(field.default, int):
                    has_error = True
                elif field.type == "bool" and not isinstance(field.default, bool):
                    has_error = True
                elif field.type == "double" and not isinstance(field.default, float):
                    has_error = True
                elif field.type == "float" and not isinstance(field.default, float):
                    has_error = True

                if has_error:
                    errors.append(
                        RuleError(
                            f"Field {field.name} in klass {klass.name} has a default value {field.default} that does not match the type {field.type}"
                        )
                    )
        return errors


class ParentFieldExistsRule(BaseRule):
    """
    Rule that checks if the parent field exists

    Attributes:
        name: The name of the rule
        description: The description of the rule
    """

    def validate(self, schema) -> List[RuleError]:
        errors = []
        for klass in schema.classes:
            for field in klass.fields:
                if field.parent:
                    parent_klass = next(
                        (k for k in schema.classes if k.name == field.type), None
                    )
                    if parent_klass is None:
                        continue

                    parent_field = next(
                        (f for f in parent_klass.fields if f.name == field.parent), None
                    )

                    if parent_field is None:
                        errors.append(
                            RuleError(
                                f"Field {field.name} in klass {klass.name} has a parent field {field.parent} that does not exist in klass {field.type}"
                            )
                        )

        return errors


class KlassNamesUniqueRule(BaseRule):
    """
    Rule that checks if all class names are unique

    Attributes:
        name: The name of the rule
        description: The description of the rule
    """

    def validate(self, schema) -> List[RuleError]:
        errors = []
        class_names = [klass.name for klass in schema.classes]
        visited_klass_names = set()
        for klass in schema.classes:
            if (
                klass.name not in visited_klass_names
                and class_names.count(klass.name) > 1
            ):
                errors.append(RuleError(f"Klass {klass.name} is not unique"))
            visited_klass_names.add(klass.name)
        return errors


class FieldNamesUniqueRule(BaseRule):
    """
    Rule that checks if all field names are unique

    Attributes:
        name: The name of the rule
        description: The description of the rule
    """

    def validate(self, schema) -> List[RuleError]:
        errors = []
        for klass in schema.classes:
            field_names = [field.name for field in klass.fields]
            visited_field_names = set()
            for field in klass.fields:
                if (
                    field.name not in visited_field_names
                    and field_names.count(field.name) > 1
                ):
                    errors.append(
                        RuleError(
                            f"Field {field.name} in klass {klass.name} is not unique"
                        )
                    )
                visited_field_names.add(field.name)
        return errors


class ChildHasParentRule(BaseRule):
    """
    Rule that checks if the child has a parent

    Attributes:
        name: The name of the rule
        description: The description of the rule
    """

    def validate(self, schema) -> List[RuleError]:
        errors = []
        for klass in schema.classes:
            for field in klass.fields:
                if field.is_child:
                    child_klass = next(
                        (k for k in schema.classes if k.name == field.type), None
                    )
                    if child_klass is None:
                        continue

                    parent_field = next(
                        (
                            f
                            for f in child_klass.fields
                            if f.parent == field.name and f.type == klass.name
                        ),
                        None,
                    )

                    if parent_field is None:
                        errors.append(
                            RuleError(
                                f"Field {field.name} in klass {klass.name} is a child field but does not have a parent field in klass {field.type}"
                            )
                        )
        return errors


class SchemaRuleSet(RuleSet):
    """
    Rule set for schema validation

    Attributes:
        rules: The list of rules
    """

    def __init__(self):
        rules = [
            FieldsHaveValidTypeRules(
                "FieldsHaveValidTypeRules", "Checks if all fields have a valid type"
            ),
            FieldExampleMatchesTypeRule(
                "FieldExampleMatchesTypeRule",
                "Checks if the example matches the field type",
            ),
            ParentFieldExistsRule(
                "ParentFieldExistsRule", "Checks if the parent field exists"
            ),
            FieldDefaultMatchesTypeRule(
                "FieldDefaultMatchesTypeRule",
                "Checks if the default value matches the field type",
            ),
            KlassNamesUniqueRule(
                "KlassNamesUniqueRule", "Checks if all klass names are unique"
            ),
            FieldNamesUniqueRule(
                "FieldNamesUniqueRule", "Checks if all field names are unique"
            ),
            ChildHasParentRule(
                "ChildHasParentRule", "Checks if the child has a parent"
            ),
        ]

        super().__init__(rules)
