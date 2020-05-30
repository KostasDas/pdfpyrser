import PyPDF2
from pdfpyrser.helpers.RegexMatchingHelper import RegexMatchingHelper


class PdfParser:

    def __init__(self):
        self.reader = None
        self.before_chapter = ''
        self.after_chapter = '\s\D.+?(\d{1,3})'
        self.matcher = RegexMatchingHelper()

    def from_location(self, file_path: str):
        """
        :param file_path:
        :return:
        """
        self.reader = PyPDF2.PdfFileReader(open(file_path, 'rb'))
        return self

    def __retrieve(self, page_start: int, page_end: int, rule='') -> list:
        """
        Retrieve data from pdf file
        :param page_end:
        :param page_start:
        :param rule: Rules to apply against columns
        :return:
        """
        self.__validate_pages(page_start, page_end)

        if page_start > page_end:
            page_start, page_end = self.__swap_pages(page_start, page_end)

        matches = (match(self.reader.getPage(i).extract_text(), rule) for i in range(page_start, page_end))
        return [item for sublist in matches for item in sublist]

    def __validate_pages(self, page_1: int, page_2: int):
        """
        Validate page values
        :param page_1:
        :param page_2:
        :return:
        """
        if page_1 < 0 or page_2 < 0:
            raise ValueError('Negative pages not accepted')
        if page_1 > self.reader.getNumPages() or page_2 > self.reader.getNumPages():
            raise IndexError('Page value larger than pdf\'s length')

    def __swap_pages(self, page_1, page_2) -> tuple:
        """
        :param page_1:
        :param page_2:
        :return:
        """
        return page_2, page_1

    def retrieve_from_pages(self, pages=None, rule='') -> list:
        """
        :param pages: list of tuple of pages
        :param rule:  string regex
        :return:
        """
        if not pages:
            yield self.__retrieve(0, self.reader.getNumPages(), rule)
        else:
            for tup in pages:
                yield self.__retrieve(tup[0], tup[1], rule)

    def retrieve_from_chapters(self, chapters: list, rule='', pages_to_look=None) -> list:
        """
        :param chapters: list of strings
        :param rule: regex
        :param pages_to_look: pages to look for chapters tuple
        :return:
        """
        for chapter in chapters:
            pages = self.__find_chapter_pages(chapter, pages_to_look)
            yield self.__retrieve(pages[0], pages[1], rule)

    def __find_chapter_pages(self, chapter: str, chapter_pages=None) -> tuple:
        """
        :param chapter:
        :param chapter_pages:
        :return:
        """
        if not chapter_pages:
            chapter_pages = (0, self.reader.getNumPages())
        next_chapter = int(chapter.split('.')[0]) + 1

        start = self.__retrieve(chapter_pages[0], chapter_pages[1], '\D' + chapter + self.after_chapter)
        end = self.__retrieve(chapter_pages[0], chapter_pages[1], '\D' + str(next_chapter) + self.after_chapter)

        if not start:
            start = self.__retrieve(chapter_pages[0], chapter_pages[1], chapter + self.after_chapter)
        if not end:
            end = self.__retrieve(chapter_pages[0], chapter_pages[1], str(next_chapter) + self.after_chapter)

        if not start or not end:
            raise IndexError('Chapter not found')

        start, end = int(start[0]), int(end[0])
        # -1 to the start page as index starts from 0 (page 1 is index 0)
        if start > 0:
            start -= 1
        return start, end

    def chapter_patterns(self, regex: str):
        """
        In case you need to overwrite the default chapter regex
        A chapter regex is what comes after the chapter number and before the page indicator
        :param regex:
        :return:
        """
        self.after_chapter = regex
