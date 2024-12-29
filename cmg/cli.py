import click
import logging

from cmg import generator

"""
CLI for the cmg package.

Example usage:

cmg --schema <path to schema file> --output <path to output directory>
"""


@click.command()
@click.option("--schema", required=True, help="Path to schema file")
@click.option("--output", required=True, help="Path to output directory")
def cli(schema, output):
    """
    Generate code from a schema file.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    logger: logging.Logger = logging.getLogger("cmg")
    logger.info(f"Generating code from schema {schema} to output directory {output}")
    exit_code = generator.generate(generator.schema_loader(schema), output, logger)
    if exit_code != 0:
        logger.error("Code generation failed.")
    else:
        logger.info("Code generation complete.")

    exit(exit_code)


if __name__ == "__main__":
    cli()
