try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Pygraph',
    'author': 'Mikko Nylen',
    'url': '',
    'download_url': '',
    'author_email': '',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['pygraph'],
    'scripts': [],
    'name': 'Pygraph'
}

setup(**config)