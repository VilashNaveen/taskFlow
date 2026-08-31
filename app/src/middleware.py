import asyncio

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class InFlightMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._inflight = 0
        self._event = asyncio.Event()
        self._event.set()

    async def dispatch(self, request: Request, call_next):
        self._inflight += 1
        if self._inflight > 0:
            self._event.clear()
        try:
            response = await call_next(request)
            return response
        finally:
            self._inflight -= 1
            if self._inflight == 0:
                self._event.set()

    async def wait_for_zero(self):
        await self._event.wait()

