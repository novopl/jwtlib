# -*- coding: utf-8 -*-


class JwtError(Exception):
    error = 'Generic Error'
    message = 'Unknown error'
    status = 401

    def __init__(self, message=None, headers=None):
        self.error = self.__class__.error or JwtError.error
        self.message = message or self.__class__.message
        self.status = self.__class__.status
        self.headers = headers

    def __repr__(self):
        return 'JwtError: {}'.format(self.error)

    def __str__(self):
        return 'JwtError: {}: {}'.format(self.error, self.message)


class AuthHeaderMissingError(JwtError):
    error = 'Authorization Header Missing'
    message = "You should set 'Authorization: Token <token>' header."


class BadAuthHeaderError(JwtError):
    error = 'Bad Authorization header'
    message = 'Bad Authorization header'


class ClaimMissing(JwtError, ValueError):
    error = 'JWT Claim Missing'


class InvalidTokenError(JwtError):
    error = "Not Authorized"


class NotAuthorizedError(JwtError):
    error = "Not Authorized"


class UserNotFoundError(JwtError):
    error = 'User Not Found'
    message = 'User does not exist'
