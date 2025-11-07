"""
Batch convert PDF files in a folder to image-based PDFs.
"""
import sys
from pathlib import Path

# Adjust path to import from src
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.cli.args import create_parser, add_common_args, add_batch_args
from src.utils.config import get_final_config
from src.core.converter import PDFConverter, ConversionResult
from src.utils.ui import print_batch_summary
from typing import List


def find_pdf_files(input_folder: str, recursive: bool, pattern: str) -> List[Path]:
    """Finds all PDF files in the given folder that match the pattern."""
    path = Path(input_folder).resolve()
    if not path.is_dir():
        print(f"❌ Error: Input folder not found: {input_folder}")
        return []

    if recursive:
        return sorted(list(path.rglob(pattern)))
    else:
        return sorted(list(path.glob(pattern)))


def main():
    """
    Main function to handle batch PDF conversion.
    """
    parser = create_parser()
    parser.epilog = """
Examples:
  # Convert all PDFs in a folder using settings from config.yaml
  python src/convert_batch.py input_folder/ output_folder/

  # Recursively convert PDFs with custom settings
  python src/convert_batch.py input_folder/ output_folder/ -r --dpi 200

  # Sample a random page from each PDF in a folder
  python src/convert_batch.py input_folder/ --sample

  # Sample page 3 from each PDF
  python src/convert_batch.py input_folder/ --sample --sample-page 3
    """

    # Add common and batch-specific arguments
    add_common_args(parser)
    add_batch_args(parser)

    parser.add_argument("input_folder", type=str, help="Path to the folder containing PDFs.")
    parser.add_argument(
        "output_folder",
        type=str,
        nargs='?',
        default=None,
        help="Path for the output folder (required unless in --sample mode)."
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.sample and args.output_folder is None:
        parser.error("The 'output_folder' argument is required when not in --sample mode.")

    # Get final configuration
    config = get_final_config(args)

    # Find PDF files to process
    pdf_files = find_pdf_files(
        args.input_folder,
        config.get('batch', {}).get('recursive', False),
        config.get('batch', {}).get('pattern', '*.pdf')
    )

    if not pdf_files:
        print(f"⚠️ No PDF files found in '{args.input_folder}' matching the pattern.")
        sys.exit(0)

    converter = PDFConverter(config)
    results: List[ConversionResult] = []

    print(f"\n📁 Found {len(pdf_files)} PDF file(s) to process.")
    print(f"   Input folder:  {args.input_folder}")
    if not args.sample:
        print(f"   Output folder: {args.output_folder}")
    print("=" * 70)

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")

        if args.sample:
            result = converter.sample_convert(str(pdf_file), args.sample_page)
        else:
            relative_path = pdf_file.relative_to(args.input_folder)
            output_file = Path(args.output_folder).resolve() / relative_path

            if config.get('batch', {}).get('skip_existing', False) and output_file.exists():
                print(f"   ↪️ Skipping, output file already exists: {output_file}")
                continue

            result = converter.convert(str(pdf_file), str(output_file))

        results.append(result)

        if result.success:
            print(f"   ✓ Success: {result.output_size_mb:.2f} MB | {result.duration_seconds:.1f}s")
        else:
            print(f"   ✗ Failed: {result.error_message}")

    # Print the final summary
    print_batch_summary(results, args.sample)

    # Exit with a status code
    successful_count = sum(1 for r in results if r.success)
    sys.exit(0 if successful_count == len(results) else 1)


if __name__ == "__main__":
    main()
