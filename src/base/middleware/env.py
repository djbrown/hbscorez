from base import models


def _ensure_env(name: str, default: models.Value, force: bool = False) -> models.Env:
    matches = models.Env.objects.filter(name=name)
    if matches.exists():
        match = matches[0]
        if force and match.value is not default.value:
            match.set_value(default)
        return match

    return models.Env.objects.create(name=name, value=default.value)


UPDATING = _ensure_env("UPDATING", models.Value.FALSE)


class EnvironmentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        request.env = {env.name: env.value for env in models.Env.objects.all()}
        request.global_message = models.GlobalMessage.objects.first()

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
