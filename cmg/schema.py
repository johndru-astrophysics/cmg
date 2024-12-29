"""A schema used to define the structure of the data in a model."""

from dataclasses import dataclass, field
import os
from typing import Any, List, Optional


def to_snake_case(name: str) -> str:
    """
    Convert a camelCase or PascalCase string to snake_case.

    Args:
        name (str): The name to convert.

    Returns:
        str: The name in snake_case.
    """
    name = "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip("_")
    return name


def to_camel_case(name: str | None, upper_first=False) -> str | None:
    """
    Convert a snake_case string to camelCase.

    Args:
        name (str): The name to convert.
        upper_first (bool): Whether to capitalize the first letter.

    Returns:
        str: The name in camelCase.
    """

    if name is None:
        return None
    name = name.replace("_", " ").title().replace(" ", "")
    if upper_first:
        return name
    return name[0].lower() + name[1:]


@dataclass
class Schema:
    """
    A schema used to define the structure of the data in a model.

    Attributes:
        name (str): The name of the schema.

        description (str): The description of the schema.

        namespace (str): The namespace of the schema.

        classes (List[Klass]): The classes in the schema.
    """

    name: str
    description: str
    namespace: str
    classes: List["Klass"] = field(default_factory=list)
    _output_dir: str = field(default=".", repr=False, init=False)

    def set_output_dir(self, output_dir: str) -> None:
        """
        Set the output directory for the schema.

        Args:
            output_dir (str): The output directory.
        """
        self._output_dir = os.path.abspath(output_dir)

    def link(self) -> None:
        """
        Link the schema to its classes and fields.
        """
        for klass in self.classes:
            klass._schema = self
            klass.link()

    def get_klass(self, name: str) -> "Klass":
        """
        Get a klass by name.

        Args:
            name (str): The name of the klass.

        Returns:
            Klass: The klass.

        Raises:
            ValueError: If the klass is not found.
        """
        for klass in self.classes:
            if klass.name == name:
                return klass
        raise ValueError(f"Klass not found: {name}")

    def get_field(self, klass_name: str, field_name: str) -> "Field":
        """
        Get a field by klass and field name.

        Args:
            klass_name (str): The name of the klass.
            field_name (str): The name of the field.

        Returns:
            Field: The field.

        Raises:
            ValueError: If the field is not found.
        """
        klass = self.get_klass(klass_name)
        for field in klass.fields:
            if field.name == field_name:
                return field
        raise ValueError(f"Field not found: {field_name} in klass: {klass_name}")

    def get_cmakelists_src(self) -> str:
        """
        Get the source files for the CMakeLists.txt file.

        Returns:
            str: The source files.
        """
        return " ".join([f'"{klass.to_snake_case()}.cpp"' for klass in self.classes])

    def get_lcov_src(self) -> str:
        """
        Get the source files for the lcov command.

        Returns:
            str: The source files.
        """
        sources = [
            "/".join(
                [
                    self._output_dir.replace(os.path.sep, "/").replace("c:", "", 1),
                    f"{klass.to_snake_case()}.cpp",
                ]
            )
            for klass in self.classes
        ]
        return " ".join(sources)

    def get_test_includes(self) -> List[str]:
        """
        Get the include statements for the test file.

        Returns:
            List[str]: A list of include statements for each class in the test file.
        """
        return [f'#include "{klass.to_snake_case()}.hpp"' for klass in self.classes]


@dataclass
class Klass:
    """
    A class used to define the structure of the data in a model.

    Attributes:
        name (str): The name of the class.

        description (str): The description of the class.

        fields (List[Field]): The fields in the class.

    """

    name: str
    description: str
    fields: List["Field"] = field(default_factory=list)
    _schema: Optional[Schema] = field(default=None, repr=False, init=False)

    def get_include_define(self) -> str:
        """
        Get the include define for the class.

        Returns:
            str: The include define.
        """
        return f"_{self.name.upper()}_HPP_"

    def get_forward_declarations(self) -> List[str]:
        """
        Get the forward declarations for the class.

        Returns:
            List[str]: The forward declarations.
        """
        forward_declarations = set()
        for field in self.fields:
            if field.is_reference():
                forward_declarations.add(field.type)
        return sorted(forward_declarations)

    def get_forward_includes(self) -> List[str]:
        """
        Get the forward includes for the class.

        Returns:
            List[str]: The forward includes.
        """
        return [to_snake_case(dec) for dec in self.get_forward_declarations()]

    def to_snake_case(self) -> str:
        """
        Convert the class name to snake_case.

        Returns:
            str: The class name in snake_case.
        """
        return to_snake_case(self.name)

    def init_fields(self, parents=True) -> List["Field"]:
        """
        Initialize the fields for the class.

        Args:
            parents (bool): Whether to include parent fields.

        Returns:
            List[Field]: The initialized fields.
        """
        init_fields = []
        for field in self.fields:
            if field.has_parent() and not parents:
                continue
            if not field.has_default() and not field.is_child and not field.is_optional:
                init_fields.append(field)
        return init_fields

    def get_create_arguments(self) -> str:
        """
        Get the create arguments for the class.

        Returns:
            str: The create arguments.
        """
        arguments = []
        for field in self.init_fields():
            arguments.append(f"{field.get_cpp_type()} {field.to_camel_case()}")
        return ", ".join(arguments)

    def get_example_arguments(self) -> str:
        """
        Get the example arguments for the class.

        Returns:
            str: The example arguments.
        """
        arguments = []
        for field in self.init_fields():
            arguments.append(field.get_example())
        return ", ".join(arguments)

    def get_example_update_arguments(self) -> str:
        """
        Get the example update arguments for the class.

        Returns:
            str: The example update arguments.
        """
        arguments = []
        for field in self.get_updatable_fields():
            if field.get_example() != "nullptr" and not field.has_parent():
                tuple_arg = f'{{"{field.to_camel_case()}", {field.get_example()}}}'
                arguments.append(tuple_arg)
        argument_str = ", ".join(arguments)

        return f"{{ {argument_str} }}"

    def get_ordered_fields(self):
        """
        Get the ordered fields for the class.

        Returns:
            List[Field]: The ordered fields.
        """
        # Returns a list of fields with the parent fields first, then other ordered alphabetically by name
        parent_fields = []
        other_fields = []
        for field in self.fields:
            if field.has_parent():
                parent_fields.append(field)
            else:
                other_fields.append(field)
        return sorted(parent_fields, key=lambda x: x.name) + sorted(
            other_fields, key=lambda x: x.name
        )

    def get_updatable_fields(self):
        """
        Get the updatable fields for the class.

        Returns:
            List[Field]: The updatable fields.
        """
        return [field for field in self.get_ordered_fields() if not field.is_list]

    def link(self) -> None:
        """
        Link the class to its fields and schema.
        """
        if not self._schema:
            raise ValueError("Schema is not linked")
        for field in self.fields:
            field._klass = self
            if field.has_parent():
                field._parent_klass = self._schema.get_klass(field.type)
                field._parent_field = self._schema.get_field(field.type, field.parent)  # type: ignore
            elif field.is_child:
                # Look for opposite field in child klass that has a matching parent
                child_klass = self._schema.get_klass(field.type)
                for child_field in child_klass.fields:
                    if child_field.has_parent() and child_field.type == self.name:
                        field._child_klass = child_klass
                        field._child_field = child_field
                        break

    def get_var_name(self) -> str:
        """
        Get the variable name for the class.

        Returns:
            str: The variable name.
        """
        # Return name with first letter lowercase
        return self.name[0].lower() + self.name[1:]

    def has_parent(self) -> bool:
        """
        Check if the class has a parent.

        Returns:
            bool: True if the class has a parent, False otherwise.
        """
        for field in self.fields:
            if field.has_parent():
                return True
        return False

    def get_create_ptr_type(self) -> str:
        """
        Get the create pointer type for the class.

        Returns:
            str: The create pointer type.
        """
        if self.has_parent():
            return f"std::weak_ptr<{self.name}>"
        else:
            return f"std::shared_ptr<{self.name}>"

    def get_parent_fields(self) -> List["Field"]:
        """
        Get the parent fields for the class.

        Returns:
            List[Field]: The parent fields.
        """
        fields = []
        for field in self.fields:
            if field.has_parent():
                if field._parent_klass is not None:
                    fields.extend(field._parent_klass.get_parent_fields())
                fields.append(field)
        return fields

    def get_parent_field(self) -> "Field":
        """
        Get the parent field for the class.

        Returns:
            Field: The parent field.

        Raises:
            ValueError: If no parent field is found.
        """
        for field in self.fields:
            if field.has_parent():
                return field
        raise ValueError("No parent field found")


@dataclass
class Field:
    """
    A field used to define the structure of the data in a model.

    Attributes:
        name (str): The name of the field.

        description (str): The description of the field.

        type (str): The type of the field.

        example (Any): The example value of the field.

        default (Optional[Any]): The default value of the field.

        parent (Optional[str]): The parent of the field.

        is_child (bool): Whether the field is a child.

        is_list (bool): Whether the field is a list.

        is_optional (bool): Whether the field is optional.

    """

    name: str
    description: str
    type: str
    example: Optional[Any] = None
    default: Optional[Any] = None
    parent: Optional[str] = None
    is_child: bool = False
    is_list: bool = False
    is_optional: bool = False
    _parent_klass: Optional[Klass] = field(default=None, repr=False, init=False)
    _parent_field: Optional["Field"] = field(default=None, repr=False, init=False)
    _child_klass: Optional[Klass] = field(default=None, repr=False, init=False)
    _child_field: Optional["Field"] = field(default=None, repr=False, init=False)
    _klass: Optional[Klass] = field(default=None, repr=False, init=False)

    def has_parent(self) -> bool:
        """
        Check if the field has a parent.

        Returns:
            bool: True if the field has a parent, False otherwise.
        """
        return self.parent is not None

    def has_default(self) -> bool:
        """
        Check if the field has a default value.

        Returns:
            bool: True if the field has a default value, False otherwise.
        """
        return self.default is not None

    def to_camel_case(self, upper_first=False) -> str | None:
        """
        Convert the field name to camelCase.

        Args:
            upper_first (bool): Whether to capitalize the first letter.

        Returns:
            str: The field name in camelCase.
        """
        return to_camel_case(self.name, upper_first)

    def get_cpp_type(self, nolist=False, cast=False) -> str:
        """
        Get the C++ type for the field.

        Args:
            nolist (bool): Whether to exclude list types.
            cast (bool): Whether to cast the type.

        Returns:
            str: The C++ type.
        """
        # Handle parent fields
        if self.has_parent():
            if cast:
                return f"std::shared_ptr<{self.type}>"
            else:
                return f"std::weak_ptr<{self.type}>"

        # Handle child fields
        if self.is_child:
            if self.is_list and not nolist:
                return f"std::vector<std::shared_ptr<{self.type}>>"
            else:
                return f"std::shared_ptr<{self.type}>"

        # Handle reference fields
        if self.is_reference():
            if self.is_list and not nolist:
                return f"std::vector<std::weak_ptr<{self.type}>>"
            else:
                return f"std::weak_ptr<{self.type}>"

        # Handle other fields
        if self.type == "str":
            type = "std::string"
        elif self.type == "float":
            type = "float"
        elif self.type == "int":
            type = "int"
        elif self.type == "bool":
            type = "bool"
        else:
            type = self.type

        # Handle optional fields
        if self.is_optional:
            type = f"std::optional<{type}>"

        return type

    def is_reference(self) -> bool:
        """
        Check if the field is a reference.

        Returns:
            bool: True if the field is a reference, False otherwise.

        Raises:
            ValueError: If the class or schema is not linked.
        """
        if self._klass is None:
            raise ValueError("Klass is not linked")

        if self._klass._schema is None:
            raise ValueError("Schema is not linked")

        return self.type in [klass.name for klass in self._klass._schema.classes]

    def get_example(self) -> Any:
        """
        Get the example value for the field.

        Returns:
            Any: The example value.
        """
        example = self.example
        if self._parent_field is not None:
            example = self.to_camel_case()
        elif isinstance(example, str):
            example = f'std::string("{example}")'
        elif isinstance(example, list):
            example = "{}"
        elif example is None:
            example = "nullptr"
        elif isinstance(example, bool):
            example = str(example).lower()
        elif isinstance(example, float):
            example = f"{example}f"
        return example
