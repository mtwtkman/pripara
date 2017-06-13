# -*- coding: utf-8 -*-
import sys


v = sys.version_info
if v.major != 3 and v.minor < 6:
    print('This requires python3.6+')
    sys.exit(0)


if __name__ == '__main__':
    from .config import Concifg
    from .client import Client

    config = Config()
    config.load()
    client = Client(**config.as_dict())
    client.login()
