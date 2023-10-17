# TikTok Research Client

[![PyPI](https://img.shields.io/pypi/v/tiktok-research-client.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/tiktok-research-client.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/tiktok-research-client)][python version]
[![License](https://img.shields.io/pypi/l/tiktok-research-client)][license]

[![Read the documentation at https://tiktok-research-client.readthedocs.io/](https://img.shields.io/readthedocs/tiktok-research-client/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/AGMoller/tiktok-research-client/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/AGMoller/tiktok-research-client/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/tiktok-research-client/
[status]: https://pypi.org/project/tiktok-research-client/
[python version]: https://pypi.org/project/tiktok-research-client
[read the docs]: https://tiktok-research-client.readthedocs.io/
[tests]: https://github.com/AGMoller/tiktok-research-client/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/AGMoller/tiktok-research-client
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## TikTok Research Client
TikTok Research Client is a command-line tool for collecting data from TikTok using the TikTok Research API. This tool provides a streamlined way to fetch information about users, search for videos by, and collect comments on specific videos.

YOU NEED TO HAVE ACCESS TO THE [TIKTOK RESEARCH API](https://developers.tiktok.com/products/research-api/) TO USE THIS TOOL.

## Requirements

- Requires granted access to the [TikTok Research API](https://developers.tiktok.com/products/research-api/). Once permisison has been granted, fill out the `.env` file.

## Installation

You can install _TikTok Research Client_ via [pip] from [PyPI]:

```console
$ pip install tiktok-research-client
```


## Usage
Please see the [Command-line Reference] for details.

To run the script, navigate to the folder containing main.py and execute the following command:

```bash
tiktok-research-client [OPTIONS]
```
or
```bash
python -m tiktok-research-client [OPTIONS]
```

### Options
- `-q, --query_option`: What do you want to query? Choose from user, search, or comments.
- `-i, --query_input`: What is the input? For user, enter the username. For search, enter the keywords separated by commas. For comments, enter the video ID.
- `-m, --collect_max`: Maximum number of videos to collect (default is 100).
- `-d, --start_date`: The start date for data collection, formatted as YYYY-MM-DD (default is 2023-01-01).

### Examples

1. To get user information for the username `john_doe`:

```bash
tiktok-research-client -q user -i john_doe
```

2. To search for videos related to coding:

```bash
tiktok-research-client -q search -i "climate,global warming" -m 50
```

3. To get comments for a video with ID 123456789:

```bash
tiktok-research-client -q comments -i 123456789
```


## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_TikTok Research Client_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/AGMoller/tiktok-research-client/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/AGMoller/tiktok-research-client/blob/main/LICENSE
[contributor guide]: https://github.com/AGMoller/tiktok-research-client/blob/main/CONTRIBUTING.md
[command-line reference]: https://tiktok-research-client.readthedocs.io/en/latest/usage.html
