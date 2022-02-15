# PDF Confectionary

PDF Confectionary is a tool for creating templated PDFs from text files, using FPDF2.

## Installation

### Requirements

- Requirements are listed in the requirements.txt file.
- the primary requirements are: FPDF2, textsplit, and cleantext.

### Installation

    pip install -r requirements.txt

### Usage

Current usage is restricted to command line usage.

`python text2pdf.py -i /path/to/input/dir -o /path/to/output/dir`

- will create one pdf from all txt files in the input directory and save it to the output directory. Add the `-r` switch to load files recursively.

## Example

TODO: Add example

## License

Apache License 2.0
