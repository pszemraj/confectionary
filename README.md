# PDF Confectionary :cupcake:

> Do you work in the NLP domain and find that your end users/clients are not thrilled by receiving a ton of .txt files with your amazing results? Look no further; you are at the right place!

PDF Confectionary is a tool for quickly creating templated PDFs from text files using [FPDF2](https://pyfpdf.github.io/fpdf2/index.html). Create some *sweet* PDFs.

## About

The primary focus of this repo is to provide a simple, easy to use, and extensible PDF creation tool. The initial use case for this project was to convert transcribed speech to a PDF for reading & review, such as in the [vid2cleantxt](https://github.com/pszemraj/vid2cleantxt) project. Relevant features in PDF Confectionary include:

- Automatic paragraph separation
- TOC generation & links to TOC entries on each page (click on footer)
- Keyword extraction for each txt file

PDF Confectionary was initially designed as a command-line tool, but it can also be used as an installable Python module.

---

## Installation

### Requirements

- Requirements are listed in the requirements.txt file.
- the primary requirements are: [FPDF2](https://pyfpdf.github.io/fpdf2/index.html), [textsplit](https://github.com/chschock/textsplit), and [clean-text](https://github.com/jfilter/clean-text).

### Package Installation

The package can be installed using pip:

    pip install confectionary

To install as a python package without pip, run:

1. `git clone <https://github.com/pszemraj/confectionary.git>`
2. `cd confectionary`
3. `pip install .`

## Usage

There are two ways to use PDF Confectionary:

1. command line, via `python confectionary/text2pdf.py`

2. as a python module, via the functions located in the `confectionary.text2pdf` module. The `dir_to_pdf` function provides analogous functionality to the above command line tool.

This will create one pdf from all txt files in the input directory and save it to the output directory. Add the `-r` switch (or `recurse=True` in function) to load files recursively.

### Command Line Usage

- call `python confectionary/text2pdf.py -i /path/to/input/dir -o /path/to/output/dir` to create a pdf from all txt files in the input directory and save it to the output directory:

`python confectionary/text2pdf.py -i "./example/text-files" -o "./example/outputs"`

- console output is below (in the next section), the result file is in the output directory `example\outputs`.
- additional options can be found in the `text2pdf.py` file or by passing the `-h` switch.

### Basic Usage within Python

- three basic functions are available in `confectionary.text2pdf`: `dir_to_pdf`, `file_to_pdf`, and `str_to_pdf`:
  - `dir_to_pdf` takes a directory path and creates a pdf from all txt files in the directory.
  - `file_to_pdf` takes a file path and creates a pdf from the file.
  - `str_to_pdf` takes a string and creates a pdf from the string.

Details on the function arguments can be found in the relevant function docstrings (or call `help()`). To replicate the above command line example, run:

- `python`
- `import confectionary`
- `confectionary.text2pdf.dir_to_pdf("./example/text-files", "./example/outputs", key_phrase="test")`

The resulting output is in `example\outputs`:

```
3 files found matching extension .txt

# entries is 3, < title thresh 39
will use one page for TOC

Building Chapters in PDF file: 100%|█| 3/3 [00
100%|█████████| 3/3 [00:00<00:00, 3010.27it/s]

PDF file saved to C:\Users\peter\code-dev-22\misc-repos\text2pdf\example\outputs\pdf_from_txt_Feb-15-2022\text-files_txt2pdf_Feb-15-2022_standard.pdf
```

- see the `dir_to_pdf` docstring for more details.

### Note

- The word2vec model is quite big, 3.7GB. If it doesn't exist, it will be downloaded, and the model will be saved to the `./models` directory.
- The word2vec model is not required for the text2pdf tool and can be disabled by setting the `do_paragraph_splitting` parameter to `False` or in command line mode, by adding the `--no-split` switch.

---

## TODO list

- [x] convert the text2pdf.py script to a module/function
- [x] publish to PyPI
- [ ] add alternate, smaller, word2vec models for splitting paragraphs
- [ ] improve TOC calculation beyond a simple title threshold
- [ ] Add a basic notebook demo

---

## License

Apache License 2.0

---

## Contributing

- Given the open-ended nature of documentation creation, there are a lot of features that are not yet implemented. Please feel free to contribute!
- Developers can contribute to this project by submitting pull requests in this repo - see details in the [contributing guide](CONTRIBUTING.md).

---
