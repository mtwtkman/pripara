# -*- coding: utf-8 -*-
import re
import os
import json
from getpass import getpass


class ConfigNotFound(Exception):
    pass


class Config:
    file_name = 'conf.json'

    def __init__(self):
        self.email = None
        self.password = None

    def _read(self):
        try:
            with open(self.file_name) as fp:
                data = json.loads(fp.read())
        except FileNotFoundError:
            data = {
                'email': os.getenv('PRIPARA_EMAIL', None),
                'password': os.getenv('PRIPARA_PASSWORD', None),
            }
        self.password = data['password']
        self.email = data['email']

    def load(self):
        self._read()
        while not all([self.password, self.email]):
            print('You must create a information to login. Please input.')
            e = input('email >>> ')
            p = getpass('password >>> ')
            ok = input('ok?[y/N] >>> ')
            if ok != 'y':
                continue
            self.password = p
            self.email = e
            with open(self.file_name, 'w') as fp:
                fp.write(json.dumps({
                    'email': self.email,
                    'password': self.password,
                }))
            print('Created a config file named "conf.json" to this directory.')

    def as_dict(self):
        return {
            'email': self.email,
            'password': self.password,
        }
