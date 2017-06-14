# -*- coding: utf-8 -*-
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

    def load(self):
        try:
            with open(self.file_name) as fp:
                conf = json.loads(fp.read())
        except FileNotFoundError:
            conf = {
                'email': os.getenv('PRIPARA_EMAIL', None),
                'password': os.getenv('PRIPARA_PASSWORD', None),
            }
        self.password = conf['password']
        self.email = conf['email']
        while not all([self.password, self.email]):
            print('You must create a information to login. Please input.')
            e = input('email >>>')
            p = getpass('password >>>')
            ok = input('ok?[y/N] >>>')
            if ok in ('no', 'N', 'No', 'NO'):
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
