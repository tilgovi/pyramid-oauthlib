import os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    user_options = [
        ('cov', None, "measure coverage")
    ]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.cov = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['pyramid_oauthlib']
        if self.cov:
            self.test_args += ['--cov', 'pyramid_oauthlib']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

setup(
    name='pyramid_oauthlib',
    version='0.4.0',
    description='Pyramid OAuthLib integration',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
    ],
    author='Randall Leeds',
    author_email='tilgovi@hypothes.is',
    url='https://github.com/tilgovi/pyramid_oauthlib',
    keywords='web pyramid pylons oauth authentication',
    cmdclass={'test': PyTest},
    exclude_package_data={'': ['.gitignore']},
    include_package_data=True,
    install_requires=['pyramid>=1.4.0', 'oauthlib'],
    packages=find_packages(),
    setup_requires=['setuptools_git'],
    tests_require=['mock', 'pytest', 'pytest-cov'],
    zip_safe=False,
)
