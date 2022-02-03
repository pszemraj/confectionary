"""
This file contains utility functions for the project.
"""

import os
import random
import re
import shutil
import warnings
from datetime import datetime
from os.path import isfile, join
from pathlib import Path

import wordninja
import yake
from cleantext import clean
from natsort import natsorted


def get_first_number(my_string):
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


def fix_punct_spaces(string):
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
    return string.strip()


def dict_sort_by_keys(d):
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


def load_files_ext(target_dir, ext, recursive=False):
    """
    Loads all files with a specific extension from a given path.
    :param path: Path to the files.
    :param ext: Extension of the files.
    :param recursive: If True, the function will recursively search for files.

    :return: List of files, sorted by the first number found in the filename.
    """
    target_dir = Path(target_dir)
    files = []
    if recursive:
        for file in target_dir.glob("**/*." + ext):
            files.append(file)
    else:
        for file in target_dir.glob("*." + ext):
            files.append(file)
    ids = [get_first_number(file.name) for file in files]
    my_dict = dict(zip(ids, files))
    sorted_dict = dict_sort_by_keys(my_dict)
    return sorted_dict.values()


def get_timestamp(detailed=False):
    if detailed:
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    else:
        return datetime.now().strftime("%b-%d-%Y")


def create_folder(directory):
    os.makedirs(directory, exist_ok=True)


def corr(s):
    # adds space after period if there isn't one
    # removes extra spaces
    return re.sub(r"\.(?! )", ". ", re.sub(r" +", " ", s))


def cleantxt_wrap(ugly_text):
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
    # takes a filename stored as text, removes extension, separates into X words ...
    # and returns a nice filename with the words separateed by
    # useful for when you are reading files, doing things to them, and making new files

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


def move2completed(from_dir, filename, new_folder="completed", verbose=False):

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
    ddpt=0.9,
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


def find_text_keywords(body_text: str, yake_ex=None, verbose=False):
    """
    find_text_keywords - return kw from free text
    """
    yake_ex = yake_ex or create_kw_extractor()
    keywords = yake_ex.extract_keywords(body_text)
    kw_list = ["{} - {}".format(keywords.index(kw), kw[0]) for kw in keywords]
    kw_string = ", ".join(kw_list)
    if verbose:
        print(f"found {len(keywords)} keywords: \n{kw_string}")
    return kw_string
