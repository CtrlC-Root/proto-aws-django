import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='multitool',
    version='0.1',

    description='Automation utilities for use with doit.',
    author='Alexandru Barbur',
    author_email='alex@ctrlc.name',
    url='https://github.com/CtrlC-Root/proto-aws-django/blob/master/pkg/multitool',

    packages=find_packages(),

    install_requires=[
        'doit >= 0.31.0'
    ]
)
