from mock import MagicMock, patch
from pyramid import testing
from pyramid.interfaces import IRequestExtensions
import pytest


class MockGrant(MagicMock):
    pass


class MockResponse(MagicMock):
    pass


class MockToken(MagicMock):
    def estimate_type(self, request):
        return 5


@pytest.fixture(scope='function')
def config(request):
    config = testing.setUp()
    config.include('pyramid_oauthlib')
    request.addfinalizer(testing.tearDown)
    return config


def test_server_registration(config):
    assert config.registry.oauth is not None


def test_grant_types(config):
    from oauthlib.oauth2 import ImplicitGrant, RequestValidator
    from pyramid_oauthlib import Server
    server = config.registry.oauth
    validator = RequestValidator()

    config.add_grant_type(MockGrant, request_validator=validator)
    config.add_grant_type('oauthlib.oauth2.ImplicitGrant', 'implicit')

    default = server.default_grant_type_handler
    assert validator is default.request_validator
    assert default is server.grant_types['']
    assert isinstance(server.grant_types[''], MockGrant)
    assert isinstance(server.grant_types['implicit'], ImplicitGrant)

    with pytest.raises(AttributeError):
        request = testing.DummyRequest()
        request.grant_type = None
        server.create_token_response(request)

    with patch.object(Server, 'default_token_type') as token:
        request = testing.DummyRequest()
        request.grant_type = None
        server.create_token_response(request, credentials={'userid': 'jill'})
        assert default.create_token_response.called_with(request, token)
        assert request.extra_credentials == {'userid': 'jill'}

        with patch.object(ImplicitGrant, 'create_token_response') as g:
            request.grant_type = 'implicit'
            server.create_token_response(request)
            assert g.called_with(request, token)


def test_response_types(config):
    from oauthlib.oauth2 import ImplicitGrant, RequestValidator
    from pyramid_oauthlib import Server
    server = config.registry.oauth
    validator = RequestValidator()

    config.add_response_type(MockResponse, request_validator=validator)
    config.add_response_type('oauthlib.oauth2.ImplicitGrant', 'token')

    default = server.default_response_type_handler
    assert validator is default.request_validator
    assert default is server.response_types['']
    assert isinstance(server.response_types[''], MockResponse)
    assert isinstance(server.response_types['token'], ImplicitGrant)

    with pytest.raises(AttributeError):
        request = testing.DummyRequest()
        request.response_type = None
        server.create_authorization_response(request)

    with patch.object(Server, 'default_token_type') as token:
        request = testing.DummyRequest()
        request.response_type = None
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

        with patch.object(ImplicitGrant, 'create_authorization_response') as r:
            request.grant_type = 'implicit'
            server.create_authorization_response(request)
            assert r.called_with(request, token)


def test_token_types(config):
    from oauthlib.oauth2 import BearerToken, RequestValidator
    server = config.registry.oauth
    validator = RequestValidator()

    config.add_token_type(MockToken, request_validator=validator)
    config.add_token_type('oauthlib.oauth2.BearerToken', 'Bearer')

    default = server.default_token_type_handler
    assert validator is default.request_validator
    assert default is server.tokens['']
    assert server.tokens[''] is default
    assert isinstance(server.tokens[''], MockToken)
    assert isinstance(server.tokens['Bearer'], BearerToken)

    request = testing.DummyRequest()
    request.access_token = 'feedfeed'
    request.token_type = None
    server.verify_request(request, scopes=['foo'])
    call = default.validate_request
    assert call.called_with(request)
    assert request.scopes == ['foo']

    with patch.object(validator, 'validate_bearer_token') as token_validator:
        request.authorization = 'Bearer deadbeef'
        server.verify_request(request, scopes=['bar'])
        call = server.tokens['Bearer'].validate_request
        assert token_validator.called_with('deadbeef', ['bar'], request)


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
            assert impl.called_with(request, **kw)
