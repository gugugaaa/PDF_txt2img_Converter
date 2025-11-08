"""
PDF to Image PDF Converter
Core conversion functionality
"""
import fitz  # PyMuPDF
import os
import time
import random
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass


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

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dpi = self.config.get('conversion', {}).get('dpi', 100)
        self.jpeg_quality = self.config.get('conversion', {}).get('jpeg_quality', 90)
        self.garbage_level = self.config.get('internal', {}).get('garbage_level', 4)
        self.use_deflate = self.config.get('internal', {}).get('use_deflate', True)
        self.create_output_dir = self.config.get('internal', {}).get('create_output_dir', True)

    def convert(self, input_path: str, output_path: str) -> ConversionResult:
        """
        Convert a PDF file to an image-based PDF.

        Args:
            input_path: Path to the source PDF file.
            output_path: Path for the output PDF file.

        Returns:
            A ConversionResult object with the details of the conversion.
        """
        start_time = time.time()
        input_path = str(Path(input_path).resolve())
        output_path = str(Path(output_path).resolve())

        if not os.path.exists(input_path):
            return ConversionResult(
                success=False, input_path=input_path, output_path=output_path,
                error_message=f"Input file not found: {input_path}"
            )

        if self.create_output_dir:
            self._ensure_output_dir(output_path)

        try:
            doc_in = fitz.open(input_path)
            doc_out = fitz.open()
            page_count = len(doc_in)

            print(f"Converting: '{os.path.basename(input_path)}' ({page_count} pages)")
            print(f"Settings: DPI={self.dpi}, JPEG Quality={self.jpeg_quality}")

            for page_num, page_in in enumerate(doc_in):
                self._convert_page(page_in, doc_out, page_num, page_count)

            print("\nSaving file...")
            doc_out.save(
                output_path, garbage=self.garbage_level, deflate=self.use_deflate
            )

            original_size = os.path.getsize(input_path) / (1024 * 1024)
            output_size = os.path.getsize(output_path) / (1024 * 1024)

            return ConversionResult(
                success=True, input_path=input_path, output_path=output_path,
                original_size_mb=original_size, output_size_mb=output_size,
                duration_seconds=time.time() - start_time, page_count=page_count
            )

        except Exception as e:
            return ConversionResult(
                success=False, input_path=input_path, output_path=output_path,
                error_message=f"Conversion failed: {e}"
            )
        finally:
            if 'doc_in' in locals():
                try:
                    doc_in.close()
                except Exception:
                    pass
            if 'doc_out' in locals():
                try:
                    doc_out.close()
                except Exception:
                    pass

    def sample_convert(self, input_path: str, page_num: Optional[int] = None) -> ConversionResult:
        """
        Convert a single page from a PDF to preview the conversion effect.

        Args:
            input_path: Path to the source PDF file.
            page_num: The 1-based page number to sample. If None, a random page is chosen.

        Returns:
            A ConversionResult object with the details of the sample conversion.
        """
        start_time = time.time()
        input_path = str(Path(input_path).resolve())
        sample_dir = Path(self.config.get('sample', {}).get('output_dir', 'examples'))

        if not os.path.exists(input_path):
            return ConversionResult(
                success=False, input_path=input_path, output_path="",
                error_message=f"Input file not found: {input_path}", is_sample=True
            )

        self._ensure_output_dir(str(sample_dir))

        try:
            doc_in = fitz.open(input_path)
            total_pages = len(doc_in)

            if total_pages == 0:
                return ConversionResult(
                    success=False, input_path=input_path, output_path="",
                    error_message="PDF has no pages.", is_sample=True
                )

            # Determine which page to sample
            if page_num is None or page_num == 0:
                if total_pages > 2:
                    # Randomly select a page, excluding the first and last
                    page_to_sample_idx = random.randint(1, total_pages - 2)
                else:
                    # For PDFs with 1 or 2 pages, just sample the first page
                    page_to_sample_idx = 0
            else:
                page_to_sample_idx = page_num - 1  # Convert to 0-based index

            if not (0 <= page_to_sample_idx < total_pages):
                return ConversionResult(
                    success=False, input_path=input_path, output_path="",
                    error_message=f"Invalid page number {page_to_sample_idx + 1}. PDF has {total_pages} pages.",
                    is_sample=True
                )

            page_in = doc_in[page_to_sample_idx]
            doc_out = fitz.open()
            self._convert_page(page_in, doc_out, page_to_sample_idx, total_pages, show_progress=False)

            output_filename = f"{Path(input_path).stem}_sample_page{page_to_sample_idx + 1}_dpi{self.dpi}_q{self.jpeg_quality}.pdf"
            output_path = str(sample_dir / output_filename)

            print(f"📄 Sampling page {page_to_sample_idx + 1} of {total_pages} from '{os.path.basename(input_path)}'")
            print(f"Settings: DPI={self.dpi}, JPEG Quality={self.jpeg_quality}")
            print(f"Saving sample to: {output_path}")

            doc_out.save(output_path, garbage=self.garbage_level, deflate=self.use_deflate)
            output_size = os.path.getsize(output_path) / (1024 * 1024)

            return ConversionResult(
                success=True, input_path=input_path, output_path=output_path,
                output_size_mb=output_size, duration_seconds=time.time() - start_time,
                page_count=total_pages, is_sample=True, sample_page_num=page_to_sample_idx + 1
            )

        except Exception as e:
            return ConversionResult(
                success=False, input_path=input_path, output_path="",
                error_message=f"Sample conversion failed: {e}", is_sample=True
            )
        finally:
            if 'doc_in' in locals():
                try:
                    doc_in.close()
                except Exception:
                    pass
            if 'doc_out' in locals():
                try:
                    doc_out.close()
                except Exception:
                    pass

    def _convert_page(self, page_in, doc_out, page_num: int, total_pages: int, show_progress: bool = True):
        """Converts a single page to an image and adds it to the output document."""
        if show_progress:
            print(f"  > Processing page {page_num + 1} / {total_pages}...", end="\r")

        zoom = self.dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        pix = page_in.get_pixmap(matrix=matrix, alpha=False)

        try:
            img_bytes = pix.tobytes("jpeg", jpg_quality=self.jpeg_quality)
        except Exception as e:
            if show_progress:
                print(f"\n  > Page {page_num + 1} failed JPEG conversion, using PNG. {e}")
            img_bytes = pix.tobytes("png")

        page_out = doc_out.new_page(width=page_in.rect.width, height=page_in.rect.height)
        page_out.insert_image(page_in.rect, stream=img_bytes)

    def _ensure_output_dir(self, path: str):
        """Ensures the directory for the given path exists."""
        dir_path = Path(path).parent
        if dir_path and not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                # This is a recoverable error, so we just print a warning.
                print(f"Warning: Could not create output directory '{dir_path}': {e}")
