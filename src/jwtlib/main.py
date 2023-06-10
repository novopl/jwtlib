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

from datetime import datetime, timedelta
from logging import getLogger
from typing import Any, Generic, Optional, TypeVar

from jwt import ExpiredSignatureError
from jwt import InvalidTokenError as PyJwtInvalidTokenError
from jwt import PyJWT

from . import exc
from .abstract import UserAdapterBase
from .types import JsonDict, TokenPayload


T = TypeVar('T')
L = getLogger(__name__)
User = Any      # We support any user class.


class JwtLib(Generic[T]):
    """ Base class implementing JWT support. """
    # For easier access
    Error = exc.JwtError

    AuthHeaderMissing = exc.AuthHeaderMissing
    ClaimMissing = exc.ClaimMissing
    BadAuthHeader = exc.BadAuthHeader
    InvalidToken = exc.InvalidToken
    NotAuthorized = exc.NotAuthorized
    UserNotFound = exc.UserNotFound
    TokenExpired = exc.TokenExpired

    def __init__(
        self,
        secret: Optional[str] = None,
        user_adapter: Optional[UserAdapterBase] = None,
    ):
        self.user_adapter = user_adapter
        self.pyjwt = PyJWT()
        self.header_prefix = 'Bearer'
        self.token_ttl = timedelta(seconds=300)
        self.not_before = timedelta(seconds=0)
        self.algorithm = 'HS256'
        self.verify_claims = ['signature', 'exp', 'iat', 'nbf']
        self.require_claims = ['exp', 'iat', 'nbf']
        self.leeway = 0
        self.secret_key = secret

    def set_user_adapter(self, user_adapter: UserAdapterBase):
        self.user_adapter = user_adapter

    def user_payload(self, account: T) -> TokenPayload:
        if self.user_adapter:
            return self.user_adapter.payload_for_user(account)

        raise exc.UserAdapterMissing('payload_for_user')

    def user_from_payload(self, payload: TokenPayload) -> Optional[T]:
        if self.user_adapter:
            return self.user_adapter.user_for_payload(payload)

        raise exc.UserAdapterMissing('user_for_payload')

    def authorize(self, auth_header: str) -> User:
        """ Given an Authorization Header try to get the matching user.

        Args:
            auth_header:
                The full content of the 'Authorization' header as read from the
                request. The way it's stored in the request will depend on
                framework used.

        Returns:
            User: The user instance represented by the token read from *auth_header*.

        Raises:
            Jwt.BadAuthHeader:
                If the given auth header cannot be parsed. This is either if
                the Authorization header is completely wrong or the header
                prefix does not match whatever is set in `Jwt.header_prefix`
            Jwt.InvalidToken:
                Cannot decode the JWT token.
            Jwt.UserNotFound:
                User represented by the token was not found. This might happen
                if the user is deleted after the token is issued but before it
                expires.
        """

        token = self.get_token_from_header(auth_header)
        return self.authorize_token(token)

    def authorize_token(self, token: str) -> User:
        """ Get user for a given token.

        This method can be useful if the token is not coming from an HTTP header but
        other means (like websockets).

        Args:
            token:
                JWT token representing a user. This actually only stores the user
                ID, the actual user is retrievieved with `user_from_payload()` method.

        Returns:
            A user corresponding to the given token (if it's valid).

        Raises:
            Jwt.InvalidToken:
                If the token can't be decoded.
            Jwt.UserNotFound:
                If the user ID stored in the token cannot be found
                (.user_from_payload() call returned ``None``).
        """
        try:
            payload = self.decode_token(token)
        except PyJwtInvalidTokenError:
            raise self.InvalidToken(f"Failed to decode token '{token}'")

        user = self.user_from_payload(payload)
        if user is None:
            raise self.UserNotFound()

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
            raise self.BadAuthHeader(
                f"Bad auth header: '{parts[0]}', expected '{self.header_prefix}'"
            )
        elif len(parts) == 1:
            raise self.InvalidToken("Missing or empty token")

        return parts[1]

    def generate_token(self, user: Optional[User]) -> str:
        """ Generate JWT token for the given user. """
        if user is None:
            raise self.NotAuthorized("No user to generate token for")

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
                token,
                key=self.secret_key,
                options=opts,
                algorithms=[self.algorithm],
                leeway=self.leeway
            )
        except ExpiredSignatureError:
            raise self.TokenExpired()
