import base64
import logging
import re

logger = logging.getLogger(__name__)


class Route:
    def __init__(self, *args, **query):
        self.args = [str(i) for i in args]
        self.query = query

    def __str__(self):
        path = "/".join(self.args)
        raw_query = [f"{k}={v}" for k, v in self.query.items()]
        query = "&".join(raw_query)
        return path + (f"?{query}" if query else "")

    @classmethod
    def decode(cls, row: str) -> "Route":
        path, query = row.split("?")
        args = path.split("/")
        query_kwargs = query.split("&")
        kwargs = dict(i.split("=") for i in query_kwargs)
        return cls(*args, **kwargs)

    @classmethod
    def b64decode(self, row: str):
        # TODO: Вернуть Route
        return base64.urlsafe_b64decode(row.encode("ascii")).decode()

    def b64encode(self):
        return base64.urlsafe_b64encode(str(self).encode("ascii")).decode("ascii")


class Router:
    def __init__(self):
        self.routes = {}

    def add_method(self, regexp):
        def wrapper(fn):
            self.routes.update({regexp: fn})
            return fn

        return wrapper

    def get_handler(self, path: str):
        for regexp in self.routes.keys():
            if re.findall(regexp, path):
                return self.routes[regexp], re.search(regexp, path).groups()
        else:
            logger.warning("Not found")


router = Router()
