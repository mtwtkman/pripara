# -*- coding: utf-8 -*-
import re
import os
import sys
import json
from getpass import getpass

import requests
from bs4 import BeautifulSoup


if sys.version_info.major != 3:
    print('This requires python3+')
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
                'password': None,
                'email': None,
            }
        self.password = os.getenv('PRIPARA_PASSWORD', conf['password'])
        self.email = os.getenv('PRIPARA_EMAIL', conf['email'])
        while not all([self.password, self.email]):
            print('You must create a information to login. Please input.')
            p = getpass('password >>>')
            e = input('email >>>')
            ok = input('ok?[y/N] >>>')
            if ok in ('no', 'N', 'No', 'NO'):
                continue
            self.password = p
            self.email = e
            print('Now created a config file named "conf.json" to this directory.')
            with open(self.file_name, 'w') as fp:
                fp.write(json.dumps({'password': self.password, 'email': self.email}))

    def as_dict(self):
        return {
            'password': self.password,
            'email': self.email,
        }


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

    def login(self):
        # NOTE: This never cache session. So this need to login every running.
        url = f'{HOST}/join/login'
        response = requests.post(url, data={
            'password': self.password,
            'mail_address': self.email,
        })
        if 'マイページへログイン' in response.text:
            raise LoginFailedError('You need to ensure the email and password are correct.')
        set_cookie = response.headers['Set-Cookie']
        self.session.update({
            'TTA_MGSID': re.search(r'TTA_MGSID=([a-z0-9]+)', set_cookie).group(1),
            'TTA_MGSID_AuthTicket': (r'TTA_MGSID_AuthTicket=([a-z0-9])', set_cookie).group(1),
        })
        print('login succeeded.')
