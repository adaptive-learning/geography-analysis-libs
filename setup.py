# -*- coding: utf-8 -*-
from setuptools import setup


setup(
    name='proso-geography-analysis',
    version='0.9.7',
    description='Libs for analysis of data from PROSO Geography project',
    author='Jan Papousek',
    author_email='jan.papousek@gmail.com',
    packages=['proso.geography', 'proso'],
    namespace_packages = ['proso.geography', 'proso'],
    license='Gnu GPL v3',
    url='https://github.com/proso/geography-analysis-libs/',
    install_requires=[
        'argparse>=1.1',
        'matplotlib>=1.3.1',
        'numpy>=1.8.0',
        'pandas>=0.13.1',
        'proso-geography-data>=1.0.1'
    ],
)
