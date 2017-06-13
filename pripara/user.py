# -*- coding: utf-8 -*- import re
import re
from datetime import datetime

from bs4 import BeautifulSoup as bs


class RequiredDataTypeError(Exception):
    pass


class Field:
    _type = None
    default = None
    allow_none = True

    def __init__(self, value=None):
        value = value or self.default
        self.value = self._clean(value)

    def _clean(self, value):
        raise NotImplementedError

    def __setattr__(self, name, value):
        if not (isinstance(value, self._type) or self.allow_none):
            raise TypeError
        object.__setattr__(self, name, self._clean(value))


class Datetime(Field):
    _type = datetime

    def _clean(self, value):
        if value is None:
            return None
        return datetime.strptime(value, '%Y年%m月%d日')


class Str(Field):
    _type = str
    default = ''
    allow_none = False

    def _clean(self, value):
        return value.strip()


class Int(Field):
    _type = int
    default = 0
    allow_none = False

    def _clean(self, value):
        return value


class User:
    fields = ('splay_data_date', 'name', 'teammate')

    def __init__(self):
        self._soup = {}
        self.play_data_date = Datetime()
        self.name = Str()
        self.teammate = Int()

    def __getattr__(self, name):
        if name not in self.__dict__:
            raise AttributeError
        if name in fields:
            return self.__dict__[name].value
        return self.__dict__[name]

    def bs(self, name, src):
        if name not in self.soup:
            self._soup[name] = bs(src, 'html.parser')
        self.name(re.match(r'(.+)\sさん.*', src.h2.text).group(1))
