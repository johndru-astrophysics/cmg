C++ Model Generation (CMG)
==========================

This package provides a command-line utility `cmg` and Python dataclasses to describe a schema, then use that schema to generate a model in C++.

You can use this for applications that require complex modeling and high performance.

The resulting code uses C++11 smart pointers for easier memory management.

## Schema Structure

The schema consists of a set of classes (`Klass`) which contain fields (`Field`).

A tree structure can be created using parent-child relationships (solid lines).
Then references can be created between classes in the DAG hierarchy (dotted lines).

![schema](assets/cmg.drawio.png)

## Examples

Please see the example schemas in the `examples` directory.

## API Documentation

[Full API documentation is available here](https://johndru-astrophysics.github.io/cmg).



