#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="dir2markdown",
    version="1.0",
    description="Converts a directory structure of python files to a markdown (.md) and PDF",
    author="Julian Loiacono",
    author_email="jcloiacon@gmail.com",
    url="https://github.com/julianfl0w/dir2markdown",
    packages=find_packages(exclude=("examples")),
    package_data={
        # everything
        # "": ["*"]
        "": ["."]
    },
    include_package_data=True,
)
