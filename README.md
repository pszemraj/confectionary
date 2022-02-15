# PDF Confectionary

PDF Confectionary is a tool for quickly creating templated PDFs from text files using [FPDF2](https://pyfpdf.github.io/fpdf2/index.html). Go create some *sweet* PDFs.

## About

The primary focus of this repo is to provide a simple, easy to use, and extensible PDF creation tool. The initial use case that this project was designed around was to convert transcribed speech to a PDF for reading & review, such as in the [vid2cleantxt](https://github.com/pszemraj/vid2cleantxt) project. Relevant features in PDF Confectionary include:

- automatic paragraph separation
- TOC generation & links to TOC entries on each page (click on footer)
- keyword extraction for each txt file

PDF Confectionary was originally designed to be used as a command line tool, but it can also be used as an installable Python module (WIP).

---

## Installation

### Requirements

- Requirements are listed in the requirements.txt file.
- the primary requirements are: FPDF2, textsplit, and cleantext.

### Package Installation

    pip install -r requirements.txt

## Usage

Current usage is restricted to command line usage.

`python text2pdf.py -i /path/to/input/dir -o /path/to/output/dir`

This will create one pdf from all txt files in the input directory and save it to the output directory. Add the `-r` switch to load files recursively.

### Example

cmd line usage:

`python text2pdf.py -i "C:\Users\peter\code-dev-22\misc-repos\text2pdf\example\text-files" -o "C:\Users\peter\code-dev-22\misc-repos\text2pdf\example\outputs"`

console output is below, the result file is in the output directory `example\outputs`.

```
3 files found matching extension .txt

# entries is 3, < title thresh 39
will use one page for TOC

Building Chapters in PDF file: 100%|█| 3/3 [00
100%|█████████| 3/3 [00:00<00:00, 3010.27it/s]

PDF file saved to C:\Users\peter\code-dev-22\misc-repos\text2pdf\example\outputs\pdf_from_txt_Feb-15-2022\text-files_txt2pdf_Feb-15-2022_standard.pdf
```

---

## TODO list

1. convert the text2pdf.py script to a module/function
2. publish to PyPI
3. improve TOC calculation beyond a simple title threshold
4. Add a basic notebook demo

---

## License

Apache License 2.0

---
