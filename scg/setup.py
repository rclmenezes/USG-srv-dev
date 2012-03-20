from setuptools import setup, find_packages

from setuptools.command import sdist
# http://rhodesmill.org/brandon/2009/eby-magic/
sdist.finders = []

setup(
    name='SCG',
    version='2.0a',
    packages=find_packages(),
    include_package_data=True,
)
