# -*- coding: utf-8 -*- import re
import re
from datetime import datetime


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
        ('closets', List),
    )
    field_names = [x[0] for x in fields]

    def __init__(self):
        self._data = None
        for field, T in self.fields:
            setattr(self, f'_{field}', T())

    def __str__(self):
        return f'<User: id={self.id} name={self.name}>'

    def __getattribute__(self, name):
        if name in object.__getattribute__(self, 'field_names'):
            return object.__getattribute__(self, f'_{name}').value
        return object.__getattribute__(self, name)

    @property
    def data(self):
        if not self._data:
            self._data = '\n'.join((
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
        return self._data

    def __call__(self):
        return self.data

    def initial(self, src):
        self._play_data_date.value = src.find('p', 'mypageDate').text.split('：')[1]
        self._name.value = re.match(r'(.+)\sさん.*', src.h2.text).group(1)
        self._teammate.value = src.find('a', 'btnD').find('strong').text
        self._id.value = src.find('dl', 'idolDataId').find('dd').text
        self._rank.value = src.find('dl', 'idolDataRank').find('dd').text
        self._like.value = src.find('dl', 'idolDataLike').dd.text
        self._weekly_ranking.value = src.find('dl', 'idolDataStateRanking').find('dd').text[:-1]
        self._weekly_total.value = src.find('dl', 'idolDataLikeWeekRanking').find('dd').text[:-1]
