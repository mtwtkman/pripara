# -*- coding: utf-8 -*-
import re

import requests
from bs4 import BeautifulSoup as bs


HOST = 'https://pripara.jp'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
NOT_LOGGED_IN = 'You have not logged in yet.'


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
        if code >= 400:
            raise AbnormalResponse(f'status code: {code}')
        return response
    return wrapper


class Client:
    headers = {'user-agent': UA}

    def __str__(self):
        if not self.logged_in:
            return f'<Client: {NOT_LOGGED_IN}>'
        return f'<Client: You logged in as {self.username}.>'

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.username = None
        self.cookies = {
            'TTA_MGSID': None,
            'TTA_MGSID_AuthTicket': None,
        }
        self.logged_in = False

    @valid_response
    def get(self, url, params=None):
        return requests.get(
            url,
            params=params,
            headers=self.headers,
            cookies=self.cookies
        )

    @valid_response
    def post(self, url, data=None):
        return requests.post(
            url,
            data=data,
            headers=self.headers
        )

    def login(self):
        response = self.post(
            f'{HOST}/join/login',
            {
                'password': self.password,
                'mail_address': self.email,
            }
        )
        if 'マイページへログイン' in response.text:
            raise LoginFailedError('You need to ensure the email and password are correct.')
        self.logged_in = True
        set_cookie = response.headers['Set-Cookie']
        self.cookies.update({
            'TTA_MGSID': re.search(r'TTA_MGSID=([a-z0-9]+)', set_cookie).group(1),
            'TTA_MGSID_AuthTicket': re.search(r'TTA_MGSID_AuthTicket=([a-z0-9]+)', set_cookie).group(1),
        })
        src = bs(response.text, 'html.parser')
        self._closet(src)
        self.username = re.match(r'(.+)\sさん.*', src.h2.text).group(1)
        return {
            'play_data_date': src.find('p', 'mypageDate').text.split('：')[1],
            'name': self.username,
            'teammate': src.find('a', 'btnD').find('strong').text,
            'id': src.find('dl', 'idolDataId').find('dd').text,
            'rank': src.find('dl', 'idolDataRank').find('dd').text,
            'like': src.find('dl', 'idolDataLike').dd.text,
            'weekly_ranking': src.find('dl', 'idolDataStateRanking').find('dd').text[:-1],
            'weekly_total': src.find('dl', 'idolDataLikeWeekRanking').find('dd').text[:-1],
        }

    def _closet_method_factory(self, closet):
        def fetch(self):
            response = self.get(f'{HOST}{c["href"]}')
            closet['fetched'] = True
            src = list(bs(response.text, 'html.parser').find('p', 'charText').children)[2:]
            name, count = src[0].text.split('：')
            return {
                'name': re.match(r'^★(.+)(?=のアイテム数$)', name).group(1),
                'count': int(count),
                'total': int(src[1]),
            }
        return fetch

    def _closet(self, src):
        self.closets = []
        for x in src.find_all('li', re.compile(r'no\d{6}')):
            c = {'href': x.a['href'], 'title': x.a.text, 'fetched': False}
            self.closets.append(c)
            setattr(
                self.__class__,
                f'live_{c["href"].split("=")[1]}',
                self._closet_method_factory(c)
            )

    @require_login
    def logout(self):
        self.get(f'{HOST}/join/logout')
        self.logged_in = False

    @require_login
    def team(self):
        return self.get(f'{HOST}mypage/team')
