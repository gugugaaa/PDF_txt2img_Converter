"""
Convert a single PDF file to image-based PDF
"""
import argparse
from pdf_converter import PDFConverter, ConversionConfig


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF to 'pure image PDF' (rasterize each page).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert entire PDF
  python convert_single.py input.pdf output.pdf
  
  # Convert with custom settings
  python convert_single.py input.pdf output.pdf --dpi 150 --quality 85
  
  # Sample first page before converting
  python convert_single.py input.pdf output.pdf --sample
  
  # Sample specific page (e.g., page 5)
  python convert_single.py input.pdf output.pdf --sample --sample-page 5
        """
    )
    
    parser.add_argument(
        "input_pdf",
        type=str,
        help="Path to the source PDF file"
    )
    
    parser.add_argument(
        "output_pdf",
        type=str,
        nargs='?',
        default=None,
        help="Path for the output image PDF file (not required in sample mode)"
    )
    
    parser.add_argument(
        "--dpi",
        type=int,
        default=100,
        help="Rendering DPI. Higher means clearer but larger file (default: 100)"
    )
    
    parser.add_argument(
        "--quality",
        type=int,
        default=90,
        help="JPEG compression quality 1-100 for page images (default: 90)"
    )
    
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Sample mode: convert only one page to preview the effect"
    )
    
    parser.add_argument(
        "--sample-page",
        type=int,
        default=1,
        help="Page number to sample in sample mode (default: 1)"
    )
    
    parser.add_argument(
        "--sample-dir",
        type=str,
        default="examples",
        help="Directory for sample output files (default: examples)"
    )

    args = parser.parse_args()
    
    # Validate arguments
    if args.dpi < 50 or args.dpi > 600:
        parser.error("DPI must be between 50 and 600")
    
    if args.quality < 1 or args.quality > 100:
        parser.error("Quality must be between 1 and 100")
    
    if args.sample_page < 1:
        parser.error("Sample page must be >= 1")
    
    # In non-sample mode, output_pdf is required
    if not args.sample and args.output_pdf is None:
        parser.error("output_pdf is required when not in sample mode")
    
    # Configure converter
    config = ConversionConfig(
        dpi=args.dpi,
        jpeg_quality=args.quality,
        sample_mode=args.sample,
        sample_output_dir=args.sample_dir
    )
    
    converter = PDFConverter(config)
    
    # Execute conversion
    if args.sample:
        # Sample mode: convert single page
        result = converter.sample_convert(
            args.input_pdf,
            page_num=args.sample_page - 1  # Convert to 0-indexed
        )
    else:
        # Normal mode: convert entire PDF
        result = converter.convert(args.input_pdf, args.output_pdf)
    
    # Print result
    PDFConverter.print_result(result)
    
    # Exit with appropriate code
    exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
