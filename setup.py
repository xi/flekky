#!/usr/bin/env python

from setuptools import setup, find_packages
import os

root = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(root, 'README.rst')) as fh:
    readme = fh.read()


setup(
    name='flekky',
    version='0.1.1',
    description="Static website generator inspired by jekyll based on flask.",
    long_description=readme,
    author='Tobias Bengfort',
    author_email='tobias.bengfort@gmx.net',
    url='https://github.com/xi/flekky',
    install_requires=[
        'Flask>=0.10.1',
        'Flask-FlatPages>=0.5',
        'Frozen-Flask>=0.11',
        'argparse>=1.2.1',
    ],
    test_suite='test',
    platforms='any',
    packages=find_packages(),
    license='GPLv3+',
    entry_points={'console_scripts': 'flekky=flekky.flekky:main'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
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
