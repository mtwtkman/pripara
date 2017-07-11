# -*- coding: utf-8 -*-
import re

import requests
from bs4 import BeautifulSoup as bs


__all__ = ['NOT_LOGGED_IN', 'Client']


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


class Closet(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fetched = False


class Client:
    headers = {'user-agent': UA}

    def __str__(self):
        if not self.logged_in:
            return f'<Client: {NOT_LOGGED_IN}>'
        return f'<Client: You logged in as {self.username}.>'

    def __init__(self, email, password):
        self.email = email
        self.closets = []
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
            'teammate': src.find('a', 'btnD').find('strong').text or None,
            'id': src.find('dl', 'idolDataId').find('dd').text,
            'rank': src.find('dl', 'idolDataRank').find('dd').text,
            'like': src.find('dl', 'idolDataLike').dd.text or None,
            'weekly_ranking': src.find('dl', 'idolDataStateRanking').find('dd').text[:-1] or None,
            'weekly_total': src.find('dl', 'idolDataLikeWeekRanking').find('dd').text[:-1] or None,
        }

    def _closet_method_factory(self, closet, href):
        def fetch(self):
            if not closet.fetched:
                response = self.get(f'{HOST}{href}')
                closet.fetched = True
                src = list(bs(response.text, 'html.parser').find('p', 'charText').children)[2:]
                name, count = src[0].text.split('：')
                closet['data'] = {
                    'name': re.match(r'^★(.+)(?=のアイテム数$)', name).group(1),
                    'count': int(count),
                    'total': int(src[1][1:]),
                }
            return {
                'name': closet['title'],
                'data': closet['data'],
            }
        return fetch

    def _closet(self, src):
        for x in src.find_all('li', re.compile(r'no\d{6}')):
            href = x.a['href']
            method_name = f'live_{href.split("=")[1]}'
            c = Closet({'title': x.a.text, 'data': None})
            self.closets.append(c)
            setattr(
                self.__class__,
                method_name,
                self._closet_method_factory(c, href)
            )
            c.fetch = getattr(self, method_name)

    @require_login
    def logout(self):
        self.get(f'{HOST}/join/logout')
        self.logged_in = False

    def _friends(self, src):
        result = []
        for friend in src.find_all('tr', re.compile(r'Rank\d+')):
            tds = friend.find_all('td')
            likes_elem = next(tds[1].children)
            if isinstance(likes_elem, str):
                likes = 0
            else:
                # NOTE: I don't know that how structure acturally...
                likes = int(likes_elem.text)
            result.append({
                'name': tds[0].span.text,
                'rank': int(friend['class'][0][4:]),
                'likes': likes,
                'count': int(tds[2].em.text[:-1]),
            })
        return result

    @require_login
    def team(self):
        response = self.get(f'{HOST}/mypage/team')
        src = bs(response.text, 'html.parser')
        return self._friends(src)

    @require_login
    def team_total(self):
        response = self.get(f'{HOST}/mypage/team_count')
        src = bs(response.text, 'html.parser')
        return self._friends(src)
