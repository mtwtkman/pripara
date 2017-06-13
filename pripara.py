# -*- coding: utf-8 -*-
import re
import os
import sys
import json
from getpass import getpass

import requests
from bs4 import BeautifulSoup as bs


v = sys.version_info
if v.major != 3 and v.minor < 6:
    print('This requires python3.6+')
    sys.exit(0)


class ConfigNotFound(Exception):
    pass


HOST = 'https://pripara.jp/'


class Config:
    file_name = 'conf.json'
    def __init__(self):
        self.password = None
        self.email = None

    def load(self):
        try:
            with open(self.file_name) as fp:
                conf = json.loads(fp.read())
        except FileNotFoundError:
            conf = {
                'password': os.getenv('PRIPARA_PASSWORD', None),
                'email': os.getenv('PRIPARA_EMAIL', None),
            }
        self.password = conf['password']
        self.email = conf['email']
        while not all([self.password, self.email]):
            print('You must create a information to login. Please input.')
            p = getpass('password >>>')
            e = input('email >>>')
            ok = input('ok?[y/N] >>>')
            if ok in ('no', 'N', 'No', 'NO'):
                continue
            self.password = p
            self.email = e
            with open(self.file_name, 'w') as fp:
                fp.write(json.dumps({'password': self.password, 'email': self.email}))
            print('Created a config file named "conf.json" to this directory.')

    def as_dict(self):
        return {
            'password': self.password,
            'email': self.email,
        }


class User:
    class Meta:
        def __init__(self):
            self.config = Config()
            self.config.load()
            self.client = Client(**self.config.as_dict())

    def __init__(self):
        self.meta = self.Meta()
        self.name = None

    def __str__(self):
        if not self.meta.client.logged_in:
            return '<User: You have not logged in yet.>'
        return '<User: You logged in as {}.>'.format(self.name)

    def _set_data(self):
        src = self.meta.src
        self.name = re.match(r'(.+)\sさん.*', src.h2.text).group(1)

    def login(self):
        response = self.meta.client.login()
        self._set_data(bs(response.text, 'html.parser'))


class LoginFailedError(Exception):
    pass


class Client:
    def __init__(self, password, email):
        self.password = password
        self.email = email
        self.session = {
            'TTA_MGSID': None,
            'TTA_MGSID_AuthTicket': None,
        }
        self._user = None
        self.logged_in = False

    def login(self):
        url = f'{HOST}/join/login'
        response = requests.post(url, data={
            'password': self.password,
            'mail_address': self.email,
        })
        if 'マイページへログイン' in response.text:
            raise LoginFailedError('You need to ensure the email and password are correct.')
        self.logged_in = True
        set_cookie = response.headers['Set-Cookie']
        self.session.update({
            'TTA_MGSID': re.search(r'TTA_MGSID=([a-z0-9]+)', set_cookie).group(1),
            'TTA_MGSID_AuthTicket': re.search(r'TTA_MGSID_AuthTicket=([a-z0-9]+)', set_cookie).group(1),
        })
        print('login succeeded.')
        return response


def pri():
    user = User()
    user.login()
