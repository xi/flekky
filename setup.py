#!/usr/bin/env python

import os
import re
from setuptools import setup, find_packages

DIRNAME = os.path.abspath(os.path.dirname(__file__))
rel = lambda *parts: os.path.abspath(os.path.join(DIRNAME, *parts))

README = open(rel('README.rst')).read()
FLEKKY = open(rel('flekky', 'flekky.py')).read()
VERSION = re.search("__version__ = '([^']+)'", FLEKKY).group(1)


setup(
    name='flekky',
    version=VERSION,
    description="Static website generator inspired by jekyll based on flask.",
    long_description=README,
    author='Tobias Bengfort',
    author_email='tobias.bengfort@gmx.net',
    url='https://github.com/xi/flekky',
    install_requires=[
        'Flask>=0.10.1',
        'Flask-FlatPages>=0.6',
        'Frozen-Flask>=0.11',
        'beautifulsoup4>=4.4.0',
        'argparse>=1.2.1',
    ],
    test_suite='test',
    platforms='any',
    packages=find_packages(),
    package_data={'flekky': [
        'init/pages/index.md',
        'init/static/css/style.css',
        'init/templates/base.html',
        'init/templates/layout/default.html',
    ]},
    license='GPLv3+',
    entry_points={'console_scripts': 'flekky=flekky.flekky:main'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: GNU General Public License v3 or later '
            '(GPLv3+)',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: HTML',
    ])
