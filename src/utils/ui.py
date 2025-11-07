"""
User interface (UI) utilities for the PDF converter.

Handles the presentation of conversion results and progress to the user,
separating the core logic from the user-facing output.
"""

from pathlib import Path
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.converter import ConversionResult


def print_result(result: "ConversionResult"):
    """
    Prints the result of a single conversion operation in a formatted way.

    Args:
        result: A ConversionResult object containing the details of the conversion.
    """
    if result.success:
        if result.is_sample:
            print("\n✨ Sample conversion successful!")
            print(f"    - Input:      {result.input_path}")
            print(f"    - Sample:     {result.output_path}")
            print(f"    - Page:       {result.sample_page_num} of {result.page_count}")
            print(f"    - Size:       {result.output_size_mb:.2f} MB")
            print(f"    - Time:       {result.duration_seconds:.2f} seconds")
            print(f"\n💡 Review the sample in '{Path(result.output_path).parent}' before full conversion!")
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


def print_batch_summary(results: List["ConversionResult"], is_sample: bool):
    """
    Prints a summary for a batch conversion operation.

    Args:
        results: A list of ConversionResult objects from the batch operation.
        is_sample: A boolean indicating if the batch operation was in sample mode.
    """
    title = "📊 SAMPLE BATCH SUMMARY" if is_sample else "📊 BATCH CONVERSION SUMMARY"
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    print(f"Total files processed: {len(results)}")
    print(f"  - Successful:        {len(successful)} ✓")
    print(f"  - Failed:            {len(failed)} ✗")

    if successful:
        total_time = sum(r.duration_seconds for r in successful)
        print(f"\nTotal time taken:      {total_time:.2f} seconds")
        print(f"Average time per file: {total_time / len(successful):.2f} seconds")

        if is_sample:
            total_size = sum(r.output_size_mb for r in successful)
            print(f"Total sample size:     {total_size:.2f} MB")
        else:
            total_original = sum(r.original_size_mb for r in successful)
            total_output = sum(r.output_size_mb for r in successful)
            print(f"Total original size:   {total_original:.2f} MB")
            print(f"Total output size:     {total_output:.2f} MB")
            if total_original > 0:
                reduction = ((total_original - total_output) / total_original) * 100
                print(f"Total size reduction:  {reduction:+.1f}%")

    if failed:
        print("\n❌ Failed files:")
        for res in failed:
            print(f"  - {Path(res.input_path).name}: {res.error_message}")

    if successful and is_sample:
        sample_dir = Path(successful[0].output_path).parent
        print(f"\n✅ Sample files saved to: {sample_dir}/")
        print("   Review the samples before proceeding with full conversion!")
