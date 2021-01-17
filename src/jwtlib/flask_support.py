""" Flask integration

As long as you don't import from here, flask is not a dependency of jwtlib.
"""

# stdlib imports
from collections import OrderedDict
from datetime import timedelta
from functools import wraps
from logging import getLogger
from typing import Any, Callable, Dict, Sequence, Tuple, Union
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
    """ A helper class that provides a basic jwtlib integration with Flask. """
    def init_app(self, app: flask.Flask, rolling_session=True) -> None:
        """ Initialize JWT from a flask app.
        This will internally call `init_config()` and `register_handlers()`. If
        you need more control over JWT initialization you can skip this method
        and call the ones mentioned above manually.

        Args:
            app (flask.Flask):
                Flask application we want to setup the handlers for.
            rolling_session (bool):
                If set to **True** this method will register an after request
                handler that will inject a refreshed token into the response
                headers if the user is logged in.

        """
        self.init_config(app)
        self.register_handlers(app, rolling_session=rolling_session)

    def init_config(self, app: flask.Flask) -> None:
        """ Initialize JWT using flask config. """
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

    def register_handlers(self, app: flask.Flask, rolling_session=True) -> None:
        """ Register flask handlers.

        Args:
            app (flask.Flask):
                Flask application we want to setup the handlers for.
            rolling_session (bool):
                If set to **True** this method will register an after request
                handler that will inject a refreshed token into the response
                headers if the user is logged in.
        """
        app.errorhandler(self.Error)(self.exc_handler)
        if rolling_session:
            app.after_request(self.rolling_session_after_request)

    def user_required(self) -> Decorator:
        """ Guard views so they return 401 if the user is missing. """
        # pylint: disable=missing-docstring
        def decorator(fn: FunctionType) -> Callable[..., Any]:
            @wraps(fn)
            def wrapper(*args, **kw) -> FlaskViewResult:
                user = self.authorize(flask.request.headers.get('Authorization'))

                if user is None:
                    raise self.UserNotFoundError()

                flask.g.user = user

                return fn(*args, **kw)

            return wrapper
        return decorator

    def exc_handler(self, exc: JwtError) -> FlaskViewResult:
        """ Flask exception handler for JwtError exceptions. """
        L.exception(exc)

        return flask.jsonify(OrderedDict([
            ('status_code', exc.status),
            ('error', exc.error),
            ('detail', exc.message),
        ])), exc.status, exc.headers

    def rolling_session_after_request(
        self,
        response: flask.Response
    ) -> flask.Response:
        """ An after request flask handler adding support for rolling sessions. """
        # Only return refreshed token for API calls that already supplied one
        # in the request..
        if (
            response.content_type == 'application/json'
            and hasattr(flask.g, 'user')
            and flask.g.user is not None
            and 'Authorization' in flask.request.headers
        ):
            token = self.generate_token(flask.g.user)
            response.headers['X-JWT-Token'] = token

        return response
