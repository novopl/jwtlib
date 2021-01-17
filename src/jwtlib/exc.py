""" Exception classes used by jwtlib. """


class JwtError(Exception):
    """ Base exception class for all exceptions thrown by jwtlib. """
    error = 'Generic Error'
    message = 'Unknown error'
    status = 401

    def __init__(self, message=None, headers=None, status=None):
        self.error = self.__class__.error or JwtError.error
        self.message = message or self.__class__.message
        self.status = status or self.__class__.status
        self.headers = headers

    def __repr__(self):
        return '<JwtError: {}>'.format(self.error)

    def __str__(self):
        return 'JwtError: {}: {}'.format(self.error, self.message)


class AuthHeaderMissingError(JwtError):
    """ Raised if authorization header is missing. """
    error = 'Authorization Header Missing'
    message = "You should set 'Authorization: Token <token>' header."


class BadAuthHeaderError(JwtError):
    """ Authorization header cannot be parsed. """
    error = 'Bad Authorization header'
    message = 'Bad Authorization header'


class ClaimMissing(JwtError, ValueError):
    """ Required claim is missing from the token. """
    error = 'JWT Claim Missing'


class InvalidTokenError(JwtError):
    """ Generic exception for situations where the given toke nis not valid. """
    error = "Not Authorized"


class NotAuthorizedError(JwtError):
    """ User is not authorized to perform the given action. """
    error = "Not Authorized"


class UserNotFoundError(JwtError):
    """ User represented by the token was not found

    User may have been deleted since the token was issued.
    """
    error = 'User Not Found'
    message = 'User does not exist'


class TokenExpired(JwtError):
    """ The token passed to .authorize() is expired. """
    error = 'Token expired'
    message = 'Token expired'
