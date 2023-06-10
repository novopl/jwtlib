from jwtlib.exc import JwtError


class FakeError(JwtError):
    msg = "fake-error-msg"


def test_uses_msg_from_the_exception_class():
    err = FakeError()

    assert str(err) == 'fake-error-msg'


def test_can_append_detail_using_exception_ctor():
    class FakeError(JwtError):
        msg = "fake-error-msg"

    err = FakeError(detail='error-detail')

    assert str(err) == 'fake-error-msg: error-detail'
