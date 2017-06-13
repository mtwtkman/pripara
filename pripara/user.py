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
    fields = [
        ('play_data_date', Datetime),
        ('name', Str),
        ('teammate', Int),
    ]
    field_names = [x[0] for x in fields]

    def __init__(self):
        self._soup = {}
        for field, T in self.fields:
            self.__dict__[field] = T()

    def __getattr__(self, name):
        if name in self.field_names:
            return self.__dict__.get(name).value
        if not hasattr(self, name):
            raise AttributeError
        return self.__dict__.get(name)

    def __setattr__(self, name, value):
        if name in self.field_names:
            field = getattr(self, name)
            field.value = value
        else:
            object.__setattr__(self, name, value)

    def bs(self, name, src):
        if name not in self.soup:
            self._soup[name] = bs(src, 'html.parser')
        self.name(re.match(r'(.+)\sさん.*', src.h2.text).group(1))
