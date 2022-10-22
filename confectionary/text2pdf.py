#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
text2pdf.py - a script to convert text files to pdf. iterates through a directory, loads each file, and converts it to ONE pdf.

python text2pdf.py -i /path/to/input/dir -o /path/to/output/dir will create one pdf from all txt files in the input directory and save it to the output directory. Add -r to load files recursively.

"""
import sys
import argparse
import pprint as pp
from pathlib import Path

from tqdm.auto import tqdm

from confectionary.pdf import PDF
from confectionary.report_generation import (
    estimate_TOC_pages,
    render_toc,
)
from confectionary.utils import (
    cleantxt_wrap,
    get_seq2replace,
    get_timestamp,
    load_files_ext,
    simple_rename,
    get_user,
    print_api_info,
)


def str_to_pdf(
    text: str,
    output_dir=None,
    key_phrase: str = None,
    create_ewriter_notes=False,
    nltk_usepunkt=True,
    do_paragraph_splitting=True,
    word2vec_model="glove-wiki-gigaword-100",
    be_verbose=False,
):
    """
    str_to_pdf - the most basic version, creates a PDF with no table of contents with a string as input.

    Parameters
    ----------
    text : str, required, the text to be converted to PDF
    output_dir : str, optional, the directory to write the output PDF to. Defaults to None, which will write to the current working directory.
    key_phrase : str, optional, the key phrase to be used to identify the file. Defaults to None, which will use the timestamp.
    create_ewriter_notes : bool, optional, whether to create ewriter notes. Defaults to False.
    nltk_usepunkt : bool, optional, whether to use nltk punkt tokenizer. Defaults to True.
    do_paragraph_splitting : bool, optional, whether to split the text into paragraphs. Defaults to True.
    word2vec_model : str, optional, the word2vec model to use. Defaults to "glove-wiki-gigaword-100".
    be_verbose : bool, optional, whether to print verbose output. Defaults to False.

    Returns
    -------
    pathlib.Path, the path to the output PDF file.
    """
    output_dir = Path.cwd() if output_dir is None else Path(output_dir)
    key_phrase = (
        f"Confectionary text2pdf - {get_timestamp()}"
        if key_phrase is None
        else key_phrase
    )
    pdf = PDF(
        orientation="P",
        unit="mm",
        format="A4",
        is_ewriter=create_ewriter_notes,
        key_phrase=key_phrase,
        split_paragraphs=do_paragraph_splitting,
    )
    title = f"{key_phrase}"
    pdf.set_title(title)
    pdf.set_author(get_user())

    pdf.update_margins()  # update formatting
    pdf.update_title_formats()

    pdf.add_page()

    pdf.write_big_title(title)
    pdf.generic_text(
        text,
        split_paragraphs=do_paragraph_splitting,
        word2vec_model=word2vec_model,
        use_punkt=nltk_usepunkt,
    )

    doc_margin_type = "ewriter" if create_ewriter_notes else "standard"
    pdf_name = (
        f"{key_phrase}_txt2pdf_{get_timestamp(detailed=True)}_{doc_margin_type}.pdf"
    )
    pdf.output(output_dir / pdf_name)

    _out = output_dir / pdf_name
    if be_verbose:
        print(f"\nPDF file written to {_out}")
    return _out


def file_to_pdf(
    filepath,
    output_dir=None,
    key_phrase: str = None,
    intro_text: str = None,
    create_ewriter_notes=False,
    nltk_usepunkt=True,
    do_paragraph_splitting=True,
    word2vec_model="glove-wiki-gigaword-100",
    keywords_enabled=True,
    be_verbose=False,
):
    """
    file_to_pdf - create a pdf from a single text file.

    Parameters
    ----------
    filepath : str, required, the path to the file to be converted to PDF.
    output_dir : str, optional, the directory to write the output PDF to. Defaults to None, which will write to the current working directory.
    key_phrase : str, optional, the key phrase to be used to identify the file. Defaults to None, which will use the filename.
    intro_text : str, optional, the text to be added to the beginning of the file. Defaults to None, which will not add any text.
    create_ewriter_notes : bool, optional, whether to create ewriter notes. Defaults to False.
    nltk_usepunkt : bool, optional, whether to use nltk punkt tokenizer. Defaults to True.
    do_paragraph_splitting : bool, optional, whether to split the text into paragraphs. Defaults to True.
    word2vec_model : str, optional, the word2vec model to use. Defaults to "glove-wiki-gigaword-100".
    be_verbose : bool, optional, whether to print verbose output. Defaults to False.

    Returns
    -------
    pathlib.Path, the path to the output PDF file.
    """
    src_path = Path(filepath)
    output_dir = src_path.parent if output_dir is None else Path(output_dir)
    key_phrase = f"{src_path.stem} - text2pdf" if key_phrase is None else key_phrase
    pdf = PDF(
        orientation="P",
        unit="mm",
        format="A4",
        is_ewriter=create_ewriter_notes,
        key_phrase=key_phrase,
        split_paragraphs=do_paragraph_splitting,
        keywords_enabled=keywords_enabled,
    )
    title = f"{key_phrase}"
    pdf.set_title(title)
    pdf.set_author(get_user())

    pdf.update_margins()  # update formatting
    pdf.update_title_formats()

    if intro_text is not None:
        pdf.add_page()
        pdf.comment_text(intro_text, preamble="")
    if be_verbose:
        print(f"attempting to print {src_path.name}")
    pdf.print_chapter(
        filepath=str(src_path.resolve()),
        num=1,
        title=key_phrase,
        word2vec_model=word2vec_model,
        use_punkt=nltk_usepunkt,
    )
    # save the generated file
    doc_margin_type = "ewriter" if create_ewriter_notes else "standard"
    pdf_name = (
        f"{key_phrase}_txt2pdf_{get_timestamp(detailed=True)}_{doc_margin_type}.pdf"
    )
    pdf.output(output_dir / pdf_name)

    _out = output_dir / pdf_name
    if be_verbose:
        print(f"\nPDF file written to {_out}")
    return _out


def dir_to_pdf(
    input_dir,
    output_dir=None,
    extension: str = ".txt",
    recurse=False,
    key_phrase: str = None,
    intro_text: str = None,
    toc_comments: str = None,
    create_ewriter_notes=False,
    nltk_usepunkt=True,
    do_paragraph_splitting=True,
    word2vec_model="glove-wiki-gigaword-100",
    keywords_enabled=True,
    be_verbose=False,
):
    """
    dir_to_pdf - converts all files in a directory 'input_dir' with extension 'extension' to a single pdf.

    Parameters
    ----------
    input_dir : str or pathlib.Path, the path to the directory containing the files to convert into a single PDF.
    output_dir : str or pathlib.Path, optional, the path to the directory to write the output files to. Defaults to input_dir
    extension : str, optional, the extension of the files to convert when iterating through the directory. Defaults to ".txt".
    recurse : bool, optional, whether to load files recursively from the input directory. Defaults to False
    key_phrase : str, optional, the key phrase to identify the conversion instance. Defaults to None
    intro_text : str, optional, the text to be written at the top of the output file. Defaults to None
    toc_comments : str, optional, the text to be written at the bottom of the output file. Defaults to None
    create_ewriter_notes : bool, optional, whether to write the output to ewriter format (narrow text width). Defaults to False
    nltk_usepunkt : bool, optional, whether to use nltk punkt tokenizer. Defaults to True
    do_paragraph_splitting : bool, optional, whether to split the text into paragraphs. Defaults to True
    word2vec_model : str, optional, the word2vec model to use. Defaults to "glove-wiki-gigaword-100".
    be_verbose : bool, optional, whether to print verbose output. Defaults to False

    Returns
    -------
    pathlib.Path, the path to the output file
    """

    src_dir = Path(input_dir)
    out_dir = Path(output_dir) if output_dir else src_dir
    key_phrase = "Confectionary txt2pdf" if key_phrase is None else key_phrase

    out_p_full = out_dir / "text-to-PDF"
    out_p_full.mkdir(parents=True, exist_ok=True)

    approved_files = load_files_ext(
        src_dir, ext=extension, recursive=recurse, verbose=be_verbose
    )
    assert len(approved_files) > 0, "No files found in the input directory"
    if be_verbose:
        pp.pprint([f.name for f in approved_files])
    print(f"{len(approved_files)} files found matching extension {extension}")

    pdf = PDF(
        orientation="P",
        unit="mm",
        format="A4",
        is_ewriter=create_ewriter_notes,
        key_phrase=key_phrase,
        split_paragraphs=do_paragraph_splitting,
        keywords_enabled=keywords_enabled,
    )
    title = f"{key_phrase}"
    pdf.set_title(title)
    pdf.set_author(get_user())

    pdf.update_margins()  # update formatting
    pdf.update_title_formats()

    pdf.add_page()

    pdf.write_big_title(title)

    # write comments
    if intro_text is None:
        intro_text = f"The below text was loaded from a folder. \
        The files are sorted alphabetically. The fname of the parent folder is:\n\t{src_dir.name}"
    if toc_comments is None:
        toc_comments = """
        Click on chapters in the TOC to be linked there.
        Click on the page footer (bottom right on any page) to return to the TOC.
        """
    pdf.comment_text(cleantxt_wrap(intro_text), 10)
    pdf.ln(1)
    pdf.comment_text(toc_comments, 14)

    # add a table of contents
    toc_pages = estimate_TOC_pages(len(approved_files), verbose=True)
    pdf.insert_toc_placeholder(render_toc, pages=toc_pages)

    seq2replace = get_seq2replace()  # define words to replace in the chapter names

    if be_verbose:
        print("\nPrinting Chapters to PDF")
    pbar = tqdm(total=len(approved_files), desc="Building Chapters in PDF file")
    for i, textfile in enumerate(approved_files):
        out_name = simple_rename(textfile, max_char_orig=75, no_ext=True).lower()
        for ugly_w in seq2replace:
            out_name = out_name.replace(ugly_w, "")  # clean up filename
        out_name = out_name[0].upper() + out_name[1:]  # capitalize first letter
        if be_verbose:
            print(f"attempting chapter {i} - filename: {out_name}")
        pdf.print_chapter(
            filepath=str(textfile.resolve()),
            num=i,
            title=out_name,
            word2vec_model=word2vec_model,
            use_punkt=nltk_usepunkt,
        )
        pbar.update()
    pbar.close()

    if be_verbose:
        print("\nPrinting TOC to PDF")

    # save the generated file
    doc_margin_type = "ewriter" if create_ewriter_notes else "standard"
    pdf_name = f"{key_phrase}_txt2pdf_{get_timestamp()}_{doc_margin_type}.pdf"
    pdf.output(out_p_full / pdf_name)

    _out = out_p_full / pdf_name
    if be_verbose:
        print(f"\nPDF file written to {_out}")
    return _out


def get_parser():
    """
    get_parser - a helper function for the argparse module
    """
    parser = argparse.ArgumentParser(description="Spell correct and create PDF")
    parser.add_argument(
        "-i",
        "--input-dir",
        required=False,
        default=None,
        type=str,
        help="path to directory containing input files. Required if not using the --api-info flag",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        required=False,
        default=None,
        type=str,
        help="path to directory to write output files (new folder created). Defaults to input-dir",
    )
    parser.add_argument(
        "-kw",
        "--keywords",
        required=False,
        default=None,
        type=str,
        help="some key words or phrases to help identify the output file",
    )
    parser.add_argument(
        "-e",
        "--ewriter-notes",
        required=False,
        default=False,
        action="store_true",
        help="if set, will write the output to ewriter format (narrow text width)",
    )
    parser.add_argument(
        "--no-split",
        required=False,
        default=False,
        action="store_true",
        help="if set, will not split the text into paragraphs (faster, less readable)",
    )
    parser.add_argument(
        "-m",
        "--model",
        required=False,
        default="glove-wiki-gigaword-100",
        type=str,
        help="the word2vec model to use",
    )
    parser.add_argument(
        "--no-punkt",
        required=False,
        default=False,
        action="store_true",
        help="if set, will not use nltk punkt tokenizer",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        required=False,
        default=False,
        action="store_true",
        help="whether to load files recursively from the input directory",
    )
    parser.add_argument(
        "--no-keywords",
        default=False,
        action="store_true",
        help="if set, will not add keywords to the PDF",
    )
    parser.add_argument(
        "--api-info",
        required=False,
        default=False,
        action="store_true",
        help="print the available word2vec models in the gensim API and exit",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        required=False,
        default=False,
        action="store_true",
        help="whether to print verbose output",
    )

    return parser


if __name__ == "__main__":

    args = get_parser().parse_args()
    be_verbose = args.verbose

    if args.api_info:
        print_api_info(verbose=be_verbose)
        sys.exit("Exiting...")
    if args.input_dir is None:
        sys.exit(
            "No input directory specified. Pass an input directory with the -i flag."
        )
    input_dir = args.input_dir
    output_dir = args.output_dir
    key_phrase = args.keywords
    create_ewriter_notes = args.ewriter_notes
    do_paragraph_splitting = not args.no_split
    word2vec_model = args.model
    nltk_usepunkt = not args.no_punkt
    recurse = args.recursive
    keywords_enabled = not args.no_keywords
    _finished_pdf_loc = dir_to_pdf(
        input_dir=input_dir,
        output_dir=output_dir,
        key_phrase=key_phrase,
        create_ewriter_notes=create_ewriter_notes,
        do_paragraph_splitting=do_paragraph_splitting,
        word2vec_model=word2vec_model,
        nltk_usepunkt=nltk_usepunkt,
        be_verbose=be_verbose,
        recurse=recurse,
        keywords_enabled=keywords_enabled,
    )

    print(f"\nPDF file written to {_finished_pdf_loc}")
