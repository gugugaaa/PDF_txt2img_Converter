"""
Convert a single PDF file to an image-based PDF.
"""
import argparse
import sys
from pathlib import Path

# Adjust path to import from src
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.cli.args import create_parser, add_common_args
from src.utils.config import get_final_config
from src.core.converter import PDFConverter
from src.utils.ui import print_result


def main():
    """
    Main function to handle single PDF conversion.
    """
    parser = create_parser()
    parser.epilog = """
Examples:
  # Convert a PDF with default settings from config.yaml
  python src/convert_single.py input.pdf output.pdf

  # Convert with custom settings, overriding config.yaml
  python src/convert_single.py input.pdf output.pdf --dpi 150 --quality 85

  # Sample a random page to preview the effect
  python src/convert_single.py input.pdf --sample

  # Sample a specific page (e.g., page 5)
  python src/convert_single.py input.pdf --sample --sample-page 5
    """

    # Add common arguments
    add_common_args(parser)

    # Add arguments specific to single file conversion
    parser.add_argument("input_pdf", type=str, help="Path to the source PDF file")
    parser.add_argument(
        "output_pdf",
        type=str,
        nargs='?',
        default=None,
        help="Path for the output PDF (required unless in --sample mode)"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.sample and args.output_pdf is None:
        parser.error("The 'output_pdf' argument is required when not in --sample mode.")

    # Get the final configuration
    config = get_final_config(args)

    # Initialize the converter
    converter = PDFConverter(config)

    # Execute the appropriate action
    if args.sample:
        result = converter.sample_convert(args.input_pdf, args.sample_page)
    else:
        result = converter.convert(args.input_pdf, args.output_pdf)

    # Print the result using the dedicated UI function
    print_result(result)

    # Exit with a status code
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
