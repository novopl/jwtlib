# -*- coding: utf-8 -*-
""" Flask integration

As long as you don't import from here, flask is not a dependency of jwtlib.
"""

# stdlib imports
from collections import OrderedDict
from datetime import timedelta
from functools import wraps
from logging import getLogger
from typing import Any, Dict, Sequence, Tuple, Union
from types import FunctionType

# 3rd party imports
import flask

# local imports
from . import Jwt
from .exc import JwtError
from .types import PlainType, Decorator


# Flask related types. Kept here so jwtlib doesn't have to depend on flask as
# long as the user does not import this module.
FlaskResponseData = Union[flask.Response, str]
FlaskResponseStatus = int
FlaskException = Any
FlaskResponseHeaders = Union[
    Dict[str, PlainType],
    Sequence[Tuple[str, PlainType]]
]
FlaskViewResult = Union[
    FlaskResponseData,
    Tuple[FlaskResponseData, FlaskResponseStatus],
    Tuple[FlaskResponseData, FlaskResponseHeaders],
    Tuple[FlaskResponseData, FlaskResponseStatus, FlaskResponseHeaders]
]


L = getLogger(__name__)


class JwtFlask(Jwt):
    def init_app(self, app: flask.Flask) -> None:
        # Load configuration from app.config and setup flask handlers
        conf_mapping = [
            ('JWT_HEADER_PREFIX', 'header_prefix', lambda x: x),
            ('JWT_TOKEN_TTL', 'token_ttl', lambda x: timedelta(seconds=x)),
            ('JWT_NOT_BEFORE', 'not_before', lambda x: timedelta(seconds=x)),
            ('JWT_ALGORITHM', 'algorithm', lambda x: x),
            ('JWT_VERIFY_CLAIMS', 'verify_claims', lambda x: x),
            ('JWT_REQUIRE_CLAIMS', 'require_claims', lambda x: x),
            ('JWT_LEEWAY', 'leeway', lambda x: x),
            ('SECRET', 'secret_key', lambda x: x),
        ]
        for name, attr, deserializer in conf_mapping:
            if name in app.config:
                setattr(self, attr, deserializer(app.config[name]))

        app.errorhandler(self.Error)(self._flask_exc_handler)
        app.after_request(self._flask_after_request)

    def user_required(self) -> Decorator:
        def decorator(fn: FunctionType) -> FunctionType:
            @wraps(fn)
            def wrapper(*args, **kw) -> FlaskViewResult:
                user = self.authorize(flask.request.headers.get('Authorization'))

                if user is None:
                    raise self.UserNotFoundError()

                flask.g.user = user

                return fn(*args, **kw)

            return wrapper
        return decorator

    def _flask_exc_handler(self, exc: JwtError) -> FlaskViewResult:
        L.exception(exc)

        return flask.jsonify(OrderedDict([
            ('status_code', exc.status),
            ('error', exc.error),
            ('detail', exc.message),
        ])), exc.status, exc.headers

    def _flask_after_request(self, response: flask.Response) -> flask.Response:
        # Only return refreshed token for API calls that already supplied one
        # in the request..
        if (
                response.content_type == 'application/json' and
                hasattr(flask.request, 'user') and
                flask.request.user is not None and
                'Authorization' in flask.request.headers
        ):
            token = self.generate_token(flask.request.user)
            response.headers['X-JWT-Token'] = token

        return response
