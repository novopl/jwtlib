# -*- coding: utf-8 -*-
""" JWT implementation

Custom token TTL per user
-------------------------

The user payload returned by `Jwt.user_payload()` method will overwrite the
default values created by `Jwt.create_payload()` if the keys overlap. This
allows the specific in-app sublcass of Jwt to specify ``exp`` claim based on
the user settings fetched from the database. This makes it easy to implement
different classes of users like *regular* and *system* each with it's own
token TTL.
"""
__version__ = '0.0.2'

# stdlib imports
from datetime import datetime, timedelta
from logging import getLogger
from typing import Any, Dict, Optional

# 3rd party imports
from jwt import PyJWT, InvalidTokenError as PyJwtInvalidTokenError

# local imports
from . import exc


L = getLogger(__name__)
User = Any      # We support any user class.
JsonDict = Dict[str, Any]


class Jwt(object):
    # For easier access
    Error = exc.JwtError

    AuthHeaderMissingError = exc.AuthHeaderMissingError
    ClaimMissing = exc.ClaimMissing
    BadAuthHeaderError = exc.BadAuthHeaderError
    InvalidTokenError = exc.InvalidTokenError
    NotAuthorizedError = exc.NotAuthorizedError
    UserNotFoundError = exc.UserNotFoundError

    def __init__(self):
        self.pyjwt = PyJWT()
        self.header_prefix = 'JWT'
        self.token_ttl = timedelta(seconds=300)
        self.not_before = timedelta(seconds=0)
        self.algorithm = 'HS256'
        self.verify_claims = ['signature', 'exp', 'iat', 'nbf']
        self.require_claims = ['exp', 'iat', 'nbf']
        self.leeway = 0
        self.secret_key = None

    def authorize(self, auth_header: str) -> User:
        if not auth_header:
            raise self.AuthHeaderMissingError()

        parts = auth_header.split()
        if parts[0] != self.header_prefix:
            raise self.BadAuthHeaderError()
        elif len(parts) == 1:
            # Missing token
            raise self.InvalidTokenError("Missing or empty token")

        try:
            payload = self.decode_token(parts[1])
        except PyJwtInvalidTokenError:
            raise self.InvalidTokenError()

        user = self.user_from_payload(payload)

        if user is None:
            raise self.UserNotFoundError()

        return user

    def user_payload(self, user) -> JsonDict:
        raise NotImplemented("user_payload() method must be implemented")

    def user_from_payload(self, payload: JsonDict) -> User:
        raise NotImplemented("user_from_payload() method must be implemented")

    def generate_token(self, user: User) -> str:
        headers = self.create_headers()
        payload = self.create_payload()
        payload.update(self.user_payload(user))

        missing = frozenset(self.require_claims) - frozenset(payload.keys())
        if missing:
            raise self.ClaimMissing("JWT payload is missing claims: {}".format(
                ', '.join(missing)
            ))

        return self.pyjwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm,
            headers=headers
        )

    def create_headers(self) -> Optional[JsonDict]:
        return None

    def create_payload(self) -> JsonDict:
        iat = datetime.utcnow()

        return {
            'iat': iat,
            'exp': iat + self.token_ttl,
            'nbf': iat + self.not_before,
        }

    def decode_token(self, token: str) -> JsonDict:
        opts = {'require_' + claim: True for claim in self.require_claims}
        opts.update({'verify_' + claim: True for claim in self.verify_claims})

        return self.pyjwt.decode(
            token, self.secret_key,
            options=opts,
            algorightms=[self.algorithm],
            leeway=self.leeway
        )
