from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from threading import local

from django.contrib.auth import get_user_model

_state = local()
_UserModel = get_user_model()


def get_role_audit_actor():
    return getattr(_state, "actor", None)


def set_role_audit_actor(actor: _UserModel | None) -> None:
    _state.actor = actor


@contextmanager
def role_audit_actor(actor: _UserModel | None) -> Generator[None]:
    previous = get_role_audit_actor()
    set_role_audit_actor(actor)
    try:
        yield
    finally:
        set_role_audit_actor(previous)


class RoleAuditActorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        actor = request.user if request.user.is_authenticated else None
        with role_audit_actor(actor):
            return self.get_response(request)
