import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'oauthlib',
    ]

setup(
    name='pyramid_oauthlib',
    version='0.0',
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
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    test_suite="pyramid_oauthlib",
)
