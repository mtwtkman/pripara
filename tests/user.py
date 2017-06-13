# -*- coding: utf-8 -*-
import sys
import unittest
from datetime import datetime

sys.path.append('../pripara')

from pripara.user import Datetime, Str, Int


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

    def test_raise_with_not_int(self):
        sbj = self._makeOne()
        with self.assertRaises(TypeError):
            sbj.value = 'hoge'

    def test_raise_with_none(self):
        sbj = self._makeOne()
        with self.assertRaises(TypeError):
            sbj.value = None


class UserTest(unittest.TestCase):
    def _makeOne(self):
        from pripara.user import User
        return User()

    def test_user_fields(self):
        sbj = self._makeOne()
        self.assertTrue(hasattr(sbj, 'play_data_date'))
        self.assertTrue(isinstance(sbj.play_data_date, Datetime))
        self.assertTrue(hasattr(sbj, 'name'))
        self.assertTrue(isinstance(sbj.name, Str))
        self.assertTrue(hasattr(sbj, 'teammate'))
        self.assertTrue(isinstance(sbj.teammate, Int))

    def test_attr(self):
        sbj = self._makeOne()
        name = 'hoge'
        sbj.name = name
        self.assertEqual(sbj.name, name)


if __name__ == '__main__':
    unittest.main()
