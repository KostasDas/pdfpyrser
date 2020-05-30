from PyPDF2 import utils
from PyPDF2.pdf import ContentStream, TextStringObject
import PyPDF2

CONST_BOLD = "bold"
CONST_UNDERLINE = "underline"
CONST_ITALICS = "italic"


class PyPage:
    def __init__(self, page: int, reader: PyPDF2.PdfFileReader):
        self.pageObject = reader.getPage(page)
        self.fonts = reader.flattenedPages[page]['/Resources']['/Font']

    def is_bold(self, blocks: list, included=True) -> list:
        """
        Include only bold fonts
        :param included: if we should return bold or exclude bold
        :param blocks:
        :return:
        """

        return self.__filter_blocks(blocks, self.__get_font_settings(CONST_BOLD), included)

    def is_not_bold(self, blocks: list)-> list:
        """
        Exclude bold fonts
        :param blocks:
        :return:
        """
        return self.is_bold(blocks, False)

    def is_italic(self, blocks: list, included=True) -> list:
        """
        Include only italic fonts
        :param blocks:
        :param included:
        :return:
        """
        return self.__filter_blocks(blocks, self.__get_font_settings(CONST_ITALICS), included)

    def is_not_italic(self, blocks: list) -> list:
        """

        :param blocks:
        :return:
        """
        return self.is_italic(blocks, False)

    def is_underline(self, blocks: list, included=True) -> list:
        """
        Include only italic fonts
        :param blocks:
        :param included:
        :return:
        """
        return self.__filter_blocks(blocks, self.__get_font_settings(CONST_UNDERLINE), included)

    def is_not_underline(self, blocks: list) -> list:
        """

        :param blocks:
        :return:
        """
        return self.is_underline(blocks, False)

    def __get_font_settings(self, constant_option: str) -> list:
        """

        :param constant_option:
        :return:
        """
        font_settings = []
        for font_name in self.fonts:
            page_font_settings = self.fonts[font_name]
            if constant_option in page_font_settings[utils.u_('/BaseFont')].lower():
                font_settings.append(utils.u_(font_name))

        return font_settings

    def __filter_blocks(self, blocks: list, options: list, included: bool) -> list:
        """
        Filters blocks of text against a list of options and returns a string
        e.g. a bold font that matches.
        :param blocks: the list of text with its formatting options
        :param options: the options to compare against
        :param included: if we want to include or exclude the text.
        :return:
        """
        desired_blocks = []
        for block in blocks:
            matches = False
            for operands, operator in block:
                if operator == utils.b_("Tf"):
                    if included:
                        matches = operands[0] in options
                    if not included:
                        matches = operands[0] not in options
                    break
            if matches:
                desired_blocks.append(self.__extract(block))

        return desired_blocks

    def extract_text_blocks(self) -> list:
        """
        Every text block in pdf begins with BT (Begin text) and ends with ET (end text)
        Get what is in between and return it.
        :return:
        """
        text = []
        content = self.pageObject["/Contents"].getObject()
        if not isinstance(content, ContentStream):
            content = ContentStream(content, self.pageObject.pdf)
        start, end = 0, 0
        for index, (operands, operator) in enumerate(content.operations):
            if operator == utils.b_("BT"):
                start = index
            if operator == utils.b_("ET"):
                end = index
            if start != 0 and end != 0:
                text.append(content.operations[start + 1:end])
                start, end = 0, 0

        return text

    def __extract(self, page: list)-> str:
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
