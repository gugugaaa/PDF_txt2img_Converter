# PDF Image Converter

A simple and efficient tool to convert PDF files into image-based PDFs, helping to reduce file size and flatten content.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure (Optional):**
    Modify `config.yaml` to set your preferred default DPI and quality settings.

## Usage

All commands should be run from the project's root directory.

### Convert a Single File

```bash
python src/convert_single.py path/to/input.pdf path/to/output.pdf
```

### Batch Convert a Folder

```bash
python src/convert_batch.py path/to/input_folder/ path/to/output_folder/
```
*Add the `-r` flag to process folders recursively.*

### Sample a Random Page

To quickly preview the conversion quality, you can sample a single, random page from a PDF.

```bash
python src/convert_single.py path/to/input.pdf --sample
```
*The sample file will be saved in the `examples/` directory by default.*
