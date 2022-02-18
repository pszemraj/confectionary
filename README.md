# PDF Confectionary :cupcake:

> Do you work in the NLP domain and find that your end users/clients are not thrilled by receiving a ton of .txt files with your amazing results? Look no further, you are at the right place!

PDF Confectionary is a tool for quickly creating templated PDFs from text files using [FPDF2](https://pyfpdf.github.io/fpdf2/index.html). Go create some *sweet* PDFs.

## About

The primary focus of this repo is to provide a simple, easy to use, and extensible PDF creation tool. The initial use case that this project was designed around was to convert transcribed speech to a PDF for reading & review, such as in the [vid2cleantxt](https://github.com/pszemraj/vid2cleantxt) project. Relevant features in PDF Confectionary include:

- automatic paragraph separation
- TOC generation & links to TOC entries on each page (click on footer)
- keyword extraction for each txt file

PDF Confectionary was originally designed to be used as a command line tool, but it can also be used as an installable Python module.

---

## Installation

### Requirements

- Requirements are listed in the requirements.txt file.
- the primary requirements are: FPDF2, textsplit, and cleantext.

### Package Installation

- to install as a python package without pip, run:

    git clone <https://github.com/pszemraj/confectionary.git>
    pip install -r requirements.txt
    pip install .

## Usage

Current usage is restricted to command line usage:

- `python confectionary/text2pdf.py -i /path/to/input/dir -o /path/to/output/dir`

This will create one pdf from all txt files in the input directory and save it to the output directory. Add the `-r` switch to load files recursively.

### Command Line Usage

- call `python confectionary/text2pdf.py -i /path/to/input/dir -o /path/to/output/dir` to create a pdf from all txt files in the input directory and save it to the output directory:

`python confectionary/text2pdf.py -i "./example/text-files" -o "./example/outputs"`

- console output is below (in the next section), the result file is in the output directory `example\outputs`.

### Basic Usage within Python

- `python`
- `import confectionary`
- `confectionary.text2pdf.convert_files_to_pdf("./example/text-files", "./example/outputs", keywords="test")`

Resulting output is in `example\outputs`:

```
3 files found matching extension .txt

# entries is 3, < title thresh 39
will use one page for TOC

Building Chapters in PDF file: 100%|█| 3/3 [00
100%|█████████| 3/3 [00:00<00:00, 3010.27it/s]

PDF file saved to C:\Users\peter\code-dev-22\misc-repos\text2pdf\example\outputs\pdf_from_txt_Feb-15-2022\text-files_txt2pdf_Feb-15-2022_standard.pdf
```

### Note

- The word2vec model is quite big, 3.7GB. It will be downloaded if it doesn't exist, and the model will be saved to the `./models` directory.
- The word2vec mode is not required for the text2pdf tool, and can be disabled by setting the `do_paragraph_splitting` parameter to `False` or in command line mode, by adding the `--no-split` switch.

---

## TODO list

[x] convert the text2pdf.py script to a module/function
[ ] publish to PyPI
[ ] improve TOC calculation beyond a simple title threshold
[ ] add alternate, smaller, word2vec models for splitting paragraphs
[ ] Add a basic notebook demo

---

## License

Apache License 2.0

---

## Contributing

Developers can contribute to this project by submitting pull requests in this repo - see details in the [contributing guide](CONTRIBUTING.md).

---