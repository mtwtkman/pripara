# -*- coding: utf-8 -*-
import os
import json
from getpass import getpass


class ConfigNotFound(Exception):
    pass


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
                fp.write(json.dumps({
                    'password': self.password,
                    'email': self.email
                }))
            print('Created a config file named "conf.json" to this directory.')

    def as_dict(self):
        return {
            'password': self.password,
            'email': self.email,
        }
