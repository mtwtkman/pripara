# -*- coding: utf-8 -*-
import re
import requests

from .const import NOT_LOGGED_IN


HOST = 'https://pripara.jp/'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'


class AbnormalResponse(Exception):
    pass


class LoginFailedError(Exception):
    pass


def require_login(method):
    def wrapper(self, *args, **kwargs):
        if not self.logged_in:
            print(NOT_LOGGED_IN)
            return
        return method(self, *args, **kwargs)
    return wrapper


def valid_response(method):
    def wrapper(self, *args, **kwargs):
        response = method(self, *args, **kwargs)
        code = response.status_code
        if code != 200:
            raise AbnormalResponse(f'status code: {code}')
        return response
    return wrapper


class Client:
    headers = {'user-agent': UA}

    def __init__(self, password, email):
        self.password = password
        self.email = email
        self.session = {
            'TTA_MGSID': None,
            'TTA_MGSID_AuthTicket': None,
        }
        self._user = None
        self.logged_in = False

    @valid_response
    def get(self, params=None):
        return requests.get(self.url, params=params, headers=self.headers)

    @valid_response
    def post(self, data=None):
        return requests.post(self.url, data=data, headers=self.headers)

    def login(self):
        self.url = f'{HOST}join/login'
        response = self.post({
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

    @require_login
    def logout(self):
        self.url = f'{HOST}join/logout'
        return self.get()

    @require_login
    def team(self):
        self.url = f'{HOST}mypage/team'
        return self.get()
