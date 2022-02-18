"""
This module contains the class PDF. It is used to generate a PDF report from a list of entries.
"""
import math
import urllib

import pandas as pd
from fpdf import FPDF, TitleStyle

from confectionary.report_generation import load_word2vec_model, split_to_pars
from confectionary.utils import find_text_keywords, fix_punct_spaces, get_timestamp


class PDF(FPDF):
    """
    PDF - instance of the class FPDF
    note, A4 dimensions in mm are: 210 wide x 297 long
    helpful doc: https://pyfpdf.github.io/fpdf2/ReferenceManual.html
    Parameters
    ----------
    FPDF : class, optional, default FPDF, the class FPDF
    """

    def __init__(
        self,
        orientation="P",
        unit="mm",
        format="A4",
        font_cache_dir=None,
        key_phrase="text2pdf",
        is_ewriter=False,
        split_paragraphs=True,
        bottom_margin=10,
    ):
        super().__init__(orientation, unit, format, font_cache_dir)
        self.key_phrase = key_phrase
        self.is_ewriter = is_ewriter
        self.split_paragraphs = split_paragraphs
        self.bottom_margin = bottom_margin
        self.initialized_word2vec = False
        self.wrdvecs = None

    def header(
        self, top_margin=10, header_text="", header_font_size=8, header_font_style="I"
    ):
        """
        header - add a header to the PDF

        Parameters
        ----------
        top_margin : int, optional, default 10, the top margin of the header
        header_text : str, optional, default "", the text to be displayed in the header
        header_font_size : int, optional, default 8, the font size of the header text
        header_font_style : str, optional, default "I", the font style of the header text
        """
        self.set_y(top_margin)  # set 1 CM from the top
        self.set_font("helvetica", header_font_style, header_font_size)
        th = self.font_size  # Text height

        self.cell(
            0,
            h=th,
            txt=f"{header_text} Created {get_timestamp()}",
            border="",
            ln=1,
            align="R",
            fill=False,
        )

        # add a rectangular border based on margins
        x_margin_L = self.l_margin
        x_margin_R = self.r_margin
        y_margin_T = self.t_margin
        y_margin_B = self.b_margin
        footer_location = th + self.bottom_margin  # where to end on bottom of page
        usable_x = self.w - x_margin_L - x_margin_R
        usable_y = self.h - footer_location - y_margin_T
        start_box = top_margin + th
        self.rect(x=x_margin_L, y=start_box, w=usable_x, h=usable_y, style="D")

    def footer(
        self, footer_text="", footer_font_size=8, footer_font_style="I", text_color=128
    ):
        """
        footer - add a footer to the PDF

        Parameters
        ----------
        footer_text : str, optional, default "", the text to be displayed in the footer
        footer_font_size : int, optional, default 8, the font size of the footer text
        footer_font_style : str, optional, default "I", the font style of the footer text
        text_color : int, optional, default 128, the color of the footer text
        """
        # Position at 1 cm from bottom
        self.set_y(-self.bottom_margin)  # Position at 1 cm from bottom
        # helvetica italic 8
        self.set_font("helvetica", footer_font_style, footer_font_size)
        # Text color in gray
        self.set_text_color(text_color)
        # Text height
        th = self.font_size

        # set link to TOC
        TOC_link = self.add_link()
        self.set_link(TOC_link, page=1)

        total_footer = f"{footer_text} - {self.key_phrase} - Page {self.page_no()}"
        self.cell(w=0, h=th, txt=total_footer, border=0, ln=0, link=TOC_link, align="R")

    def update_margins(self):
        """
        update_margins - update the margins of the PDF, based assigned margins
        """
        if self.is_ewriter:
            print("EWriter mode - setting margins large")

            # allocate margins
            pdf_width = self.w
            divided_space = math.floor(pdf_width / 3)
            divided_space = divided_space * 0.75  # take a lower %

            leftright_width = divided_space

            self.l_margin = leftright_width
            self.r_margin = leftright_width

            self.t_margin = 20
            self.b_margin = 20
        else:
            self.l_margin = 10
            self.r_margin = 10

            self.t_margin = 20
            self.b_margin = 20

    def update_title_formats(
        self,
        font_family="Helvetica",
        main_title_font_size=24,
        main_title_font_style="B",
        sub_title_font_size=20,
        sub_title_font_style="B",
        do_underline=False,
    ):
        """
        update_title_formats - update the title formats of the PDF, based assigned formats

        Parameters
        ----------
        font_family : str, optional, default "Helvetica", the font family of the title
        main_title_font_size : int, optional, default 24, the font size of the main title
        main_title_font_style : str, optional, default "B", the font style of the main title
        sub_title_font_size : int, optional, default 20, the font size of the sub title
        sub_title_font_style : str, optional, default "B", the font style of the sub title
        do_underline : bool, optional, default False, whether to underline the title
        """

        self.set_section_title_styles(
            # Level 0 titles:
            TitleStyle(
                font_family=font_family,
                font_style=main_title_font_style,
                font_size_pt=main_title_font_size,
                color=0,  # black
                underline=do_underline,
                t_margin=10,
                l_margin=10,
                b_margin=0,
            ),
            # Level 1 subtitles:
            TitleStyle(
                font_family=font_family,
                font_style=sub_title_font_style,
                font_size_pt=sub_title_font_size,
                color=128,
                underline=do_underline,
                t_margin=10,
                l_margin=20,
                b_margin=5,
            ),
        )

    def init_word2vec(self):
        """
        init_word2vec - initialize the word2vec model
        """
        if self.split_paragraphs and not self.initialized_word2vec:
            gensim_model = load_word2vec_model()
            self.wrdvecs = pd.DataFrame(
                gensim_model.vectors, index=gensim_model.key_to_index
            )
            self.initialized_word2vec = True

    def chapter_title(self, num: int, label: str):
        """
        chapter_title - add a chapter title to the PDF

        Parameters
        ----------
        num : int, the chapter number
        label : str, the chapter label
        """
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(200, 220, 255)
        th = self.font_size
        total_title = "Chapter " + str(num) + " - " + label
        self.start_section(total_title)
        self.ln(4)

    def chapter_body_filepath(self, filepath, verbose=False, std_font=14):
        """
        chapter_body_filepath - read in a file and add to the PDF as a chapter

        Parameters
        ----------
        filepath : str, filepath to the file to be added to the PDF
        verbose : bool, optional, by default False
        std_font : int, optional, by default 14
        """

        with open(filepath, "r", encoding="UTF-8", errors="ignore") as f:
            text = f.read()  # Read text file
        text = fix_punct_spaces(text)
        # Times for reading
        self.set_font("Times", "", std_font)
        # Text height. Add some millimeters for legibility
        th = self.font_size + 0.75

        enc_line = text.encode("latin-1", errors="replace")
        decoded_line = enc_line.decode("latin-1")
        if self.split_paragraphs:
            self.init_word2vec()
            paragraph_list = split_to_pars(
                decoded_line, wordvectors=self.wrdvecs, use_punkt=True
            )
            for par in paragraph_list:
                formatted_par = " " * 8 + par.strip()
                self.multi_cell(w=0, h=th, txt=formatted_par, border=0)
                self.ln()
        else:
            # "keep all text as one blob"

            self.multi_cell(w=0, h=th, txt=decoded_line, border=0)
            self.ln()

        if len(text) > 1500:
            # add keywords generated by YAKE
            self.generic_text(f"KeyWords:\n\t{find_text_keywords(text)}")
            self.ln()

        self.set_font("", "I")
        self.cell(0, th, "(end of excerpt)")

    def chapter_body_fromURL(self, aURL):
        """
        chapter_body_fromURL - read in a URL and add to the PDF as a chapter

        Parameters
        ----------
        aURL : str, the URL to be added to the PDF
        """

        session = urllib.request.urlopen(aURL)
        self.set_font("Times", "", 10)
        # Text height
        th = self.font_size

        for line in session:
            URL_line = line.decode("utf-8")
            enc_line = URL_line.encode("latin-1", errors="replace")
            decoded_line = enc_line.decode("latin-1")
        if self.split_paragraphs:
            self.init_word2vec()
            paragraph_list = split_to_pars(
                decoded_line, wordvectors=self.wrdvecs, use_punkt=True
            )
            for par in paragraph_list:
                formatted_par = " " * 8 + par
                self.multi_cell(w=0, h=th, txt=formatted_par, border=0)
                self.ln()
        else:
            # "keep all text as one blob"

            self.multi_cell(w=0, h=th, txt=decoded_line, border=0)
            self.ln()

        # Mention in italics
        self.set_font("", "I")
        self.cell(0, 5, "(end of excerpt)")

    def print_chapter(self, filepath, num: int, title: str = ""):
        """
        print_chapter is a wrapper for chapter_body that takes a filepath, title, and number, and prints the chapter

        :param fname: filepath to text file
        :param num: chapter number
        :param title: chapter title
        """
        self.add_page()
        self.chapter_title(num, title)
        self.chapter_body_filepath(filepath)

    def print_chapter_URL(self, theURL, num: int, title: str = ""):
        """
        print_chapter_URL is a wrapper for chapter_body that takes a URL, title, and number, and prints the chapter from the URL

        Parameters
        ----------
        theURL : str, URL
        num : int, chapter number, starting at 1
        title : str, optional, title of chapter
        """
        self.add_page()
        self.chapter_title(num, title)
        self.chapter_body_fromURL(theURL)

    def figure_title(self, title: str):
        # self.add_page()
        self.set_font("helvetica", "B", 14)
        # Text height
        th = self.font_size
        self.multi_cell(w=0, h=th, txt=title, border="B", ln=1, align="L", fill=False)
        # Line break
        self.ln()

    def write_big_title(self, a_title: str, font_size=24, font_style="B"):

        self.set_font("Helvetica", font_style, font_size)
        # Text height
        th = self.font_size
        self.multi_cell(w=0, h=th, txt=a_title, border="B", ln=1, align="C", fill=False)
        self.ln()

    def generic_text(self, the_text: str, the_size: int = 12):
        """
        generic_text is a wrapper for multi_cell that takes a string and font size, and prints it in the current page

        Parameters
        ----------
        the_text : str, required, the text to be printed
        the_size : int, optional, the font size to be used, default is 12
        """
        self.set_font("Times", "", int(the_size))

        # Text height
        th = self.font_size
        self.multi_cell(w=0, h=th, txt=the_text, ln=1, align="L")

    def comment_text(
        self, the_text: str, the_size: int = 12, preamble="**PLEASE NOTE:** "
    ):
        """
        comment_text is a wrapper for generic_text that adds a comment to the pdf.

        Parameters
        ----------
        the_text : str, the text to be added
        the_size : int, optional, the font size of the text. The default is 12.
        preamble : str, optional, the text to be added before the comment. The default is "**PLEASE NOTE:** ".
        """
        self.set_font("Courier", size=int(the_size), style="B")
        self.set_text_color(r=153, g=76, b=0)
        # Text height
        th = self.font_size
        my_text = preamble + the_text
        enc_line = my_text.encode("latin-1", errors="replace")
        decoded_line = enc_line.decode("latin-1")
        self.multi_cell(w=0, h=th, txt=decoded_line, ln=1, align="L")
        self.set_text_color(r=0, g=0, b=0)
