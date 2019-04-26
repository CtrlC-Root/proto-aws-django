import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='frontdesk',
    version='0.1',

    description='A Django based package tracking application.',
    author='Alexandru Barbur',
    author_email='alex@ctrlc.name',
    url='https://github.com/CtrlC-Root/proto-aws-django/blob/master/pkg/frontdesk',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        'Django >= 2.2.0'
    ]
)
