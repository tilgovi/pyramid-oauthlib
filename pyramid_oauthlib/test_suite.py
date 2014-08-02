import unittest

from mock import MagicMock, patch
from pyramid import testing
from pyramid.interfaces import IRequestExtensions
import pytest


@pytest.fixture(scope='function')
def config(request):
    config = testing.setUp()
    config.include('pyramid_oauthlib')
    request.addfinalizer(testing.tearDown)
    return config


def test_server_registration(config):
    assert config.registry.oauth is not None


def test_grant_types(config):
    server = config.registry.oauth
    default = MagicMock()
    auth_code = MagicMock()

    config.add_grant_type(default)
    config.add_grant_type(auth_code, 'authorization_code')

    assert server.grant_types[''] is default
    assert server.grant_types['authorization_code'] is auth_code

    from pyramid_oauthlib import Server
    with patch.object(Server, 'default_token_type') as token:
        request = testing.DummyRequest()
        request.grant_type = 'authorization_code'
        server.create_token_response(request, credentials={'userid': 'jill'})
        call = default.create_token_response
        assert call.called_with(request, token)
        assert request.extra_credentials == {'userid': 'jill'}


def test_response_types(config):
    server = config.registry.oauth
    default = MagicMock()
    auth_code = MagicMock()

    config.add_response_type(default)
    config.add_response_type(auth_code, 'code')

    assert server.response_types[''] is default
    assert server.response_types['code'] is auth_code

    request = testing.DummyRequest()
    request.response_type = 'code'

    from pyramid_oauthlib import Server

    with patch.object(Server, 'default_token_type') as token:
        server.create_authorization_response(
            request,
            scopes=['foo'],
            credentials={'userid': 'jill'},
        )
        call = default.create_authorization_response
        assert call.called_with(request, token)
        assert request.scopes == ['foo']

    server.validate_authorization_request(request)
    assert request.scopes is None
    assert default.validate_authorization_request.called_with(request)


def test_token_types(config):
    server = config.registry.oauth
    default = MagicMock()
    custom = MagicMock()

    default.estimate_type = lambda r: 0
    custom.estimate_type = lambda r: 9

    config.add_token_type(default)
    config.add_token_type(custom, 'custom')

    assert server.tokens[''] is default
    assert server.tokens['custom'] is custom

    from pyramid_oauthlib import Server

    with patch.object(Server, 'default_token_type_handler') as token:
        request = testing.DummyRequest()
        request.token_type = 'custom'
        server.verify_request(
            request,
            scopes=['foo'],
        )
        call = token.validate_request
        assert call.called_with(request)


@pytest.mark.parametrize('name,scopes,credentials', [
    ('create_authorization_response', True, True),
    # TODO: revocation
    ('create_token_response', False, True),
    ('validate_authorization_request', False, False),
    ('verify_request', True, False),
])
def test_request_methods(config, name, scopes, credentials):
    server = config.registry.oauth
    methods = config.registry.getUtility(IRequestExtensions).methods
    assert name in methods

    meth = methods[name]
    kw = {}

    if scopes:
        kw['scopes'] = ['foo']

    if credentials:
        kw['credentials'] = ['bar']

    request = testing.DummyRequest()
    with patch.object(server, name) as impl:
        with patch('pyramid_oauthlib.oauth_response'):
            meth(request, **kw)
            impl.assert_called_with(request, **kw)
