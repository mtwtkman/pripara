# -*- coding: utf-8 -*- import re
import re
from datetime import datetime

from .client import Client, NOT_LOGGED_IN
from .config import Config


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
    _type = (int, str)
    default = 0
    allow_none = False

    def _clean(self, value):
        if isinstance(value, str):
            if not value.isdigit():
                raise TypeError
            value = int(value)
        return value


class List(Field):
    _type = list

    def _clean(self, value):
        return value


class User:
    fields = (
        ('play_data_date', Datetime),
        ('name', Str),
        ('teammate', Int),
        ('id', Int),
        ('rank', Str),
        ('like', Int),
        ('weekly_ranking', Int),
        ('weekly_total', Int),
    )
    field_names = [x[0] for x in fields]

    def __init__(self):
        self._info = None
        config = Config()
        config.load()
        self.client = Client(**config.as_dict())
        for field, T in self.fields:
            setattr(self, f'_{field}', T())

    def __str__(self):
        return f'<User: id={self.id} name={self.name}>'

    def __getattribute__(self, name):
        if name in object.__getattribute__(self, 'field_names'):
            return object.__getattribute__(self, f'_{name}').value
        return object.__getattribute__(self, name)

    def login(self):
        response = self.client.login()
        for k, v in response.items():
            getattr(self, f'_{k}').value = v
        print(f'Logged in as {self.name}')

    def logout(self):
        self.client.logout()
        print('bye bye.')

    def as_dict(self):
        return {f: getattr(self, f) for f in self.field_names}

    @property
    def info(self):
        if not self.client.logged_in:
            print(NOT_LOGGED_IN)
            return
        elif not self._info:
            self._info = '\n'.join((
                'User data',
                f'-- As of {self.play_data_date.strftime("%Y/%m/%d")} --',
                f'id:\t{self.id}',
                f'name:\t{self.name}',
                f'teammate:\t{self.teammate}',
                f'rank:\t{self.rank}',
                f'like:\t{self.like}',
                f'weekly ranking:\t{self.weekly_ranking}',
                f'weekly total:\t{self.weekly_total}'
            ))
        print(self._info)
