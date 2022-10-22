"""
this script contains helper functions to generate a PDF report from a list of entries, including paragraph splitting by coherence, and a table of contents.
"""
import math
import warnings
from pathlib import Path

import gensim.downloader as api
import joblib
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from textsplit.algorithm import split_optimal
from textsplit.tools import SimpleSentenceTokenizer, get_penalty, get_segments
from tqdm.auto import tqdm

model_storage_loc = Path.cwd() / "models"
model_storage_loc.mkdir(exist_ok=True)


def load_word2vec_model(
    word2vec_model: str = "glove-wiki-gigaword-100",
    storage_loc=model_storage_loc,
    verbose=False,
):
    """
    Loads a word2vec model through the gensim.data api.

        See this repo for more details: https://github.com/RaRe-Technologies/gensim-data
        the print_api_info() function will print the available models to load.

    :param word2vec_model: Name of the model to load, default is "glove-wiki-gigaword-100"
    :param storage_loc: Location to store the model locally, defaults to current working directory as a subdirectory called "models"
    :param verbose: bool, default False, print the model info

    :return: Word2Vec model, a gensim.models.keyedvectors.Word2VecKeyedVectors object
    """
    storage_loc = Path(storage_loc)
    storage_loc.mkdir(exist_ok=True)

    # check if an existing .pkl file exists with the same name, otherwise load it
    model_path = storage_loc / f"{word2vec_model}.pkl"
    if model_path.exists():
        if verbose:
            print("\nLoading existing word2vec model from {}".format(word2vec_model))
        model = joblib.load(model_path)
    else:
        print(
            f"\nNo local model file - downloading {word2vec_model} from gensim-data API"
        )
        model = api.load(word2vec_model)
        joblib.dump(model, model_path, compress=True)
        if verbose:
            print(f"Saved model to {model_path}")
    print(f"\nLoaded word2vec model {word2vec_model}")
    return model


def estimate_TOC_pages(
    n_entries: int, title_thresh: int = 39, std_thresh: int = 60, verbose=False
):
    """
    estimate_TOC_pages - a naive estimator for the number of pages required for
                        generated PDF report. Probably should be replaced by a
                        function that computes the actual distance / space with
                        the font size etc.
    Parameters
    ----------
    n_entries : int, the number of entries in the report
    title_thresh : int, the number of entries that will be printed on a single
                    page
    std_thresh : int, the number of entries that will be printed on a single
                    page
    verbose : bool, default False, print the number of pages estimated

    Returns
    ------
    int, the number of pages to save for TOC
    """
    assert n_entries > 0, f"require >=1 entry to estimate # pages, got {n_entries}"
    title_num = int(math.ceil(n_entries / title_thresh))
    if title_num < 2:
        if verbose:
            print(f"\n# entries is {n_entries}, < title thresh {title_thresh}")
            print("will use one page for TOC\n")
        return 1
    else:
        std_pg_entries = n_entries - title_thresh  # get entries not on the title page
        std_num = int(math.ceil(std_pg_entries / std_thresh))
        # TODO: find out what std_thresh actually is moving from 2->3 pages
        # and update
        toc_pgs = 1 + std_num
        if verbose:
            print(f"\n# entries is {n_entries}, > title thresh {title_thresh}")
            print(f"will use {toc_pgs} pages for TOC\n")
        return 1 + std_num


def load_punkt(nltk_usepunkt=True):
    """
    load_punkt - loads the punkt sentence tokenizer from nltk.

    Parameters
    ----------
    nltk_usepunkt : bool, optional, default True

    Returns
    -------
    punkt_sent_tokenizer : PunktSentenceTokenizer   # nltk.tokenize.punkt.PunktSentenceTokenizer
    """
    try:
        nltk.data.find("tokenizers/punkt")
        sent_detector = (
            nltk.data.load("tokenizers/punkt/english.pickle") if nltk_usepunkt else None
        )
    except LookupError:
        # if punkt is not installed, download it
        nltk.download("punkt")
        sent_detector = (
            nltk.data.load("tokenizers/punkt/english.pickle") if nltk_usepunkt else None
        )

    return sent_detector


def split_to_pars(
    full_text,
    wordvectors,
    use_punkt=False,
    sent_detector=None,
    segment_len=5,
    verbose=False,
):
    """
    split_to_pars - splits a string into paragraphs using the punkt sentence tokenizer or default

    Parameters
    ----------
    full_text : str, the full text to split into paragraphs
    wordvectors : Word2Vec model, the word2vec model to use for word embeddings
    use_punkt : bool, optional, default False
    sent_detector : [type], optional, default None, the punkt sentence tokenizer to use for splitting
    segment_len : int, optional, default 5, the length of the segments to use for word embeddings
    verbose : bool, optional, default False

    Returns
    -------
    list of str, the paragraphs of the text
    """
    if verbose:
        print(f"Splitting text into paragraphs using {segment_len}-word segments")
    sent_detector = (
        load_punkt(use_punkt) if use_punkt and sent_detector is None else sent_detector
    )
    if use_punkt:
        sentenced_text = sent_detector.tokenize(full_text.strip())
    else:
        sentence_tokenizer = SimpleSentenceTokenizer()
        sentenced_text = sentence_tokenizer(full_text)

    if isinstance(sentenced_text, str):
        sentenced_text = sentenced_text.split(".")

    # both parameters definitely will change depending on application
    if len(sentenced_text) > segment_len:
        vecr = CountVectorizer(vocabulary=wordvectors.index)
        sentence_vectors = vecr.transform(sentenced_text).dot(wordvectors)
        try:
            penalty = get_penalty([sentence_vectors], segment_len)
            optimal_segmentation = split_optimal(sentence_vectors, penalty)
            segmented_text = get_segments(sentenced_text, optimal_segmentation)
            paragraphs = [" ".join(segment) for segment in segmented_text]

            # segmented_text is a list of lists. The first level is segment and the second is sentences in the segment
        except Exception as e:
            warnings.warn(f"Error in split_to_pars: {e}, returning full text")
            segmented_text = sentenced_text
            paragraphs = segmented_text

    else:
        # the input text has less sentences than desired segments.
        # Just return the sentenced text
        warnings.warn(
            f"Input text has less sentences than desired segments. Returning full text"
        )
        paragraphs = sentenced_text
    # strip whitespace from the beginning and end of each paragraph
    paragraphs = [p.strip(" ") for p in paragraphs]
    return paragraphs


def print_pdf_margin_info(the_pdf):
    """
    print_pdf_margin_info - prints the margins of the pdf

    Parameters
    ----------
    the_pdf : FPDF object, the pdf to print margins for
    """
    pdf_height = the_pdf.h
    pdf_width = the_pdf.w
    left_margin = the_pdf.l_margin
    right_margin = the_pdf.r_margin
    writeable_space = math.floor(pdf_width - left_margin - right_margin)
    print(
        f"PDF dimensions are {round(pdf_width,3)} mm wide by {round(pdf_height,3)} mm tall"
    )
    print(
        f"width: {round(pdf_width,2)} mm ",
        f"The margins are  R: {right_margin} mm,  L: {left_margin} mm ",
    )
    print(f"the total useable space is {writeable_space} mm ")


def p_outside(pdf, text, **kwargs):
    """
    p_outside - prints text outside the margins of the pdf

    """
    # if you want to set align="C" you need to pass it in as a **kwargs
    pdf.multi_cell(w=pdf.epw, h=pdf.font_size, txt=text, ln=1, **kwargs)


def render_toc(pdf, outline, title="Table of Contents", verbose=False):
    """
    render_toc - renders the outline of the pdf

    Parameters
    ----------
    pdf : FPDF object, the pdf to render the outline for
    outline : list of dicts, the outline to render
    """
    # configure params
    pdf.y += 20
    pdf.set_x(pdf.l_margin)  # was in some weird location
    pdf.set_font("Helvetica", size=16)
    pdf.set_text_color(0)
    pdf.underline = False
    p_outside(pdf, title, align="L")  # write title of TOC
    pdf.y += 15
    pdf.set_font("Courier", size=12)
    # iterate through items
    for section in tqdm(outline):
        link = pdf.add_link()
        pdf.set_link(link, page=section.page_number)
        # get rid of spaces and the word chapter, keep only the first 20 chars

        upd_section_name = section.name
        upd_section_name = upd_section_name.replace("Chapter", "")
        if len(upd_section_name) > 45:
            upd_section_name = upd_section_name[:45]

        text = f'{" " * section.level * 2} {upd_section_name}'
        text += f' {"." * (60 - section.level * 2 - len(upd_section_name))} {section.page_number}'
        pdf.multi_cell(w=pdf.epw, h=pdf.font_size, txt=text, ln=1, align="C", link=link)
