# PDF Confectionary :cupcake

> Do you work in the NLP domain and find that your end users/clients are not thrilled by receiving a ton of .txt files with your amazing results? Look no further; you are at the right place!

PDF Confectionary is a tool for quickly creating templated PDFs from text files using [FPDF2](https://pyfpdf.github.io/fpdf2/index.html). Create some *sweet* PDFs.

## About

The primary focus of this repo is to provide a simple, easy to use, and extensible PDF creation tool. T Relevant features in PDF Confectionary include:

- Automatic paragraph separation via the ``textsplit`` module
- Fast navigation through generated PDFs via links between TOC to chapters & footer links back to TOC.
- Keyword extraction for each txt file

The initial use case that inspired this project was the need creating clean output documents for reading & review from speech transcription in the [vid2cleantxt](https://github.com/pszemraj/vid2cleantxt) project. PDF Confectionary was initially designed as a command-line tool, but also provides a Python API for more advanced use cases.

---

## Installation

### Requirements

- the primary requirements are: [FPDF2](https://pyfpdf.github.io/fpdf2/index.html), [textsplit](https://github.com/chschock/textsplit), [gensim](https://radimrehurek.com/gensim/), and [clean-text](https://github.com/jfilter/clean-text).
- Requirements are listed in the ``requirements.txt`` file.

### Package Installation

The package can be installed using pip:

```bash
pip install confectionary
```

To install as a python package without pip, run:

```bash
git clone <https://github.com/pszemraj/confectionary.git>
cd confectionary
python setup.py install
```

\*Note: running `setup.py` can be replaced with `pip install -e .` if you are in the root directory of the repo.

## Usage

There are two ways to use PDF Confectionary:

1. command line, via `python confectionary/text2pdf.py -i <input_dir> -o <output_dir>`

2. Python API via functions in the `confectionary.text2pdf` module. The `dir_to_pdf` function is the equivalent of the command line tool application.

Both create one pdf from all txt files in the input directory and save it to the output directory. Add the `-r` switch (or `recurse=True` in function) to load files recursively.

### Command Line Usage

- call `python confectionary/text2pdf.py -i /path/to/input/dir -o /path/to/output/dir` to create a pdf from all txt files in the input directory and save it to the output directory:

```bash
    python confectionary/text2pdf.py -i /path/to/input/dir -o /path/to/output/dir -kw "my keywords to label this document"
```

- console output is below (in the next section), the result file is in the output directory `example/outputs`.

Find out more info about the command line tool by running `python confectionary/text2pdf.py -h`.

### Basic Usage within Python

Three basic functions are available in `confectionary.text2pdf`: `dir_to_pdf`, `file_to_pdf`, and `str_to_pdf`:

- `dir_to_pdf` takes a directory path and creates a pdf from all txt files in the directory.
- `file_to_pdf` takes a file path and creates a pdf from the file.
- `str_to_pdf` takes a string and creates a pdf from the string.

Details on the function arguments can be found in the relevant function docstrings (or call `help()`). To replicate the above command line usage, use the following code:

```python
from confectionary.text2pdf import dir_to_pdf

report_path = dir_to_pdf(
    input_dir="/path/to/input/dir",
    output_dir="/path/to/output/dir",
    keywords="my keywords to label this document",
)

print(f"Report saved to {report_path}")
```

Check out the `dir_to_pdf` docstring for more options:

```python
import inspect
from confectionary.text2pdf import dir_to_pdf

inspect.getdoc(dir_to_pdf)
```

### Note

Splitting input text into paragraphs is enabled by default and uses a *word2vec* model to do so. If it doesn't exist, it will be downloaded via `gensim`'s API, and saved to the `./models` directory.

- the quality of the paragraph splitting is dependent on the quality of the *word2vec* model. If you want to use a different model, you can pass the path to the model to the `dir_to_pdf` function via the `word2vec_model` argument.
- additional models that are downloadable are listed [here](<https://github.com/RaRe-Technologies/gensim-data>). This info is also available by passing the ``--api-info`` flag to the command line tool or by calling the `confectionary.report_generator.print_api_info()` function.
- Using paragraph splitting is not required, and can be disabled by setting the `do_paragraph_splitting` parameter to `False` or in command line mode, by adding the `--no-split` switch.

---

## TODO list

- [x] convert the text2pdf.py script to a module/function
- [x] publish to PyPI
- [x] add alternate, smaller, word2vec models for splitting paragraphs
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
