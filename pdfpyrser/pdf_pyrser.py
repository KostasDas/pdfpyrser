import PyPDF2

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
