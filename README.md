# PDF Confectionary :cupcake:

> Work in the NLP domain and find that your end users/clients don't like using `.txt` files with your excellent results? Look no further!

PDF Confectionary is a tool for quickly creating templated PDFs from text files using [FPDF2](https://pyfpdf.github.io/fpdf2/index.html). Essentially, point it at a directory of text files, and generate some _sweet_ PDFs.

* * *

<p align="center">
<img src="https://user-images.githubusercontent.com/74869040/196545251-fb28e9ab-aa89-4c7d-b144-83e746f5d7c9.png" width="640" height="400">
</p>

<p align="center">
<i>Quickly convert text files into readable, paragraph-segmented PDFs that are easy to navigate.</i>
</p>

* * *

**Table of Contents**

<!-- TOC -->

-   [About](#about)
-   [Installation](#installation)
    -   [Requirements](#requirements)
    -   [Package Installation](#package-installation)
-   [Usage](#usage)
    -   [Command Line Usage](#command-line-usage)
    -   [Basic Usage within Python](#basic-usage-within-python)
    -   [Note: word2vec model loading](#note-word2vec-model-loading)
-   [TODO list](#todo-list)
-   [License](#license)
-   [Contributing](#contributing)

<!-- /TOC -->

* * *

## About



The focus of this repo is to provide a simple, easy-to-use, and extensible PDF creation tool. Relevant features in PDF Confectionary include:

-   Automatic paragraph separation via the `textsplit` module
-   Fast navigation through generated PDFs via links between TOC to chapters & footer links back to TOC.
-   Keyword extraction for each text file

This module was inspired by the need to create clean output documents for reading & review speech transcription from the [vid2cleantxt](https://github.com/pszemraj/vid2cleantxt) project. PDF Confectionary was initially designed as a command-line tool but provides a Python API for more advanced use cases.

* * *



## Installation

### Requirements

Primary modules used by `confectionary` are: [FPDF2](https://pyfpdf.github.io/fpdf2/index.html), [textsplit](https://github.com/chschock/textsplit), [gensim](https://radimrehurek.com/gensim/), and [clean-text](https://github.com/jfilter/clean-text).

All dependencies are listed in the `requirements.txt` file.

### Package Installation

The package can be installed using pip:

```bash
pip install confectionary
```

To install as a python package without pip, run:

```bash
git clone <https://github.com/pszemraj/confectionary.git>
cd confectionary
pip install -e .
```

## Usage

There are two ways to use PDF Confectionary:

1.  command line, via `python confectionary/text2pdf.py -i <input_dir> -o <output_dir>`

2.  Python API via functions in the `confectionary.text2pdf` module. The `dir_to_pdf` function is the equivalent of the command line tool application.

Both create one pdf from all txt files in the input directory, saved to `output_dir`. Add the `-r` switch (or `recurse=True` in function) to load files recursively.

### Command Line Usage

Call `python confectionary/text2pdf.py -i /path/to/input/dir -o /path/to/output/dir` to create a pdf from all txt files in the input directory and save it to the output directory:

```bash
    python confectionary/text2pdf.py -i /path/to/input/dir -o /path/to/output/dir \
    -kw "my keywords to label this document."
```

The below example shows the output of the command line tool and uses the `-m` switch to specify a specific word2vec model.

```sh
$ python confectionary/text2pdf.py -i "example/text-files" -o "example/outputs" -kw "my keywords to label this document" \
    -m "glove-wiki-gigaword-200"
```

Output:

    Since the GPL-licensed package `unidecode` is not installed, using Pythons `unicodedata` package which yields worse results.
    3 files found matching extension .txt

    # entries is 3, < title thresh 39
    will use one page for TOC

    Building Chapters in PDF file:   0%|                                                                                    | 0/3 [00:00<?, ?it/s]
    No local model file - downloading glove-wiki-gigaword-200 from gensim-data API
    [==================================================] 100.0% 252.1/252.1MB downloaded

    Loaded word2vec model glove-wiki-gigaword-200
    Building Chapters in PDF file: 100%|████████████████████████████████████████████████████████████████████████████| 3/3 [01:23<00:00, 27.77s/it]
    100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [00:00<00:00, 3484.61it/s]

    PDF file written to example/outputs/text-to-PDF/my keywords to label this document_txt2pdf_Oct-18-2022_standard.pdf

Find out more about the command line tool by running `python confectionary/text2pdf.py -h`.

### Basic Usage within Python

Three basic functions are available in `confectionary.text2pdf`: `dir_to_pdf`, `file_to_pdf`, and `str_to_pdf`:

-   `dir_to_pdf` takes a directory path and creates a pdf from all txt files in the directory.
-   `file_to_pdf` takes a file path and creates a pdf from the file.
-   `str_to_pdf` takes a string and creates a pdf from the string.

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

### Note: word2vec model loading

Splitting input text into paragraphs is enabled by default and uses a _word2vec_ model. If it doesn't exist, it will be downloaded via `gensim`'s API and saved to the `./models` directory.

-   the quality of the paragraph splitting and runtime of the script both depend on the size and complexity of the _word2vec_ model. If you want to use a different model, you can pass the path to the model to the `dir_to_pdf` function via the `word2vec_model` argument.
    -   the default model is `glove-wiki-gigaword-100` and is a 100-dimensional model and has a download size of ~130 MB.
-   additional models that are downloadable are listed [here](https://github.com/RaRe-Technologies/gensim-data). This info is also available by passing the `--api-info` flag to the command line tool or calling the `confectionary.utils.print_api_info()` function.
-   Using paragraph splitting is not required and can be disabled by setting the `do_paragraph_splitting` parameter to `False` or, in command line mode, by adding the `--no-split` switch.

* * *

## TODO list

-   [x] convert the `text2pdf.py` script to a module/function
-   [x] publish to PyPI
-   [x] add alternate, smaller, _word2vec_ models for splitting paragraphs
-   [ ] improve TOC calculation beyond a simple title threshold
-   [ ] Add a basic notebook demo

* * *

## License

Apache License 2.0

* * *

## Contributing

-   Given the open-ended nature of documentation creation, there are a lot of features that are not yet implemented. Please feel free to contribute!
-   Developers can contribute to this project by submitting pull requests in this repo - see details in the [contributing guide](CONTRIBUTING.md).

* * *
