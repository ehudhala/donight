from setuptools import setup, find_packages

setup(
    name='donight',
    description='Finds events, and notifies users about them.',
    packages=find_packages(),
    install_requires=['sqlalchemy', 'requests', 'beautifulsoup4', 'lxml', 'pyexcelerate', 'python-dateutil']
)
