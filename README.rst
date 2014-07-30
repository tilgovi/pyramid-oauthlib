Pyramid OAuthLib
================

Pyramid OAuthLib is a library to integrate the excellent `OAuthLib`_ library
easily into `Pyramid`_ applications. It is designed to ease development of
OAuth applications, provide smooth migration possibilites to legacy codebases
using other authentication or authorization schemes, and configuration patterns
for creating pluggable OAuth components for Pyramid.

Initial functionality:

- Grant, Response, and Token Type registration
- Composite endpoint with delegation to type
- Introspectables
- OAuthlib compatibility request properties

Missing:

- Revocation
- Tests
- Documentation

Examples
--------

Token response::

    def access_token(request):
        """Core functionality is available directly from the request.

        Responses from OAuthLib are wrapped in a response object of type
        :class:`pyramid.response.Response` so they can be returned directly
        from views.
        """
        userid = request.authenticated_userid
        if userid is not None:
            credentials = dict(userId=userid)
        else:
            credentials = None

        return request.create_token_response(credentials=credentials)

Using OAuthLib components::

    from oauthlib.oauth2 import BearerToken, RequestValidator

    class MyRequestValidator(RequestValidator):
        """Omitted for brevity.

        Unlike regular OAuthLib endpoints, the endpoint created by
        Pyramid OAuthLib passes :class:`pyramid.request.Request` objects
        rather than OAuthLib request objects. However, including the
        Pyramid OAuthLib package in your Pyramid project will cause the
        request to contain new properties, such as `request.state` that
        hold OAuth parameters for interoperability with OAuthLib code.
        """

    def includeme(config):
        bearer_token = BearerToken(request_validator=MyRequestValidator())
        config.add_token_type(bearer_token, 'Bearer')


.. _OAuthLib: https://github.com/idan/oauthlib
.. _Pyramid: http://www.pylonsproject.org/
