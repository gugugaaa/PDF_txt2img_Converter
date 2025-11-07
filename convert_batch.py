"""
Batch convert PDF files in a folder to image-based PDFs
"""
import argparse
import os
from pathlib import Path
from typing import List
from pdf_converter import PDFConverter, ConversionConfig, ConversionResult


class BatchConverter:
    """Handles batch conversion of PDF files"""
    
    def __init__(self, config: ConversionConfig):
        self.config = config
        self.converter = PDFConverter(config)
    
    def sample_folder(
        self,
        input_folder: str,
        recursive: bool = False,
        pattern: str = "*.pdf",
        sample_page: int = 0
    ) -> List[ConversionResult]:
        """
        Sample convert one page from each PDF file in a folder
        
        Args:
            input_folder: Source folder containing PDF files
            recursive: Whether to process subfolders recursively
            pattern: File pattern to match (default: "*.pdf")
            sample_page: Page number to sample (0-indexed)
            
        Returns:
            List of ConversionResult objects
        """
        input_path = Path(input_folder).resolve()
        
        if not input_path.exists():
            print(f"❌ Error: Input folder not found: {input_folder}")
            return []
        
        # Find all PDF files
        if recursive:
            pdf_files = list(input_path.rglob(pattern))
        else:
            pdf_files = list(input_path.glob(pattern))
        
        pdf_files = [f for f in pdf_files if f.is_file()]
        
        if not pdf_files:
            print(f"⚠️  No PDF files found in {input_folder}")
            return []
        
        print(f"\n📄 Sampling {len(pdf_files)} PDF file(s)")
        print(f"   Input folder:   {input_path}")
        print(f"   Sample folder:  {self.config.sample_output_dir}")
        print(f"   Sample page:    {sample_page + 1}")
        print(f"   Recursive:      {recursive}")
        print("=" * 70)
        
        results = []
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] Sampling: {pdf_file.name}")
            
            # Convert sample
            result = self.converter.sample_convert(str(pdf_file), page_num=sample_page)
            results.append(result)
            
            # Print individual result
            if result.success:
                print(f"   ✓ Success: {result.output_size_mb:.2f} MB | {result.duration_seconds:.1f}s")
            else:
                print(f"   ✗ Failed: {result.error_message}")
        
        # Print summary
        self._print_sample_summary(results)
        
        return results
    
    def convert_folder(
        self,
        input_folder: str,
        output_folder: str,
        recursive: bool = False,
        pattern: str = "*.pdf"
    ) -> List[ConversionResult]:
        """
        Convert all PDF files in a folder
        
        Args:
            input_folder: Source folder containing PDF files
            output_folder: Destination folder for converted PDFs
            recursive: Whether to process subfolders recursively
            pattern: File pattern to match (default: "*.pdf")
            
        Returns:
            List of ConversionResult objects
        """
        input_path = Path(input_folder).resolve()
        output_path = Path(output_folder).resolve()
        
        if not input_path.exists():
            print(f"❌ Error: Input folder not found: {input_folder}")
            return []
        
        # Find all PDF files
        if recursive:
            pdf_files = list(input_path.rglob(pattern))
        else:
            pdf_files = list(input_path.glob(pattern))
        
        pdf_files = [f for f in pdf_files if f.is_file()]
        
        if not pdf_files:
            print(f"⚠️  No PDF files found in {input_folder}")
            return []
        
        print(f"\n📁 Found {len(pdf_files)} PDF file(s) to convert")
        print(f"   Input folder:  {input_path}")
        print(f"   Output folder: {output_path}")
        print(f"   Recursive:     {recursive}")
        print("=" * 70)
        
        results = []
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
            
            # Calculate relative path to preserve folder structure
            try:
                relative_path = pdf_file.relative_to(input_path)
            except ValueError:
                relative_path = Path(pdf_file.name)
            
            # Determine output path
            output_file = output_path / relative_path
            
            # Convert
            result = self.converter.convert(str(pdf_file), str(output_file))
            results.append(result)
            
            # Print individual result
            if result.success:
                print(f"   ✓ Success: {result.output_size_mb:.2f} MB | {result.duration_seconds:.1f}s")
            else:
                print(f"   ✗ Failed: {result.error_message}")
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _print_sample_summary(self, results: List[ConversionResult]):
        """Print sample conversion summary"""
        print("\n" + "=" * 70)
        print("📊 SAMPLE CONVERSION SUMMARY")
        print("=" * 70)
        
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        print(f"Total files sampled:  {len(results)}")
        print(f"Successful:           {len(successful)} ✓")
        print(f"Failed:               {len(failed)} ✗")
        
        if successful:
            total_size = sum(r.output_size_mb for r in successful)
            total_time = sum(r.duration_seconds for r in successful)
            
            print(f"\nTotal sample size:    {total_size:.2f} MB")
            print(f"Total time:           {total_time:.2f} seconds")
            print(f"Average per file:     {total_time / len(successful):.2f} seconds")
            
            # Estimate full conversion
            avg_pages = sum(r.page_count for r in successful) / len(successful)
            estimated_time = total_time * avg_pages
            print(f"\n💡 Estimated time for full conversion: {estimated_time:.1f} seconds ({estimated_time / 60:.1f} minutes)")
        
        if failed:
            print(f"\n❌ Failed files:")
            for result in failed:
                print(f"   - {os.path.basename(result.input_path)}: {result.error_message}")
        
        if successful:
            print(f"\n✅ Sample files saved to: {self.config.sample_output_dir}/")
            print("   Review the samples before proceeding with full conversion!")
    
    def _print_summary(self, results: List[ConversionResult]):
        """Print batch conversion summary"""
        print("\n" + "=" * 70)
        print("📊 BATCH CONVERSION SUMMARY")
        print("=" * 70)
        
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        print(f"Total files:      {len(results)}")
        print(f"Successful:       {len(successful)} ✓")
        print(f"Failed:           {len(failed)} ✗")
        
        if successful:
            total_original = sum(r.original_size_mb for r in successful)
            total_output = sum(r.output_size_mb for r in successful)
            total_time = sum(r.duration_seconds for r in successful)
            
            print(f"\nTotal original size:  {total_original:.2f} MB")
            print(f"Total output size:    {total_output:.2f} MB")
            if total_original > 0:
                reduction = ((total_original - total_output) / total_original) * 100
                print(f"Total size change:    {reduction:+.1f}%")
            print(f"Total time:           {total_time:.2f} seconds")
        
        if failed:
            print(f"\n❌ Failed files:")
            for result in failed:
                print(f"   - {os.path.basename(result.input_path)}: {result.error_message}")


def main():
    parser = argparse.ArgumentParser(
        description="Batch convert PDF files in a folder to image-based PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sample mode - preview conversion effect
  python convert_batch.py input_folder --sample
  python convert_batch.py input_folder --sample --sample-page 3 --dpi 150
  
  # Full conversion
  python convert_batch.py input_folder output_folder
  python convert_batch.py input_folder output_folder --recursive
  python convert_batch.py input_folder output_folder -r --dpi 150 --quality 85
        """
    )
    
    parser.add_argument(
        "input_folder",
        type=str,
        help="Path to folder containing PDF files to convert"
    )
    
    parser.add_argument(
        "output_folder",
        type=str,
        nargs='?',
        default=None,
        help="Path to folder for converted PDF files (not required in sample mode)"
    )
    
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Process subfolders recursively"
    )
    
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.pdf",
        help="File pattern to match (default: *.pdf)"
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
        help="Sample mode: convert only one page from each PDF to preview the effect"
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
    
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip files that already exist in output folder"
    )

    args = parser.parse_args()
    
    # Validate arguments
    if args.dpi < 50 or args.dpi > 600:
        parser.error("DPI must be between 50 and 600")
    
    if args.quality < 1 or args.quality > 100:
        parser.error("Quality must be between 1 and 100")
    
    if args.sample_page < 1:
        parser.error("Sample page must be >= 1")
    
    # In non-sample mode, output_folder is required
    if not args.sample and args.output_folder is None:
        parser.error("output_folder is required when not in sample mode")
    
    # Configure batch converter
    config = ConversionConfig(
        dpi=args.dpi,
        jpeg_quality=args.quality,
        sample_mode=args.sample,
        sample_output_dir=args.sample_dir
    )
    
    batch_converter = BatchConverter(config)
    
    # Execute conversion
    if args.sample:
        # Sample mode
        results = batch_converter.sample_folder(
            input_folder=args.input_folder,
            recursive=args.recursive,
            pattern=args.pattern,
            sample_page=args.sample_page - 1  # Convert to 0-indexed
        )
    else:
        # Full conversion mode
        results = batch_converter.convert_folder(
            input_folder=args.input_folder,
            output_folder=args.output_folder,
            recursive=args.recursive,
            pattern=args.pattern
        )
    
    # Exit with appropriate code
    success_count = sum(1 for r in results if r.success)
    exit(0 if success_count == len(results) else 1)


if __name__ == "__main__":
    main()
