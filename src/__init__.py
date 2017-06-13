# -*- coding: utf-8 -*-
import sys


v = sys.version_info
if v.major != 3 and v.minor < 6:
    print('This requires python3.6+')
    sys.exit(0)


if __name__ == '__main__':
    from .main import main
    main()
