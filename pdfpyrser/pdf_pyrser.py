import PyPDF2
from PyPDF2 import utils
from PyPDF2.pdf import PageObject, ContentStream, TextStringObject

from pdfpyrser.helpers import regex_matching_helper


class PdfPyrser:

    def __init__(self):
        self.matcher = regex_matching_helper.match
        self.reader = None
        self.page_start = 0
        self.page_end = 0

    def read(self, source: str):
        """
        :param source:
        :return:
        """
        self.reader = PyPDF2.PdfFileReader(source)
        self.page_end = self.reader.getNumPages()
        blocks = self.extractTextBlocks(self.reader.getPage(0))
        text = self.extractTextFromBlocks(blocks, ["isBold"])

    def from_pages(self, pages: tuple):
        """

        :param pages:
        :return:
        """
        self.__validate_pages(pages)
        self.page_start, self.page_end = pages[0], pages[1]
        if self.page_start > self.page_end:
            self.page_start, self.page_end = pages[1], pages[0]

        return self

    def fetch(self, pattern='') -> list:
        """
        Use a regex pattern to search the pdf pages
        :param pattern: regex rule
        :return:
        """
        matches = (self.matcher(self.reader.getPage(i).extractText(), pattern) for i in
                   range(self.page_start, self.page_end))
        return [item for sublist in matches for item in sublist]

    def fetch_paragraphs(self):
        pass

    def fetch_sentences(self):
        pass

    def __validate_pages(self, pages: tuple):
        if pages[0] < 0 or pages[1] < 0:
            raise ValueError('Negative pages not accepted')
        if pages[0] > self.reader.getNumPages() or pages[1] > self.reader.getNumPages():
            raise IndexError('Page value larger than pdf\'s length')

    def isBold(self, operator: bytes, operands: list):
        """
           Locate all text drawing commands, in the order they are provided in the
           content stream, and extract the text.  This works well for some PDF
           files, but poorly for others, depending on the generator used.  This will
           be refined in the future.  Do not rely on the order of text coming out of
           this function, as it will change if this function is made more
           sophisticated.
           operators (Tj, TJ etc) can be found in page 196 of PDF Reference
           :return: a unicode string object.
        """

        if operator == utils.b_("Tf"):
            return operands[0] == utils.u_("/F4")
        return True

    def extractTextBlocks(self, page: PageObject) -> list:
        content = page["/Contents"].getObject()
        if not isinstance(content, ContentStream):
            content = ContentStream(content, page.pdf)
        start = 0
        end = 0
        blocks = []
        for index, (operands, operator) in enumerate(content.operations):
            if operator == utils.b_("BT"):
                start = index
            if operator == utils.b_("ET"):
                end = index
            if start != 0 and end != 0:
                blocks.append(content.operations[start+1:end])
                start, end = 0, 0
        return blocks


    def extractTextFromBlocks(self, blocks: list, filters: list):
        text = []
        for block in blocks:
            text.append(self.extract(block))
        return text

    def extract(self, page: list):
        """
       Locate all text drawing commands, in the order they are provided in the
       content stream, and extract the text.  This works well for some PDF
       files, but poorly for others, depending on the generator used.  This will
       be refined in the future.  Do not rely on the order of text coming out of
       this function, as it will change if this function is made more
       sophisticated.
       operators (Tj, TJ etc) can be found in page 196 of PDF Reference
       :return: a unicode string object.
       """
        text = utils.u_("")
        # Note: we check all strings are TextStringObjects.  ByteStringObjects
        # are strings where the byte->string encoding was unknown, so adding
        # them to the text here would be gibberish.
        for operands, operator in page:
            if operator == utils.b_("Tj"):
                _text = operands[0]
                if isinstance(_text, TextStringObject):
                    text += _text
            elif operator == utils.b_("T*"):
                text += "\n"
            elif operator == utils.b_("'"):
                text += "\n"
                _text = operands[0]
                if isinstance(_text, TextStringObject):
                    text += operands[0]
            elif operator == utils.b_('"'):
                _text = operands[2]
                if isinstance(_text, TextStringObject):
                    text += "\n"
                    text += _text
            elif operator == utils.b_("TJ"):
                for i in operands[0]:
                    if isinstance(i, TextStringObject):
                        text += i
                text += "\n"
        return text
