import dataclasses
from typing import Generator

import pytest

from jwtlib import exc
from jwtlib.main import JwtLib, TokenPayload


@dataclasses.dataclass
class User:
    id: str
    username: str


USERS_DB = {
    '1': User(id='1', username='user-1'),
    '2': User(id='2', username='user-2'),
    '3': User(id='3', username='user-3'),
}


@pytest.fixture(scope='session')
def jwt() -> Generator[JwtLib, None, None]:
    class TestJwt(JwtLib):
        def __init__(self, *args, **kw):
            super(TestJwt, self).__init__(*args, **kw)

            self.secret_key = 'long-random-string-as-the-secret-key'
            self.users = {
                '1': User(id='1', username='user-1'),
                '2': User(id='2', username='user-2'),
                '3': User(id='3', username='user-3'),
            }

        def user_payload(self, user) -> TokenPayload:
            return {
                'id': user.id,
            }

        def user_from_payload(self, payload: TokenPayload) -> User:
            if user := USERS_DB.get(payload['id']):
                return user
            raise exc.UserNotFound()

    yield TestJwt()


def test_can_generate_token_and_decode_them(jwt):
    user = User(id='1', username='john')
    token = jwt.generate_token(user)

    payload = jwt.decode_token(token)

    assert payload['id'] == user.id


def test_raises_NotAuthorized_when_trying_to_generate_token_for_empty_user(jwt):
    with pytest.raises(exc.NotAuthorized):
        jwt.generate_token(None)


def test_can_authorize_user_directly_from_token(jwt):
    user = USERS_DB['1']
    token = jwt.generate_token(user)

    authenticated_user = jwt.authorize_token(token)

    assert authenticated_user == user
    assert authenticated_user is user


def test_raises_InvalidToken_if_the_token_cant_be_decoded(jwt):
    with pytest.raises(exc.InvalidToken):
        jwt.authorize_token('invalid-token')


def test_raises_UserNotFound_if_the_user_is_missing(jwt):
    user = User(id='5', username='bob')
    token = jwt.generate_token(user)

    with pytest.raises(exc.UserNotFound):
        jwt.authorize_token(token)


def test_can_authorize_from_an_auth_header(jwt):
    user = USERS_DB['1']
    header = f'{jwt.header_prefix} {jwt.generate_token(user)}'

    authenticated_user = jwt.authorize(header)

    assert authenticated_user == user
    assert authenticated_user is user


def test_raises_BadAuthHeader_for_invalid_header_prefix(jwt):
    user = USERS_DB['1']
    header = f'InvalidPrefix {jwt.generate_token(user)}'

    with pytest.raises(exc.BadAuthHeader):
        jwt.authorize(header)


def test_raises_InvalidToken_if_the_token_is_missing(jwt):
    header = f'{jwt.header_prefix}'

    with pytest.raises(exc.InvalidToken):
        jwt.authorize(header)
