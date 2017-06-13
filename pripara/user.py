# -*- coding: utf-8 -*- import re
import re
from datetime import datetime

from bs4 import BeautifulSoup as bs


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
    fields = (
        'play_data_date', 'name', 'teammate',
        'id', 'rank', 'like', 'weekly_ranking',
        'weekly_total'
    )

    def __init__(self):
        self._play_data_date = Datetime()
        self._name = Str()
        self._teammate = Int()
        self._id = Int()
        self._rank = Str()
        self._like = Int()
        self._weekly_ranking = Int()
        self._weekly_total = Int()

    def __str__(self):
        return f'<User: id={self.id} name={self.name}'

    def __getattribute__(self, name):
        if name in object.__getattribute__(self, 'fields'):
            return object.__getattribute__(self, f'_{name}').value
        return object.__getattribute__(self, name)

    def data(self):
        return '\n'.join((
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

    def initial(self, src):
        soup = bs(src, 'html.parser')
        self._play_data_date.value = soup.find('p', 'mypageDate').text.split('：')[1]
        self._name.value = re.match(r'(.+)\sさん.*', soup.h2.text).group(1)
        self._teammate.value = int(soup.find('a', 'btnD').find('strong').text)
        self._id.value = int(soup.find('dl', 'idolDataId').find('dd').text)
        self._rank.value = soup.find('dl', 'idolDataRank').find('dd').text
        self._like.value = int(soup.find('dl', 'idolDataLike').dd.text)
        self._weekly_ranking.value = int(soup.find('dl', 'idolDataStateRanking').find('dd').text[:-1])
        self._weekly_total.value = int(soup.find('dl', 'idolDataLikeWeekRanking').find('dd').text[:-1])
