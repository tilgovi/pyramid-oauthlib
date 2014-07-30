Pyramid OAuthLib
================

Pyramid OAuthLib is a library to integrate the excellent `OAuthLib`_ library
easily into `Pyramid`_ applications. It is designed to ease development of
OAuth applications, provide smooth migration possibilites to legacy codebases
using other authentication or authorization schemes, and provide patterns for
providing pluggable OAuth functionality in Pyramid applications.

Initial functionality:

- Grant, Response, and Token Type registration
- Composite endpoint with delegation to type
- Introspectables
- OAuthlib compatibility request properties

Missing:

- Revocation
- Tests
- Documentation


.. _OAuthLib: https://github.com/idan/oauthlib
.. _Pyramid: http://www.pylonsproject.org/
