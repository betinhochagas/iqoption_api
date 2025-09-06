class ApiError(Exception):
    """Erro base da IQOption API."""
    pass


class NetworkError(ApiError):
    def __init__(self, message, url=None):
        super().__init__(message)
        self.url = url


class HttpError(ApiError):
    def __init__(self, status_code, message, url=None, body=None):
        super().__init__(message)
        self.status_code = status_code
        self.url = url
        self.body = body


class AuthError(HttpError):
    pass


class NotFoundError(HttpError):
    pass


class RateLimitError(HttpError):
    pass


class ServerError(HttpError):
    pass


class TimeoutError(ApiError):
    pass


def from_http_response(response, exc=None):
    code = getattr(response, "status_code", None)
    url = getattr(response, "url", None)
    text = None
    try:
        text = response.text
    except Exception:
        text = None

    message = f"HTTP {code} for {url}"
    if code == 401 or code == 403:
        return AuthError(code, message, url=url, body=text)
    if code == 404:
        return NotFoundError(code, message, url=url, body=text)
    if code == 429:
        return RateLimitError(code, message, url=url, body=text)
    if code and 500 <= code:
        return ServerError(code, message, url=url, body=text)
    return HttpError(code or -1, message, url=url, body=text)

