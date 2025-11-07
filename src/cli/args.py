"""
Command-line interface (CLI) argument parsing.

Centralizes the definition of command-line arguments for the PDF conversion
scripts, ensuring consistency and reusability.
"""

import argparse


def create_parser() -> argparse.ArgumentParser:
    """
    Creates and configures the argument parser for the application.

    Returns:
        The configured argparse.ArgumentParser object.
    """
    parser = argparse.ArgumentParser(
        description="Convert PDF to 'pure image PDF' (rasterize each page).",
        formatter_class=argparse.RawTextHelpFormatter
    )

    return parser


def add_common_args(parser: argparse.ArgumentParser):
    """
    Adds common arguments to the parser, used by both single and batch modes.

    Args:
        parser: The argument parser to which the arguments will be added.
    """
    # Configuration for conversion settings
    group_conversion = parser.add_argument_group("Conversion Settings")
    group_conversion.add_argument(
        "--dpi",
        type=int,
        help="Rendering DPI. Higher DPI results in clearer images but larger file sizes."
    )
    group_conversion.add_argument(
        "--quality",
        type=int,
        help="JPEG compression quality (1-100) for page images."
    )

    # Configuration for sample mode
    group_sample = parser.add_argument_group("Sample Mode")
    group_sample.add_argument(
        "--sample",
        action="store_true",
        help="Enable sample mode. Converts only one page to preview the effect."
    )
    group_sample.add_argument(
        "--sample-page",
        type=int,
        nargs='?',
        const=0,  # Used when --sample-page is provided without a value
        default=None, # Default when the argument is not present at all
        help="Page number to sample. If not specified, a random page is chosen."
    )
    group_sample.add_argument(
        "--sample-dir",
        type=str,
        help="Directory for saving sample output files."
    )

    # General configuration
    group_general = parser.add_argument_group("General")
    group_general.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to a custom YAML configuration file."
    )


def add_batch_args(parser: argparse.ArgumentParser):
    """
    Adds arguments specific to batch processing mode.

    Args:
        parser: The argument parser to which the arguments will be added.
    """
    group_batch = parser.add_argument_group("Batch Processing")
    group_batch.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Process subfolders recursively."
    )
    group_batch.add_argument(
        "--pattern",
        type=str,
        help="File pattern to match (e.g., '*.pdf')."
    )
    group_batch.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip files that already exist in the output folder."
    )
