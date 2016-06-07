from setuptools import setup
from setuptools import find_packages

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
    license='Apache',
    packages=find_packages()
)
