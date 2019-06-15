import configparser
import os


class ConfigHelper:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.source_path = os.path.join(os.path.abspath(os.getcwd()), 'libparser')
        self.__section = ''

    def get_section_value(self, index, is_path=False):
        """
        :param index:
        :param is_path:
        :return:
        """
        if self.__section == '':
            raise ValueError('No config section provided')
        if index not in list(self.__section.keys()):
            raise ValueError('Index provided:"{0}" does not exist'.format(index))
        if is_path:
            return os.path.join(self.source_path, self.__section[index])
        return self.__section[index]

    def source(self, location: str):
        """

        :param location:
        :return:
        """
        self.config.read(os.path.join(self.source_path, 'config', location))

        return self

    def section(self, section: str):
        """
        :param section:
        :return:
        """
        if not self.config.has_section(section):
            raise ValueError('Current config file does not have a section:"{0}"'.format(section))
        self.__section = self.config[section]

        return self

    def file_exists(self, filepath:str)-> bool:
        """

        :param filepath:
        :return:
        """
        return os.path.isfile(filepath)

    def section_items(self)->dict:
        if not self.__section:
            raise ValueError('No section defined')
        return dict(self.__section.items())
