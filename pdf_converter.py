"""
PDF to Image PDF Converter
Core conversion functionality
"""
import fitz  # PyMuPDF
import os
import time
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class ConversionConfig:
    """Configuration for PDF conversion"""
    dpi: int = 100
    jpeg_quality: int = 90
    create_output_dir: bool = True
    garbage_level: int = 4
    use_deflate: bool = True
    sample_mode: bool = False
    sample_output_dir: str = "examples"


@dataclass
class ConversionResult:
    """Result of a PDF conversion operation"""
    success: bool
    input_path: str
    output_path: str
    original_size_mb: float = 0.0
    output_size_mb: float = 0.0
    duration_seconds: float = 0.0
    page_count: int = 0
    error_message: Optional[str] = None
    is_sample: bool = False
    sample_page_num: Optional[int] = None


class PDFConverter:
    """Handles PDF to image-based PDF conversion"""
    
    def __init__(self, config: Optional[ConversionConfig] = None):
        self.config = config or ConversionConfig()
    
    def convert(self, input_path: str, output_path: str) -> ConversionResult:
        """
        Convert a PDF file to an image-based PDF
        
        Args:
            input_path: Path to the source PDF file
            output_path: Path for the output PDF file
            
        Returns:
            ConversionResult object with conversion details
        """
        start_time = time.time()
        input_path = str(Path(input_path).resolve())
        output_path = str(Path(output_path).resolve())
        
        # Validate input
        if not os.path.exists(input_path):
            return ConversionResult(
                success=False,
                input_path=input_path,
                output_path=output_path,
                error_message=f"Input file not found: {input_path}"
            )
        
        # Create output directory if needed
        if self.config.create_output_dir:
            output_dir = os.path.dirname(output_path)
            if output_dir and output_dir != "." and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except Exception as e:
                    return ConversionResult(
                        success=False,
                        input_path=input_path,
                        output_path=output_path,
                        error_message=f"Failed to create output directory: {e}"
                    )
        
        # Perform conversion
        try:
            doc_in = fitz.open(input_path)
        except Exception as e:
            return ConversionResult(
                success=False,
                input_path=input_path,
                output_path=output_path,
                error_message=f"Could not open source PDF: {e}"
            )
        
        try:
            doc_out = fitz.open()
            page_count = len(doc_in)
            
            print(f"Converting: '{os.path.basename(input_path)}' ({page_count} pages)")
            print(f"Settings: DPI={self.config.dpi}, JPEG Quality={self.config.jpeg_quality}")
            
            # Convert each page
            for page_num, page_in in enumerate(doc_in):
                self._convert_page(page_in, doc_out, page_num, page_count)
            
            print("\nSaving file...")
            
            # Save output
            doc_out.save(
                output_path,
                garbage=self.config.garbage_level,
                deflate=self.config.use_deflate
            )
            
            doc_in.close()
            doc_out.close()
            
            # Calculate statistics
            end_time = time.time()
            original_size = os.path.getsize(input_path) / (1024 * 1024)
            output_size = os.path.getsize(output_path) / (1024 * 1024)
            duration = end_time - start_time
            
            return ConversionResult(
                success=True,
                input_path=input_path,
                output_path=output_path,
                original_size_mb=original_size,
                output_size_mb=output_size,
                duration_seconds=duration,
                page_count=page_count
            )
            
        except Exception as e:
            if 'doc_in' in locals():
                doc_in.close()
            if 'doc_out' in locals():
                doc_out.close()
            return ConversionResult(
                success=False,
                input_path=input_path,
                output_path=output_path,
                error_message=f"Conversion failed: {e}"
            )
    
    def sample_convert(self, input_path: str, page_num: int = 0) -> ConversionResult:
        """
        Convert a single page from PDF to preview the conversion effect
        
        Args:
            input_path: Path to the source PDF file
            page_num: Page number to sample (0-indexed, default: 0 for first page)
            
        Returns:
            ConversionResult object with conversion details
        """
        start_time = time.time()
        input_path = str(Path(input_path).resolve())
        
        # Validate input
        if not os.path.exists(input_path):
            return ConversionResult(
                success=False,
                input_path=input_path,
                output_path="",
                error_message=f"Input file not found: {input_path}",
                is_sample=True
            )
        
        # Create sample output directory
        sample_dir = Path(self.config.sample_output_dir)
        if not sample_dir.exists():
            try:
                sample_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return ConversionResult(
                    success=False,
                    input_path=input_path,
                    output_path="",
                    error_message=f"Failed to create sample directory: {e}",
                    is_sample=True
                )
        
        # Construct output filename
        input_filename = Path(input_path).stem
        output_filename = f"{input_filename}_sample_page{page_num + 1}_dpi{self.config.dpi}_q{self.config.jpeg_quality}.pdf"
        output_path = str(sample_dir / output_filename)
        
        # Perform sampling conversion
        try:
            doc_in = fitz.open(input_path)
            total_pages = len(doc_in)
            
            # Validate page number
            if page_num < 0 or page_num >= total_pages:
                doc_in.close()
                return ConversionResult(
                    success=False,
                    input_path=input_path,
                    output_path=output_path,
                    error_message=f"Invalid page number {page_num + 1}. PDF has {total_pages} pages.",
                    is_sample=True,
                    sample_page_num=page_num + 1
                )
            
            print(f"📄 Sampling page {page_num + 1} of {total_pages} from '{os.path.basename(input_path)}'")
            print(f"Settings: DPI={self.config.dpi}, JPEG Quality={self.config.jpeg_quality}")
            
            doc_out = fitz.open()
            page_in = doc_in[page_num]
            
            # Convert the single page
            self._convert_page(page_in, doc_out, page_num, total_pages, show_progress=False)
            
            print(f"Saving sample to: {output_path}")
            
            # Save output
            doc_out.save(
                output_path,
                garbage=self.config.garbage_level,
                deflate=self.config.use_deflate
            )
            
            doc_in.close()
            doc_out.close()
            
            # Calculate statistics
            end_time = time.time()
            output_size = os.path.getsize(output_path) / (1024 * 1024)
            duration = end_time - start_time
            
            return ConversionResult(
                success=True,
                input_path=input_path,
                output_path=output_path,
                original_size_mb=0.0,  # Not meaningful for single page
                output_size_mb=output_size,
                duration_seconds=duration,
                page_count=total_pages,
                is_sample=True,
                sample_page_num=page_num + 1
            )
            
        except Exception as e:
            if 'doc_in' in locals():
                doc_in.close()
            if 'doc_out' in locals():
                doc_out.close()
            return ConversionResult(
                success=False,
                input_path=input_path,
                output_path=output_path,
                error_message=f"Sample conversion failed: {e}",
                is_sample=True,
                sample_page_num=page_num + 1
            )
    
    def _convert_page(self, page_in, doc_out, page_num: int, total_pages: int, show_progress: bool = True):
        """Convert a single page to image"""
        if show_progress:
            print(f"  > Processing page {page_num + 1} / {total_pages}...", end="\r")
        
        zoom = self.config.dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        
        # Render page to image
        pix = page_in.get_pixmap(matrix=matrix, alpha=False)
        
        # Convert to JPEG (fallback to PNG if fails)
        try:
            img_bytes = pix.tobytes("jpeg", jpg_quality=self.config.jpeg_quality)
        except Exception as e:
            if show_progress:
                print(f"\n  > Page {page_num + 1} failed JPEG conversion, using PNG. {e}")
            img_bytes = pix.tobytes("png")
        
        # Create new page and insert image
        page_out = doc_out.new_page(width=page_in.rect.width, height=page_in.rect.height)
        page_out.insert_image(page_in.rect, stream=img_bytes)
    
    @staticmethod
    def print_result(result: ConversionResult):
        """Print conversion result in a formatted way"""
        if result.success:
            if result.is_sample:
                print("\n✨ Sample conversion successful!")
                print(f"    - Input:      {result.input_path}")
                print(f"    - Sample:     {result.output_path}")
                print(f"    - Page:       {result.sample_page_num} of {result.page_count}")
                print(f"    - Size:       {result.output_size_mb:.2f} MB")
                print(f"    - Time:       {result.duration_seconds:.2f} seconds")
                print(f"\n💡 Review the sample in '{Path(result.output_path).parent}' folder before batch conversion!")
            else:
                print("\n🎉 Conversion successful!")
                print(f"    - Input:  {result.input_path} ({result.original_size_mb:.2f} MB)")
                print(f"    - Output: {result.output_path} ({result.output_size_mb:.2f} MB)")
                print(f"    - Pages:  {result.page_count}")
                print(f"    - Time:   {result.duration_seconds:.2f} seconds")
                if result.original_size_mb > 0:
                    reduction = ((result.original_size_mb - result.output_size_mb) / result.original_size_mb) * 100
                    print(f"    - Size change: {reduction:+.1f}%")
        else:
            if result.is_sample:
                print(f"\n❌ Sample conversion failed: {result.error_message}")
            else:
                print(f"\n❌ Conversion failed: {result.error_message}")
