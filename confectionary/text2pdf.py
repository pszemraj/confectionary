#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
text2pdf.py - a script to convert text files to pdf. iterates through a directory, loads each file, and converts it to ONE pdf.

python text2pdf.py -i /path/to/input/dir -o /path/to/output/dir will create one pdf from all txt files in the input directory and save it to the output directory. Add -r to load files recursively.

"""
import argparse
import os
import pprint as pp
from pathlib import Path

from tqdm.auto import tqdm

from confectionary.pdf import PDF
from confectionary.report_generation import estimate_TOC_pages, render_toc
from confectionary.utils import (
    cleantxt_wrap,
    get_seq2replace,
    get_timestamp,
    load_files_ext,
    simple_rename,
)


def str_to_pdf(
    text: str,
    output_dir=None,
    key_phrase: str = None,
    create_ewriter_notes=False,
    do_paragraph_splitting=True,
    nltk_usepunkt=True,
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
    do_paragraph_splitting : bool, optional, whether to split the text into paragraphs. Defaults to True.
    nltk_usepunkt : bool, optional, whether to use nltk punkt tokenizer. Defaults to True.
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
    pdf.set_author(os.getlogin())

    pdf.update_margins()  # update formatting
    pdf.update_title_formats()

    pdf.add_page()

    pdf.write_big_title(title)
    pdf.generic_text(text)
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


def file_to_pdf(
    filepath,
    output_dir=None,
    key_phrase: str = None,
    intro_text: str = None,
    create_ewriter_notes=False,
    do_paragraph_splitting=True,
    nltk_usepunkt=True,
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
    do_paragraph_splitting : bool, optional, whether to split the text into paragraphs. Defaults to True.
    nltk_usepunkt : bool, optional, whether to use nltk punkt tokenizer. Defaults to True.
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
    )
    title = f"{key_phrase}"
    pdf.set_title(title)
    pdf.set_author(os.getlogin())

    pdf.update_margins()  # update formatting
    pdf.update_title_formats()

    if intro_text is not None:
        pdf.add_page()
        pdf.comment_text(intro_text, preamble="")
    if be_verbose:
        print(f"attempting to print {src_path.name}")
    pdf.print_chapter(filepath=str(src_path.resolve()), num=1, title=key_phrase)
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
    key_phrase: str = None,
    intro_text: str = None,
    toc_comments: str = None,
    create_ewriter_notes=False,
    do_paragraph_splitting=True,
    nltk_usepunkt=True,
    be_verbose=False,
    recurse=False,
):
    """
    dir_to_pdf - converts all files in a directory 'input_dir' with extension 'extension' to a single pdf.

    Parameters
    ----------
    input_dir : str or pathlib.Path, the path to the directory containing the files to convert
    output_dir : str or pathlib.Path, optional, the path to the directory to write the output files to. Defaults to input_dir
    extension : str, optional, the extension of the files to convert. Defaults to '.txt'
    key_phrase : str, optional, the key phrase to identify the conversion instance. Defaults to None
    intro_text : str, optional, the text to be written at the top of the output file. Defaults to None
    toc_comments : str, optional, the text to be written at the bottom of the output file. Defaults to None
    create_ewriter_notes : bool, optional, whether to write the output to ewriter format (narrow text width). Defaults to False
    do_paragraph_splitting : bool, optional, whether to split the text into paragraphs. Defaults to True
    nltk_usepunkt : bool, optional, whether to use nltk punkt tokenizer. Defaults to True
    be_verbose : bool, optional, whether to print verbose output. Defaults to False
    recurse : bool, optional, whether to load files recursively from the input directory. Defaults to False

    Returns
    -------
    pathlib.Path, the path to the output file
    """

    src_dir = Path(input_dir)
    out_dir = Path(output_dir) if output_dir else src_dir.parent
    key_phrase = "Confectionary txt2pdf" if key_phrase is None else key_phrase

    out_subfolder = f"pdf_from_txt_{get_timestamp()}"
    out_p_full = out_dir / out_subfolder
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
    )
    title = f"{key_phrase}"
    pdf.set_title(title)
    pdf.set_author(os.getlogin())

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
        pdf.print_chapter(filepath=str(textfile.resolve()), num=i, title=out_name)
        pbar.update(1)
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
        required=True,
        type=str,
        help="path to directory containing input files",
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
        help="keywords identifying files to be processed",
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
        help="if set, will not split the text into paragraphs (faster)",
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
    input_dir = args.input_dir
    output_dir = args.output_dir
    key_phrase = args.keywords
    create_ewriter_notes = args.ewriter_notes
    do_paragraph_splitting = not args.no_split
    nltk_usepunkt = not args.no_punkt
    be_verbose = args.verbose
    recurse = args.recursive
    _finished_pdf_loc = dir_to_pdf(
        input_dir=input_dir,
        output_dir=output_dir,
        key_phrase=key_phrase,
        create_ewriter_notes=create_ewriter_notes,
        do_paragraph_splitting=do_paragraph_splitting,
        nltk_usepunkt=nltk_usepunkt,
        be_verbose=be_verbose,
        recurse=recurse,
    )

    print(f"\nPDF file written to {_finished_pdf_loc}")
