from distutils.core import setup

from setuptools import find_packages


if __name__ == '__main__':
    setup(
        name='donight',
        version='0.1',
        packages=find_packages(),
        install_requires=[
            'selenium',
            'requests',
            'facebook-sdk'
        ],
        description='Scrape events'
    )
