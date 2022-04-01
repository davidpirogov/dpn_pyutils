#!/usr/bin/env python
import sys

try:
    from setuptools import setup
except ImportError:
    print(
        "You do not have setuptools installed and can not install this module. The easiest "
        "way to fix this is to install pip by following the instructions at "
        "https://pip.readthedocs.io/en/latest/installing/\n",
        file=sys.stderr,
    )
    sys.exit(1)


with open("README.md") as readme_file:
    readme = readme_file.read()

setup(long_description=f"{readme}\n\n", long_description_content_type="text/markdown")
