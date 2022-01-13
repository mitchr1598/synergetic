#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

requirements = [ ]

setup(
    author="Mitchell Reid",
    author_email='mitchr1598@gmail.com',
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    description="An interface for working with the Synergetic Database",
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords='synergetic',
    name='synergetic',
    packages=find_packages(include=['synergetic', 'synergetic.*', 'synergetic.Attendance']),
    url='https://github.com/mitchr1598/synergetic',
    version='0.0.1',
)
