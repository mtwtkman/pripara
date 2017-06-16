# -*- coding: utf-8 -*-
import sys
import unittest
from io import StringIO
from collections import namedtuple

from bs4 import BeautifulSoup as bs

from pripara.client import NOT_LOGGED_IN, AbnormalResponse


class ClientTestMixin:
    def _makeOne(self, email=None, password=None):
        from pripara.client import Client
        return Client(email, password)


class ClientClosetMethodTest(ClientTestMixin, unittest.TestCase):
    def setUp(self):
        self.tags = [201701, 201601, 201501]
        self.htmls = [
            f'<li class="no{y}"><a href="url?live={y}">test{i}</a></li>'
            for i, y in enumerate(self.tags)
        ]
        self.src = bs(''.join(self.htmls), 'html.parser')

    def _callFUT(self):
        ins = self._makeOne()
        ins._closet(self.src)
        return ins

    def test(self):
        sbj = self._callFUT()
        self.assertEqual(len(sbj.closets), len(self.htmls))
        expects = [
            {'href': f'url?live={x}', 'title': f'test{i}', 'fetched': False} for i, x in enumerate(self.tags)
        ]
        for i, e in enumerate(expects):
            with self.subTest(e=e):
                self.assertEqual(e, sbj.closets[i])
                self.assertTrue(hasattr(sbj, f'live_{self.tags[i]}'))


class FriendsMethodTest(ClientTestMixin, unittest.TestCase):
    def setUp(self):
        self.tbody = '<tbody>{}</tbody>'
        self.tr = '''
        <tr class="Rank{rank}">
          <th><img src="img.png"></th>
          <td><span>{name}</span>さん</td>
          <td>{likes}</td>
          <td class="lastChild"><em>{count}回</em></td>
        </tr>
        '''

    def _callFUT(self, src):
        ins = self._makeOne()
        return ins._friends(bs(src, 'html.parser'))

    def test_no_friend(self):
        result = self._callFUT(self.tbody)
        self.assertEqual(len(result), 0)

    def test_has_friend(self):
        inner = [
            dict(zip(('rank', 'name', 'likes', 'count'), x))
            for x in (
                (1, 'そふぃ', '<em>10</em>', 100),
                (2, 'ドロシー', '-', 10),
            )
        ]
        result = self._callFUT(self.tbody.format('\n'.join([self.tr.format(**x) for x in inner])))
        self.assertEqual(len(result), len(inner))
        for friend, r in zip(inner, result):
            for k, v in friend.items():
                if k == 'likes':
                    v = 0 if v == '-' else int(bs(v, 'html.parser').text)
                self.assertEqual(r[k], v)


class DecoratorTestMixin:
    def _dummyClass(self, return_value):
        class C:
            def method(self):
                return return_value
        return C


class RequireLoginDecoratorTest(DecoratorTestMixin, unittest.TestCase):
    def setUp(self):
        self.capture = StringIO()
        sys.stdout = self.capture

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def _callFUT(self, method):
        from pripara.client import require_login
        return require_login(method)

    def test_return_none_when_not_logged_in(self):
        c = self._dummyClass(1)
        c.logged_in = False
        response = self._callFUT(c.method)(c)
        self.assertIsNone(response)
        self.assertEqual(self.capture.getvalue(), f'{NOT_LOGGED_IN}\n')

    def test_return_result_when_logged_in(self):
        return_value = 1
        c = self._dummyClass(return_value)
        c.logged_in = True
        response = self._callFUT(c.method)(c)
        self.assertEqual(response, return_value)


class ValidResponseDecoratorTest(DecoratorTestMixin, unittest.TestCase):
    def _callFUT(self, method):
        from pripara.client import valid_response
        return valid_response(method)

    def _responseClass(self, status_code):
        R = namedtuple('Response', 'status_code')
        return R(status_code)

    def test_raise_status_code_more_then_3xx(self):
        r = self._responseClass(400)
        c = self._dummyClass(r)
        with self.assertRaises(AbnormalResponse):
            self._callFUT(c.method)(c)

    def test_return_response_status_code_is_3xx(self):
        code = 300
        r = self._responseClass(code)
        c = self._dummyClass(r)
        response = self._callFUT(c.method)(c)
        self.assertEqual(response.status_code, code)

    def test_return_response_status_code_is_2xx(self):
        code = 200
        r = self._responseClass(code)
        c = self._dummyClass(r)
        response = self._callFUT(c.method)(c)
        self.assertEqual(response.status_code, code)
