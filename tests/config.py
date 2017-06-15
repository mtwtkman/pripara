# -*- coding: utf-8 -*-
import os
import json
import unittest
import tempfile


class ConfigReadTest(unittest.TestCase):
    def setUp(self):
        self.tmp_file = tempfile.NamedTemporaryFile()
        self.original_os_environ = os.environ.copy()

    def tearDown(self):
        os.environ = self.original_os_environ.copy()

    def _callFUT(self, file_name=None):
        from pripara.config import Config
        Config.file_name = file_name or self.tmp_file.name
        ins = Config()
        ins._read()
        return ins

    def test_both_config_and_env_var_do_not_exist(self):
        ins = self._callFUT('not_exist')
        self.assertIsNone(ins.password)
        self.assertIsNone(ins.email)

    def test_only_env_var_exists(self):
        e = 'mirei@pripara.com'
        p = 'puri'
        os.environ.update({
            'PRIPARA_EMAIL': e,
            'PRIPARA_PASSWORD': p,
        })
        ins = self._callFUT('not_exist')
        self.assertEqual(ins.email, e)
        self.assertEqual(ins.password, p)

    def test_only_config_exists(self):
        e = 'laala@pripara.com'
        p = 'kasikoma'
        self.tmp_file.write(bytes(json.dumps({'email': e, 'password': p}), 'utf-8'))
        self.tmp_file.seek(0)
        ins = self._callFUT()
        self.assertEqual(ins.email, e)
        self.assertEqual(ins.password, p)


if __name__ == '__main__':
    unittest.main()
