import os

from codecs import open
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as fp:
    requirements = fp.read().splitlines()

setup(
    name='solenoid',
    version='1.0',
    author='Lisa Roach',
    author_email='lisroach@cisco.com',
    url='https://cto-github.cisco.com/lisroach/Solenoid',
    description='''
        Injects routes into Cisco's IOS-XR RIB table, based on some
        outside logic.
    ''',
    license='BSD',
    packages=find_packages(),
    install_requires=requirements
)
