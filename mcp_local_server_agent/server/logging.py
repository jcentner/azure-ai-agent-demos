# server/logging.py
from __future__ import annotations

import contextvars
import logging
import time
import uuid

_request_id = contextvars.ContextVar("request_id", default="-")


class RequestContext(logging.Filter):
    def filter(self, record):
        record.request_id = _request_id.get("-")
        return True


def setup_logging(level: str = "info") -> None:
    lvl = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=lvl,
        format="%(asctime)s %(levelname)s %(request_id)s %(name)s :: %(message)s",
    )
    for h in logging.getLogger().handlers:
        h.addFilter(RequestContext())


def new_request_id() -> str:
    rid = uuid.uuid4().hex[:12]
    _request_id.set(rid)
    return rid


def timeit(fn):
    def _wrap(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            dt = (time.perf_counter() - t0) * 1000
            logging.getLogger(fn.__module__).debug(
                "duration_ms=%0.2f fn=%s", dt, fn.__name__
            )
    return _wrap
