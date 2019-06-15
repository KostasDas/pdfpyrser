import re


class RegexMatchingHelper:

    def matches(self, target, search_query):
        """
        Uses a regex to match the header title with the desired title
        :param target: The title to compare against
        :param search_query: The field to compare with
        :return: Boolean
        """
        title_regex = re.compile(search_query, re.IGNORECASE)
        res = title_regex.search(str(target))
        return res is not None

    def replace(self, target, replace_that, replace_that_with):
        """

        :param target:
        :param replace_that:
        :param replace_that_with:
        :return:
        """
        regex = re.compile(replace_that, re.IGNORECASE)
        return regex.sub(replace_that_with, target)

    def match(self, target, search_query):
        """
        Uses a regex to match the header title with the desired title
        :param target: The title to compare against
        :param search_query: The field to compare with
        :return: Boolean
        """
        matching_regex = re.compile(search_query, re.IGNORECASE | re.DOTALL)
        return matching_regex.findall(str(target))

    def group_match(self, target, search_query):
        """
        Uses a regex to match the header title with the desired title
        :param target: The title to compare against
        :param search_query: The field to compare with
        :return: Boolean
        """
        matching_regex = re.compile(search_query, re.IGNORECASE | re.DOTALL)
        return matching_regex.search(str(target)).groups()
