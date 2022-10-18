"""
This file contains utility functions for the project.
"""

import os
import pprint as pp
import random
import re
import shutil
import warnings
from datetime import datetime
from os.path import join
from pathlib import Path

import gensim.downloader as api
import wordninja
import yake
from cleantext import clean
from natsort import natsorted


def get_user():
    """get_user - returns the username of the user running the script"""
    try:
        return os.getlogin()
    except Exception:
        return "unknown"


def get_seq2replace(additional_terms: list = None):
    """
    get_seq2replace - returns a list of terms to be replaced from text. This is used to remove "filename" stopwords from the text.

    Parameters
    ----------
    additional_terms : list, optional, default None, list of additional terms to be replaced

    Returns
    -------
    list, list of terms to be replaced
    """
    seq2replace = [
        "fins",
        "phones",
        "cons",
        "fin",
        "pegasus",
        "phone",
        "con",
        "-v-",
        "---",
        "summ",
        "sum",
        "ocr",
    ]
    if additional_terms is not None:
        seq2replace.extend(additional_terms)
    return seq2replace


def get_first_number(my_string: str):
    """
    get_first_number - return the first number found in a string with regex as an integer

    Parameters
    ----------
    my_string : str, required, input

    Returns
    -------
    int, first number found in the string
    """
    search = re.search(r"\d+", my_string)
    if search is None:
        warnings.warn(
            "No number found in string: {}, returning random".format(my_string)
        )
        return random.randint(0, 10**8)
    else:
        return int(search.group(0))


def fix_punct_spaces(string: str):
    """
    fix_punct_spaces - replace spaces around punctuation with punctuation. For example, "hello , there" -> "hello, there"

    Parameters
    ----------
    string : str, required, input string to be corrected

    Returns
    -------
    str, corrected string
    """

    fix_spaces = re.compile(r"\s*([?!.,]+(?:\s+[?!.,]+)*)\s*")
    string = fix_spaces.sub(lambda x: "{} ".format(x.group(1).replace(" ", "")), string)
    string = string.replace(" ' ", "'")
    string = string.replace(' " ', '"')
    string = string.replace("- _", "-")
    string = string.replace("_ -", "-")
    string = string.replace(" _ ", "-")
    string = string.replace("_ ", "-")
    string = string.strip("_")
    return string.strip()


def dict_sort_by_keys(d: dict):
    """
    dict_sort_by_keys - given a dictionary, sorts and returns the dictionary sorted by ascending keys

    Parameters
    ----------
    d : dict, required, input dictionary

    Returns
    -------
    dict, sorted dictionary
    """
    return {k: v for k, v in natsorted(d.items(), key=lambda item: item[0])}


def dict_sort_by_vals(d: dict):
    """
    dict_sort_by_keys - given a dictionary, sorts and returns the dictionary sorted by ascending values

    Parameters
    ----------
    d : dict, required, input dictionary

    Returns
    -------
    dict, sorted dictionary
    """
    return {k: v for k, v in natsorted(d.items(), key=lambda item: item[1])}


def load_files_ext(target_dir, ext: str, recursive=False, verbose=False):
    """
    load_files_ext - loads all files with a given extension from a directory, optionally recursively. It then returns a list of the files that is sorted by name.

    :param path: Path to the files.
    :param ext: Extension of the files. e.g. 'txt'
    :param recursive: If True, the function will recursively search for files.

    :return: List of files, sorted by the first number found in the filename.
    """
    target_dir = Path(target_dir)
    ext = ext.replace(".", "")  # make sure extension is lowercase and without dot
    files = []
    if verbose:
        print("Loading files from {} with extension {}".format(target_dir, ext))
    if recursive:
        for file in target_dir.glob("**/*." + ext):
            files.append(file)
    else:
        for file in target_dir.glob("*." + ext):
            files.append(file)
    ids = [get_first_number(file.name) for file in files]
    my_dict = dict(zip(files, ids))
    sorted_dict = dict_sort_by_vals(my_dict)
    return sorted_dict.keys()


def get_timestamp(detailed=False):
    """
    get_timestamp - returns a timestamp in string format

    detailed : bool, optional, default False, if True, returns a timestamp with seconds
    """
    if detailed:
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    else:
        return datetime.now().strftime("%b-%d-%Y")


def create_folder(directory):
    os.makedirs(directory, exist_ok=True)


def corr(s: str):
    """
    corr - adds space after period if there isn't one. For example, "hello.there" -> "hello. there"
            removes extra spaces. For example, "hello  there" -> "hello there"
    """
    return re.sub(r"\.(?! )", ". ", re.sub(r" +", " ", s))


def cleantxt_wrap(ugly_text: str):
    # a wrapper for clean text with options different than default

    # https://pypi.org/project/clean-text/
    cleaned_text = clean(
        ugly_text,
        fix_unicode=True,  # fix various unicode errors
        to_ascii=True,  # transliterate to closest ASCII representation
        lower=False,  # lowercase text
        no_line_breaks=True,  # fully strip line breaks as opposed to only normalizing them
        no_urls=True,  # replace all URLs with a special token
        no_emails=True,  # replace all email addresses with a special token
        no_phone_numbers=True,  # replace all phone numbers with a special token
        no_numbers=False,  # replace all numbers with a special token
        no_digits=False,  # replace all digits with a special token
        no_currency_symbols=True,  # replace all currency symbols with a special token
        no_punct=True,  # remove punctuations
        replace_with_punct="",  # instead of removing punctuations you may replace them
        replace_with_url="<URL>",
        replace_with_email="<EMAIL>",
        replace_with_phone_number="<PHONE>",
        replace_with_number="<NUM>",
        replace_with_digit="0",
        replace_with_currency_symbol="<CUR>",
        lang="en",  # set to 'de' for German special handling
    )

    return cleaned_text


def cleantxt_summary(ugly_text, lang="en"):
    # a wrapper for clean text with options different than default

    # https://pypi.org/project/clean-text/
    cleaned_text = clean(
        ugly_text,
        fix_unicode=True,  # fix various unicode errors
        to_ascii=True,  # transliterate to closest ASCII representation
        lower=False,  # lowercase text
        no_line_breaks=True,  # fully strip line breaks as opposed to only normalizing them
        no_urls=True,  # replace all URLs with a special token
        no_emails=True,  # replace all email addresses with a special token
        no_phone_numbers=True,  # replace all phone numbers with a special token
        no_numbers=False,  # replace all numbers with a special token
        no_digits=False,  # replace all digits with a special token
        no_currency_symbols=True,  # replace all currency symbols with a special token
        no_punct=False,  # remove punctuations
        replace_with_punct="",  # instead of removing punctuations you may replace them
        replace_with_url="<URL>",
        replace_with_email="<EMAIL>",
        replace_with_phone_number="<PHONE>",
        replace_with_number="<NUM>",
        replace_with_digit="0",
        replace_with_currency_symbol="<CUR>",
        lang=lang,  # de
    )

    return cleaned_text


def beautify_filename(
    filename,
    num_words=20,
    start_reverse=False,
    word_separator="_",
    replace_underscores=True,
):
    """
    beautify_filename - given a filename, returns a string with the first num_words words separated by word_separator

    Parameters
    ----------
    filename : str, required, input filename
    num_words : int, optional, number of words to include in the string, default is 20
    start_reverse : bool, optional, if True, the first num_words words are reversed, default is False
    word_separator : str, optional, word separator, default is "_"
    replace_underscores : bool, optional, if True, replaces underscores with a whitespace at the end, default is True

    Returns
    -------
    str, string with the first num_words words separated by word_separator
    """

    filename = str(filename)
    current_name = filename.split(".")[0]
    extension = filename.split(".")[-1]
    if current_name.isnumeric():
        current_name = current_name + extension
        return current_name
    clean_name = cleantxt_wrap(current_name)
    file_words = wordninja.split(clean_name)
    # splits concatenated text into a list of words based on common word freq

    if num_words > len(file_words):
        t_file_words = file_words
    else:
        if start_reverse:
            t_file_words = file_words[-num_words:]
        else:
            t_file_words = file_words[:num_words]

    pretty_name = word_separator.join(t_file_words)  # see function argument
    pretty_name = pretty_name.replace("_", " ") if replace_underscores else pretty_name
    # NOTE IT DOES NOT RETURN THE EXTENSION
    return pretty_name.strip()


def simple_rename(
    filepath,
    header: str = "",
    max_char_orig: int = None,
    target_ext: str = ".txt",
    no_ext: bool = False,
):
    """
    simple_rename - given a filepath, extracts the base name and adds a header, and returns a new filepath with extension target_ext. The extracted name is truncated to max_char_orig if specified.

    Parameters
    ----------
    filepath : str or pathlib.Path, required, input filepath
    header : str, optional, header to add to the file name, default is ""
    max_char_orig : int, optional, maximum number of characters to keep from the original name, default is None (no truncation)
    target_ext : str, optional, target extension, default is ".txt"

    Returns
    -------
    str, new file name with extension target_ext (if no_ext is False)
    """
    _fp = Path(filepath)
    basename = _fp.stem
    max_char_orig = len(basename) if max_char_orig is None else max_char_orig
    target_ext = target_ext if target_ext.startswith(".") else f".{target_ext}"

    new_name = (
        f"{header}_{basename[:max_char_orig]}{target_ext}"
        if not no_ext
        else f"{header}{basename[:max_char_orig]}"
    )
    renamed = fix_punct_spaces(new_name)

    return renamed.strip()


def move2completed(from_dir, filename, new_folder="completed", verbose=False):
    """
    move2completed moves a file from a directory to a new directory.

    Parameters
    ----------
    from_dir : str, the directory to move the file from
    filename : str, the name of the file to move
    new_folder : str, optional, the name of the new directory to move the file to, defaults to "completed"
    verbose : bool, optional, whether to print the file moved, defaults to False
    """

    # this is the better version
    old_filepath = join(from_dir, filename)

    new_filedirectory = join(from_dir, new_folder)

    if not os.path.isdir(new_filedirectory):
        os.mkdir(new_filedirectory)
        if verbose:
            print("created new directory for files at: \n", new_filedirectory)

    new_filepath = join(new_filedirectory, filename)

    try:
        shutil.move(old_filepath, new_filepath)
        print("successfully moved the file {} to */completed.".format(filename))
    except:
        print(
            "ERROR! unable to move file to \n{}. Please investigate".format(
                new_filepath
            )
        )


def digest_txt_directory(src_dir, identifer="", verbose=False, make_folder=False):
    """
    digest_txt_directory - merge all text files together in a given directory

    Parameters
    ----------
    src_dir : str
        the directory to digest
    identifer : str
        the identifier to use for the digest file
    verbose : bool
        if true, prints out the digest file name
    make_folder : bool
        if true, creates a folder for the digest file

    Returns
    -------
    digest_file : str
        the digest file name
    """

    digest_file = identifer + "_digest.txt"
    digest_file_path = join(src_dir, digest_file)

    if make_folder:
        digest_folder = identifer + "_digest"
        digest_folder_path = join(src_dir, digest_folder)
        if not os.path.isdir(digest_folder_path):
            os.mkdir(digest_folder_path)

    with open(digest_file_path, "w") as f:
        for filename in os.listdir(src_dir):
            if filename.endswith(".txt"):
                with open(join(src_dir, filename), "r") as f2:
                    f.write(f2.read())
                    f.write("\n\n")

    if verbose:
        print("created digest file at: \n", digest_file_path)

    return digest_file_path


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def create_kw_extractor(
    language="en",
    max_ngram_size=3,
    deduplication_algo="seqm",
    windowSize=10,
    numOfKeywords=10,
    ddpt=0.7,
):
    """
    creates a keyword extractor object

    :param language: language of the text
    :param max_ngram_size: max ngram size
    :param deduplication_algo: deduplication algorithm
    :param windowSize: window size
    :param numOfKeywords: number of keywords
    :param ddpt: Deduplication Percentage Threshold

    :return: keyword extractor object
    """
    assert ddpt >= 0 and ddpt <= 1, f"need 0<thresh<1, got {ddpt}"
    return yake.KeywordExtractor(
        lan=language,
        n=max_ngram_size,
        dedupLim=ddpt,
        dedupFunc=deduplication_algo,
        windowsSize=windowSize,
        top=numOfKeywords,
        features=None,
    )


def find_text_keywords(body_text: str, yake_ex=None, return_list=False, verbose=False):
    """
    find_text_keywords - find keywords in a text using YAKE

    Parameters
    ----------
    body_text : str, required, the text to find keywords in
    yake_ex : _type_, optional, keyword extractor object, default is None and will create a new one
    verbose : bool, optional, whether to print the keywords, default is False
    return_list : bool, optional, whether to return a list of keywords, default is False

    Returns
    -------
    keywords : str, the keywords found in the text as a string
    """
    yake_ex = yake_ex or create_kw_extractor()
    keywords = yake_ex.extract_keywords(body_text)
    kw_list = ["{} - {}".format(keywords.index(kw), kw[0]) for kw in keywords]
    if return_list:
        return kw_list
    kw_string = ", ".join(kw_list)
    if verbose:
        print(f"found {len(keywords)} keywords: \n{kw_string}")
    return kw_string


def print_api_info(verbose=False):
    """print_api_info - prints possible word2vec models to load for paragraph splitting"""

    model_info = api.info()["models"]

    labels = [m for m in model_info.keys()]
    print("Available word2vec models:")
    if verbose:
        pp.pprint(model_info)
        print("See https://github.com/RaRe-Technologies/gensim-data for more info")
    else:
        pp.pprint(labels)
