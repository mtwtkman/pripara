# -*- coding: utf-8 -*-
import unittest
from datetime import datetime


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
    def setUp(self):
        self.src = '''
        <p class="mypageDate">データ取得日：2017年10月1日</p>
        <h2>ほげ さん!こんにちは</h2>
        <a class="btnD"><strong>10</strong></a>
        <dl class="idolDataId"><dd>100</dd></dl>
        <dl class="idolDataRank"><dd>神アイドル</dd></dl>
        <dl class="idolDataLike"><dd>400</dd></dl>
        <dl class="idolDataStateRanking"><dd>79位</dd></dl>
        <dl class="idolDataLikeWeekRanking"><dd>111位</dd></dl>
        '''

    def _makeOne(self):
        from pripara.user import User
        return User()

    def test_initial(self):
        sbj = self._makeOne()
        sbj.initial(self.src)
        self.assertEqual(sbj.play_data_date, datetime(2017, 10, 1))
        self.assertEqual(sbj.name, 'ほげ')
        self.assertEqual(sbj.teammate, 10)
        self.assertEqual(sbj.id, 100)
        self.assertEqual(sbj.rank, '神アイドル')
        self.assertEqual(sbj.like, 400)
        self.assertEqual(sbj.weekly_ranking, 79)
        self.assertEqual(sbj.weekly_total, 111)

    def test_data_after_loading_data(self):
        sbj = self._makeOne()
        sbj.initial(self.src)
        result = sbj.data.split('\n')
        self.assertEqual(result[0], 'User data')
        self.assertEqual(result[1], '-- As of 2017/10/01 --')
        self.assertEqual(result[2], 'id:\t100')
        self.assertEqual(result[3], 'name:\tほげ')
        self.assertEqual(result[4], 'teammate:\t10')
        self.assertEqual(result[5], 'rank:\t神アイドル')
        self.assertEqual(result[6], 'like:\t400')
        self.assertEqual(result[7], 'weekly ranking:\t79')
        self.assertEqual(result[8], 'weekly total:\t111')

    def test_print_after_loading_data(self):
        sbj = self._makeOne()
        sbj.initial(self.src)
        result = sbj.__str__()
        self.assertEqual(result, '<User: id=100 name=ほげ>')

    def test_call(self):
        sbj = self._makeOne()
        sbj.initial(self.src)
        result = sbj.data
        self.assertEqual(sbj(), result)


if __name__ == '__main__':
    unittest.main()
