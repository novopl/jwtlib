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
__version__ = '0.1.6'

from datetime import datetime, timedelta
from logging import getLogger
from typing import Any, Dict, Optional

from jwt import PyJWT, InvalidTokenError as PyJwtInvalidTokenError, ExpiredSignatureError


from . import exc


L = getLogger(__name__)
User = Any      # We support any user class.
JsonDict = Dict[str, Any]


class Jwt(object):
    """ Base class implementing JWT support. """
    # For easier access
    Error = exc.JwtError

    AuthHeaderMissingError = exc.AuthHeaderMissingError
    ClaimMissing = exc.ClaimMissing
    BadAuthHeaderError = exc.BadAuthHeaderError
    InvalidTokenError = exc.InvalidTokenError
    NotAuthorizedError = exc.NotAuthorizedError
    UserNotFoundError = exc.UserNotFoundError
    TokenExpired = exc.TokenExpired

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

    def authorize(self, auth_header: Optional[str]) -> User:
        """ Given an Authorization Header try to get the matching user.

        Args:
            auth_header (Optional[str]):
                The full content of the 'Authorization' header as read from the
                request. The way it's stored in the request will depend on
                framework used.

        Returns:
            User: The user instance represented by the token read from *auth_header*.

        Raises:
            Jwt.AuthHeaderMissingError:
                If the given auth header is empty or `None`.
            Jwt.BadAuthHeaderError:
                If the given auth header cannot be parsed. This is either if
                the Authorization header is completely wrong or the header
                prefix does not match whatever is set in `Jwt.header_prefix`
            Jwt.InvalidTokenError:
                Cannot decode the JWT token.
            Jwt.UserNotFoundError:
                User represented by the token was not found. This might happen
                if the user is deleted after the token is issued but before it
                expires.
        """
        if not auth_header:
            raise self.AuthHeaderMissingError()

        token = self.get_token_from_header(auth_header)
        try:
            payload = self.decode_token(token)
        except PyJwtInvalidTokenError:
            raise self.InvalidTokenError(f"Failed to decode token '{token}'")

        # Convert token payload to user it represents
        user = self.user_from_payload(payload)
        if user is None:
            raise self.UserNotFoundError()

        return user

    def get_token_from_header(self, auth_header: str) -> str:
        """ Parse auth header and extract the token

        Args:
            auth_header:
                The content of the auth header as received with in the request.

        Returns:
            The JWT token stored in the header
        """
        # Verify the token is in the right format
        parts = auth_header.split()
        if parts[0] != self.header_prefix:
            raise self.BadAuthHeaderError(
                f"Bad auth header: '{parts[0]}', expected '{self.header_prefix}'"
            )
        elif len(parts) == 1:
            raise self.InvalidTokenError("Missing or empty token")

        return parts[1]

    def user_payload(self, user) -> JsonDict:
        """ Return payload for the given user.

        This method must be implemented by the subclasses in order to integrate
        with any storage used by the project (jwtlib itself is framework
        agnostic).
        """
        raise NotImplementedError("user_payload() method must be implemented")

    def user_from_payload(self, payload: JsonDict) -> User:
        """ Return a user for the given JWT payload.

        This method must be implemented by the subclasses in order to integrate
        with any storage used by the project (jwtlib itself is framework
        agnostic).

        This method is the opposite of `user_payload`.
        """
        raise NotImplementedError("user_from_payload() method must be implemented")

    def generate_token(self, user: Optional[User]) -> str:
        """ Generate JWT token for the given user. """
        if user is None:
            raise self.NotAuthorizedError("No user to generate token for")

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
        """ Create general JWT token headers.

        This method can be overloaded in subclasses to customize the way tokens
        are generated.
        """
        return None

    def create_payload(self) -> JsonDict:
        """ Create core JWT payload.

        This will contain the fields that are required by JWT like expiration
        and will be included in every token generated.

        Be careful when you overload this method in subclasses as you will have
        to take care of including the necessary fields or the jwtlib will break.
        """
        iat = datetime.utcnow()

        return {
            'iat': iat,
            'exp': iat + self.token_ttl,
            'nbf': iat + self.not_before,
        }

    def decode_token(self, token: str) -> JsonDict:
        """ Decode the token and return it's payload. """
        opts = {'require_' + claim: True for claim in self.require_claims}
        opts.update({'verify_' + claim: True for claim in self.verify_claims})

        try:
            return self.pyjwt.decode(
                token, self.secret_key,
                options=opts,
                algorightms=[self.algorithm],
                leeway=self.leeway
            )
        except ExpiredSignatureError:
            raise self.TokenExpired()
