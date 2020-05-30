import PyPDF2
from pdfpyrser.helpers import RegexMatchingHelper
from pdfpyrser.PyPage import PyPage


class PdfPyrser:

    def __init__(self):
        self.matcher = RegexMatchingHelper.match
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

    def extract_text(self, callables: list) -> list:
        """
        TODO: Text has a list entry for every callable. and a group of entries per page. let's say 2 pages with 2 callables is 2*2 = 4 lists.
        TODO: You have to intersect the lists of every page to find the common ground for the callables. also your italics isn't working
        :param callables:
        :return:
        """
        text = []

        for x in range(self.page_start, self.page_end+1):
            page_text = []
            current_page = PyPage(x, self.reader)
            blocks = current_page.extract_text_blocks()
            for call in callables:
                page_text.append(getattr(current_page, call)(blocks))
            text.append("".join(set(page_text[0]).intersection(*page_text[1:])))
        return text

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
        matches = (self.matcher(self.reader.getPage(i).extract_text(), pattern) for i in
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
