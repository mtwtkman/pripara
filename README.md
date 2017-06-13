# Mind
> プリパラは好きぷり?
> じゃあ大丈夫ぷり!

# pripara
This is a client for [priparaclub](https://pripara.jp/) implemented by python.

You know Laala said, "Everyone are friend, everyone are idol.". I think so.

# Requirements
- python3.6+
- priparaclub account

# Install
I recommend to create virtual env for python.

```sh
$ git clone git@github.com:mtwtkman/pripara
$ cd pripara
$ pyvenv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

Done✨

# Usage
This script exposes `Config`, `Client`, `User`. Mainly needed is `Client`.

`Client` needs `email` and `password` to login. `Config` helps store there.

```sh
>>> from pripara import config, client
>>> conf = config.Config()
>>> conf.load()
>>> cli = client.Client(**conf.as_dict())
>>> cli.login()
>>> cli.user.data()
User data
-- As of 2017/06/13 --
id:     00000000000
name:   ほげ
teammate:       0
rank:   ピカピカけんきゅうせい
like:   23916
weekly ranking: 26155
weekly total:   17968
>>> cli.logout()
```

Ok, you are so gread idol. Laala said...

# Test
`$ python -m unittest tests/*.py`
