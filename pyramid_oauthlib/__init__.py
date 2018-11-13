# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from oauthlib import oauth2
from oauthlib.oauth2.rfc6749.endpoints import base
from pyramid.response import Response
from pyramid.compat import native_

log = logging.getLogger(__name__)

OAUTH_PARAMS = (
    'access_token',
    'client_id',
    'client_secret',
    'code',
    'grant_type',
    'password',
    'refresh_token',
    'response_type',
    'redirect_uri',
    'scope',
    'state',
    'username',
)


class Server(
        oauth2.AuthorizationEndpoint,
        oauth2.ResourceEndpoint,
        oauth2.RevocationEndpoint,
        oauth2.TokenEndpoint,
        base.BaseEndpoint,
):
    def __init__(self):
        base.BaseEndpoint.__init__(self)

        # For grants and responses these are string keys.
        self._default_grant_type = ''
        self._default_response_type = ''
        self._default_token = ''

        self._grant_types = {}
        self._response_types = {}
        self._tokens = {}

    @property
    def default_token_type(self):
        return self.tokens.get('')

    @base.catch_errors_and_unavailability
    def create_authorization_response(self, request,
                                      scopes=None, credentials=None):
        request.scopes = scopes
        for k, v in (credentials or {}).items():
            setattr(request, k, v)
        handler = self.response_types.get(
            request.response_type,
            self.default_response_type_handler,
        )

        token = self.default_token_type
        if token is None:
            raise AttributeError('No default token type registered.')

        return handler.create_authorization_response(request, token)

    @base.catch_errors_and_unavailability
    def create_revocation_response(self, request):
        pass

    @base.catch_errors_and_unavailability
    def create_token_response(self, request, credentials=None):
        request.scopes = None
        request.extra_credentials = credentials
        handler = self.grant_types.get(
            request.grant_type,
            self.default_grant_type_handler,
        )

        token = self.default_token_type
        if token is None:
            raise AttributeError('No default token type registered.')

        return handler.create_token_response(request, token)

    @base.catch_errors_and_unavailability
    def validate_authorization_request(self, request):
        request.scopes = None
        handler = self.response_types.get(
            request.response_type,
            self.default_response_type_handler,
        )
        return handler.validate_authorization_request(request)

    @base.catch_errors_and_unavailability
    def verify_request(self, request, scopes=None):
        request.scopes = scopes
        request.token_type = self.find_token_type(request)
        handler = self.tokens.get(
            request.token_type,
            self.default_token_type_handler,
        )
        return handler.validate_request(request)


def add_grant_type(config, grant_type, name='', **kwargs):
    grant_type = config.maybe_dotted(grant_type)(**kwargs)

    def register():
        config.registry.oauth.grant_types[name] = grant_type

    intr = config.introspectable(
        category_name='oauth handlers',
        discriminator=('grant', name),
        title=name or '<default>',
        type_name='grant',
    )
    intr['value'] = grant_type

    config.action(('oauth grant type', name), register,
                  introspectables=(intr,), order=1)


def add_response_type(config, response_type, name='', **kwargs):
    response_type = config.maybe_dotted(response_type)(**kwargs)

    def register():
        config.registry.oauth.response_types[name] = response_type

    intr = config.introspectable(
        category_name='oauth handlers',
        discriminator=('response', name),
        title=name or '<default>',
        type_name='response',
    )
    intr['value'] = response_type

    config.action(('oauth response type', name), register,
                  introspectables=(intr,), order=1)


def add_token_type(config, token_type, name='', **kwargs):
    token_type = config.maybe_dotted(token_type)(**kwargs)

    def register():
        config.registry.oauth.tokens[name] = token_type

    intr = config.introspectable(
        category_name='oauth handlers',
        discriminator=('token', name),
        title=name or '<default>',
        type_name='token',
    )
    intr['value'] = token_type

    config.action(('oauth token type', name), register,
                  introspectables=(intr,), order=1)


def add_oauth_param(config, name):
    def getter(request):
        return request.params.get(name)
    config.add_request_method(getter, str(name), reify=True)


def duplicate_params(request):
    keys = list(request.params)
    return [k for k in keys if keys.count(k) > 1]

def oauth_response(result):
    headers, body, status = result
    return Response(body=body, status=status, headers={
        native_(name, encoding='latin-1'): native_(value, encoding='latin-1')
        for name, value
        in headers.items()
    })


def register(config, server):
    config.registry.oauth = server


def includeme(config):
    server = Server()
    intr = config.introspectable(
        category_name='oauth servers',
        discriminator='server',
        title='<default>',
        type_name='server',
    )
    intr['value'] = server

    config.action('oauth server', register,
                  introspectables=(intr,), args=(config, server))

    config.add_directive('add_grant_type', add_grant_type, True)
    config.add_directive('add_response_type', add_response_type, True)
    config.add_directive('add_token_type', add_token_type, True)
    config.add_directive('add_oauth_param', add_oauth_param)

    config.add_request_method(
        lambda request, scopes=None, credentials=None:
        oauth_response(
            server.create_authorization_response(
                request,
                scopes=scopes,
                credentials=credentials
            )
        ),
        str('create_authorization_response'))

    config.add_request_method(
        lambda request:
        server.create_revocation_response(request),
        str('create_revocation_response'))

    config.add_request_method(
        lambda request, credentials=None:
        oauth_response(
            server.create_token_response(request, credentials=credentials)
        ),
        str('create_token_response'))

    config.add_request_method(
        lambda request:
        server.validate_authorization_request(request),
        str('validate_authorization_request'))

    config.add_request_method(
        lambda request, scopes=None:
        server.verify_request(request, scopes=scopes),
        str('verify_request'))

    config.add_request_method(
        lambda request: duplicate_params,
        str("duplicate_params"),
        property=True
    )

    for name in OAUTH_PARAMS:
        config.add_oauth_param(str(name))
