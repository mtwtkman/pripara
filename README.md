# Mind
> プリパラは好きぷり?
> じゃあ大丈夫ぷり!

# pripara
This is a client for [priparaclub](https://pripara.jp/join/login) implemented by python.

You know Laala said "Everyone are friend, everyone are idol.". I think so.

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
This script exposes APIs which are `Config`, `Client` and `User`. Mainly you need is `User`.

- `Config` helps you to store login data.
- `Client` helps you to fetch data from priparaclub.
- `User` helps you to store fetched data and show them.

## How to login and logout
At first you must login every running this script.

```sh
>>> from pripara.user import User
>>> user = User()
>>> user.login()
```

Ok, you are so great idol. Laala said...

And if you want to logout,
```sh
>>> user.logout()
```

## How to reference user data
After you logged in, you can reference already basic user data.

```sh
>>> user.info
User data
-- As of 2017/06/16 --
id:     XXXXXXXXXXX
name:   パル
teammate:       1
rank:   がんばりけんきゅうせい
like:   77236
weekly ranking: 8287
weekly total:   4145
```

And you can access each data via `User` object.

```sh
>>> user.id
>>> user.name
>>> user.teammate
...
```

All of them are listed at `User.field_names`. Or `User` object exposes `as_dict()` which show you them as dictionary format.

```sh
>>> user.as_dict()
{'id': 'XXXXXXXXXXX', 'name': 'パル', ...}
```

## How to fetch team data
```sh
>>> user.team()
>>> user.team_total()
```

Do you want to check team data? You can.

```sh
>>> user.team_data
```

## How to fetch closet data
After you logged in, you can reference closet data.

```sh
>>> user.closets
```

If you want to fetch data of 'タイム2弾'.

```sh
>>> user.closets[0].fetch()
```

Ok. Fine.

# Test
`$ python -m unittest tests`
