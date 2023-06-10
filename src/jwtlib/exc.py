""" Exception classes used by jwtlib. """
from typing import Optional


class JwtError(Exception):
    msg: str

    def __init__(self, detail: Optional[str] = None, **kw):
        super(JwtError, self).__init__(self.msg + (f": {detail}" if detail else ""))

        self.detail = detail
        self.err_kwargs = kw


class AuthHeaderMissing(JwtError):
    msg = 'Authorization Header Missing'


class BadAuthHeader(JwtError):
    msg = 'Bad Authorization header'


class ClaimMissing(JwtError, ValueError):
    msg = 'JWT Claim Missing'


class InvalidToken(JwtError):
    msg = "Not Authorized"


class NotAuthorized(JwtError):
    msg = "Not Authorized"


class UserNotFound(JwtError):
    msg = 'User Not Found'


class TokenExpired(JwtError):
    msg = 'Token expired'


class UserAdapterMissing(JwtError):
    msg = "User adapter is not configured."
