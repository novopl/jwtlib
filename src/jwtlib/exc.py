""" Exception classes used by jwtlib. """
from typing import Optional


class JwtError(Exception):
    msg: str

    def __init__(self, detail: Optional[str] = None, **kw):
        super(JwtError, self).__init__(self.msg + (f": {detail}" if detail else ""))

        self.detail = detail
        self.err_kwargs = kw


class AuthHeaderMissingError(JwtError):
    msg = 'Authorization Header Missing'


class BadAuthHeaderError(JwtError):
    msg = 'Bad Authorization header'


class ClaimMissing(JwtError, ValueError):
    msg = 'JWT Claim Missing'


class InvalidTokenError(JwtError):
    msg = "Not Authorized"


class NotAuthorizedError(JwtError):
    msg = "Not Authorized"


class UserNotFoundError(JwtError):
    msg = 'User Not Found'


class TokenExpired(JwtError):
    msg = 'Token expired'
