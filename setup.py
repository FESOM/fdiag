#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

# with open('README.md') as readme_file:
#     readme = readme_file.read()

# with open('HISTORY.rst') as history_file:
#     history = history_file.read()

requirements = ['papermill','jinja2', 'pyyaml', 'pyfesom2']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="FESOM team",
    author_email='koldunovn@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    entry_points={
    'console_scripts': [
        'fdiag=fdiag.fdiag:fdiag',  # command=package.module:function
    ],
    },
    description="FESOM2 diagnostics",
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords='fdiag',
    name='fdiag',
    packages=['fdiag'],
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/koldunovn/fdiag',
    version='0.1.0',
    zip_safe=False,
)
