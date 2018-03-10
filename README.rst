Pyramid OAuthLib
================

.. image:: https://travis-ci.org/tilgovi/pyramid-oauthlib.svg?branch=master
    :target: https://travis-ci.org/tilgovi/pyramid-oauthlib
.. image:: http://img.shields.io/coveralls/tilgovi/pyramid-oauthlib.svg
    :target: https://coveralls.io/r/tilgovi/pyramid-oauthlib

Pyramid OAuthLib is a library to integrate the excellent `OAuthLib`_ library
easily into `Pyramid`_ applications. It is designed to ease development of
OAuth applications, provide smooth migration possibilites to legacy codebases
using other authentication or authorization schemes, and configuration patterns
for creating pluggable OAuth components for Pyramid.

**NOTICE**: Pyramid OAuthLib is not feature complete! It is missing the hooks
for token revocation. While this shouldn't be hard to add, it wasn't a priority
to get the initial version released.

Usage Overview
--------------

Configuration::

    def includeme(config):
        """Integration with OAuthLib is as smooth as possible."""
        from oauthlib.oauth2 import BearerToken, AuthorizationCodeGrant

        # Validator callback functions are passed Pyramid request objects so
        # you can access your request properties, database sessions, etc.
        # The request object is populated with accessors for the properties
        # referred to in the OAuthLib docs and used by its built in types.
        validator = MyRequestValidator()

        # Register response types to create grants.
        config.add_response_type('oauthlib.oauth2.AuthorizationCodeGrant',
                                 name='code',
                                 request_validator=validator)

        # Register grant types to validate token requests.
        config.add_grant_type('oauthlib.oauth2.AuthorizationCodeGrant',
                              name='authorization_code',
                              request_validator=validator)

        # Register the token types to use at token endpoints.
        # The second parameter to all registrations may be left out to set it
        # as default to use when no corresponding request parameter specifies
        # the grant, response or token type. Be aware that the built in types
        # will fail if a matching request parameter is missing, though.
        config.add_token_type('oauthlib.oauth2.BearerToken',
                              request_validator=validator)


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

Custom grant type::

    from oauthlib.oauth2 import ClientCredentialsGrant, InvalidClientError
    from pyramid.authentication import BadCSRFToken
    from pyramid.session import check_csrf_token

    class SessionGrant(ClientCredentialsGrant):

        """A combined authentication and authorization session assertion grant.

        When the Authorization Server and the Token Service are the same server
        this grant type uses a single assertion, the CSRF token, for client
        authentication and an authorization grant.[1] This works particularly
        well with :class:`pyramid.authentication.SessionAuthenticationPolicy`.

        [1] http://tools.ietf.org/html/draft-ietf-oauth-assertions-01#section-3
        """

        def validate_token_request(self, request):
            try:
                check_csrf_token(request, token='assertion')
            except BadCSRFToken:
                raise InvalidClientError(request=request)

            # An object with the confidential client_id and client_secret.
            request.client = LOCAL_CLIENT

            if request.client is None:
                raise InvalidClientError(request=request)

            request.client_id = request.client_id or request.client.client_id


    def includeme(config):
        config.add_grant_type(SessionGrant, 'assertion')

License
-------

Pyramid OAuthLib is released under the `2-Clause BSD License`_, sometimes
referred to as the "Simplified BSD License" or the "FreeBSD License". More
license information can be found in the included ``LICENSE.txt`` file.

.. _OAuthLib: https://github.com/idan/oauthlib
.. _Pyramid: http://www.pylonsproject.org/
.. _2-Clause BSD License: http://www.opensource.org/licenses/BSD-2-Clause
