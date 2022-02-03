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

from pdf import PDF
from report_generation import render_toc, estimate_TOC_pages
from utils import beautify_filename, cleantxt_wrap, get_timestamp, load_files_ext


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
        help="path to file containing keywords to be used for spell correction",
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
    src_dir = Path(args.input_dir)
    key_phrase = args.keywords
    key_phrase = src_dir.name if key_phrase is None else key_phrase

    out_dir = Path(args.output_dir) if args.output_dir else src_dir.parent
    out_subfolder = f"pdf_from_txt_{get_timestamp()}"
    out_p_full = out_dir / out_subfolder
    out_p_full.mkdir(parents=True, exist_ok=True)

    create_ewriter_notes = args.ewriter_notes
    do_paragraph_splitting = not args.no_split
    nltk_usepunkt = not args.no_punkt
    be_verbose = args.verbose
    recurse = args.recursive

    approved_files = load_files_ext(src_dir, ext="txt", recursive=recurse)
    assert len(approved_files) > 0, "No files found in the input directory"
    if be_verbose:
        pp.pprint([f.stem for f in approved_files])
    print(f"{len(approved_files)} files found matching extension .txt")

    # create pdf object
    pdf = PDF(
        orientation="P",
        unit="mm",
        format="A4",
        is_ewriter=create_ewriter_notes,
        key_phrase=key_phrase,
        split_paragraphs=do_paragraph_splitting,
    )
    title = f"{key_phrase} - txt2pdf"
    pdf.set_title(title)
    pdf.set_author(os.getlogin())

    # update formatting
    pdf.update_margins()
    pdf.update_title_formats()

    pdf.add_page()

    # set title
    pdf.write_big_title(title)

    # write comment
    intro_text = f"The below text was loaded from a folder. \
    The files are sorted alphabetically. The fname of the folder is:\n\t{src_dir.name}"
    pdf.comment_text(cleantxt_wrap(intro_text), 10)
    pdf.ln(1)
    toc_comment = """
    Click on chapters in the TOC to be linked there.
    Click on the page footer (bottom right on any page) to return to the TOC.
    """
    pdf.comment_text(toc_comment, 14)

    # add a table of contents
    toc_pages = estimate_TOC_pages(len(approved_files), verbose=True)
    pdf.insert_toc_placeholder(render_toc, pages=toc_pages)

    # define words to replace in the chapter names
    seq2replace = ["fin", "pegasus", "phone", "con", "-v-", "---", "sum"]

    if be_verbose:
        print("\nPrinting Chapters to PDF")
    pbar = tqdm(total=len(approved_files), desc="Building Chapters in PDF file")
    for i, textfile in enumerate(approved_files):
        out_name = beautify_filename(
            textfile.name,
            num_words=30,
        )
        for ugly_w in seq2replace:
            out_name = out_name.replace(ugly_w, "")  # clean up filename
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
    print(f"\nPDF file saved to {_out}")
