# -*- coding: utf-8 -*-
import sys
import unittest
from io import StringIO
from unittest import mock
from datetime import datetime

from pripara.user import Datetime, Str, Int, NOT_LOGGED_IN


class DatetimeTest(unittest.TestCase):
    def _makeOne(self):
        return Datetime()

    def test_initial(self):
        sbj = self._makeOne()
        self.assertIsNone(sbj.value)

    def test_with_valid_value(self):
        sbj = self._makeOne()
        sbj.value = '2017年1月10日'
        self.assertEqual(sbj.value, datetime(2017, 1, 10))

    def test_with_none(self):
        sbj = self._makeOne()
        sbj.value = None
        self.assertIsNone(sbj.value)

    def test_raise_with_invalid_format(self):
        sbj = self._makeOne()
        with self.assertRaises(ValueError):
            sbj.value = '2017/1/10'


class StrTest(unittest.TestCase):
    def _makeOne(self):
        return Str()

    def test_initial(self):
        sbj = self._makeOne()
        self.assertEqual(sbj.value, '')

    def test_with_valid_value(self):
        sbj = self._makeOne()
        v = 'hoge'
        sbj.value = v
        self.assertEqual(sbj.value, v)

    def test_raise_with_not_str(self):
        sbj = self._makeOne()
        with self.assertRaises(TypeError):
            sbj.value = 1

    def test_raise_with_none(self):
        sbj = self._makeOne()
        with self.assertRaises(TypeError):
            sbj.value = None

    def test_with_value_includes_spaces_at_both_edges(self):
        sbj = self._makeOne()
        v = 'hoge'
        sbj.value = f'    {v}     '
        self.assertEqual(sbj.value, v)


class IntTest(unittest.TestCase):
    def _makeOne(self):
        return Int()

    def test_initial(self):
        sbj = self._makeOne()
        self.assertEqual(sbj.value, 0)

    def test_with_valid_value(self):
        sbj = self._makeOne()
        v = 10
        sbj.value = v
        self.assertEqual(sbj.value, v)

    def test_raise_with_not_digit_str(self):
        sbj = self._makeOne()
        with self.assertRaises(TypeError):
            sbj.value = 'hoge'

    def test_with_digit_str(self):
        sbj = self._makeOne()
        v = '10'
        sbj.value = v
        self.assertEqual(sbj.value, int(v))

    def test_raise_with_none(self):
        sbj = self._makeOne()
        with self.assertRaises(TypeError):
            sbj.value = None


class UserTest(unittest.TestCase):
    def setUp(self):
        self.capture = StringIO()
        sys.stdout = self.capture
        self.email = 'mirei@pripara.com'
        self.password = 'puri'
        self.login_response = {
            'play_data_date': '2017年10月1日',
            'name': 'みれぃ',
            'teammate': 100,
            'id': 3,
            'rank': '神アイドル',
            'like': 1000000,
            'weekly_ranking': 1,
            'weekly_total': 1,
        }

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def _makeOne(self, logged_in=False):
        with mock.patch('pripara.user.Config') as ConfigMock, \
             mock.patch('pripara.user.Client') as ClientMock:
            ConfigMock().load = mock.Mock(return_value=None)
            ConfigMock().as_dict = mock.Mock(return_value={
                'email': self.email,
                'password': self.password,
            })
            ClientMock().login = mock.Mock(return_value=self.login_response)
            ClientMock().logged_in = mock.Mock(return_value=logged_in)()
            from pripara.user import User
            return User()

    def test_init(self):
        sbj = self._makeOne()
        for f in sbj.field_names:
            with self.subTest(f=f):
                self.assertTrue(hasattr(sbj, f'_{f}'))

    def test_login(self):
        sbj = self._makeOne(logged_in=True)
        sbj.login()
        for k, v in self.login_response.items():
            with self.subTest(k=k):
                if k == 'play_data_date':
                    self.assertEqual(getattr(sbj, k), datetime.strptime(v, '%Y年%m月%d日'))
                    continue
                self.assertEqual(getattr(sbj, k), v)

    def test_as_dict_before_login(self):
        sbj = self._makeOne()
        for field, T in sbj.fields:
            with self.subTest(field=field, T=T):
                self.assertEqual(getattr(sbj, field), T.default)

    def test_as_dict_after_login(self):
        sbj = self._makeOne(logged_in=True)
        sbj.login()
        expect = self.login_response.copy()
        expect['play_data_date'] = datetime.strptime(self.login_response['play_data_date'], '%Y年%m月%d日')
        self.assertEqual(sbj.as_dict(), expect)

    def test_info_before_login(self):
        sbj = self._makeOne()
        sbj.info
        self.assertEqual(self.capture.getvalue(), f'{NOT_LOGGED_IN}\n')

    def test_info_after_login(self):
        sbj = self._makeOne(logged_in=True)
        sbj.login()
        self.capture.seek(0)
        self.capture.write('')
        sbj.info
        result = self.capture.getvalue().split('\n')
        self.assertEqual(result[0], 'User data')
        self.assertEqual(result[1], f'-- As of {sbj.play_data_date.strftime("%Y/%m/%d")} --')
        self.assertEqual(result[2], f'id:\t{sbj.id}')
        self.assertEqual(result[3], f'name:\t{sbj.name}')
        self.assertEqual(result[4], f'teammate:\t{sbj.teammate}')
        self.assertEqual(result[5], f'rank:\t{sbj.rank}')
        self.assertEqual(result[6], f'like:\t{sbj.like}')
        self.assertEqual(result[7], f'weekly ranking:\t{sbj.weekly_ranking}')
        self.assertEqual(result[8], f'weekly total:\t{sbj.weekly_total}')

if __name__ == '__main__':
    unittest.main()
