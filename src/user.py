# -*- coding: utf-8 -*-
import re

from bs4 import BeautifulSoup as bs

from .config import Config
from .client import Client
from .const import NOT_LOGGED_IN


class User:
    class Meta:
        def __init__(self):
            self.config = Config()
            self.config.load()
            self.client = Client(**self.config.as_dict())

    def __init__(self):
        self.meta = self.Meta()
        self.data = None
        self.name = None

    def __str__(self):
        if not self.meta.client.logged_in:
            return f'<User: {NOT_LOGGED_IN}>'
        return f'<User: You logged in as {self.name}.>'

    def _mapping(self, src):
        self.name = re.match(r'(.+)\sさん.*', src.h2.text).group(1)

    def login(self):
        response = self.meta.client.login()
        self._mapping(bs(response.text, 'html.parser'))
