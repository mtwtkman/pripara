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

```python
>>> from pripara import config, client
>>> conf = config.Config()
>>> conf.load()
>>> cli = client.Client(**conf.as_dict())
>>> cli.login()
```

Ok, now you an idol. You are so gread idol!

# Test
`$ python -m unittest tests/*.py`
