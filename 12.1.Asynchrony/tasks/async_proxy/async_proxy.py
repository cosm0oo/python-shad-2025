import aiohttp
from aiohttp import web
from yarl import URL


async def proxy_handler(request: web.Request) -> web.Response:
    """
    Check request contains http url in query args:
        /fetch?url=http%3A%2F%2Fexample.com%2F
    and trying to fetch it and return body with http status.
    If url passed without scheme or is invalid raise 400 Bad request.
    On failure raise 502 Bad gateway.
    :param request: aiohttp.web.Request to handle
    :return: aiohttp.web.Response
    """
    url_str: str | None = request.query.get("url")  # pyrefly: ignore  # missing-attribute
    if not url_str:
        raise web.HTTPBadRequest(text="No url to fetch")
    try:
        url = URL(url_str)
    except Exception:
        raise web.HTTPBadRequest(text="Empty url scheme")

    if not url.scheme:
        raise web.HTTPBadRequest(text="Empty url scheme")

    if url.scheme not in ("http", "https"):
        raise web.HTTPBadRequest(text=f"Bad url scheme: {url.scheme}")

    session = request.app["session"]
    try:
        async with session.get(str(url)) as response:
            body = await response.read()
            return web.Response(body=body, status=response.status)
    except Exception:
        raise web.HTTPBadGateway()


async def setup_application(app: web.Application) -> None:
    """
    Setup application routes and aiohttp session for fetching
    :param app: app to apply settings with
    """
    app["session"] = aiohttp.ClientSession()
    app.router.add_get("/fetch", proxy_handler)


async def teardown_application(app: web.Application) -> None:
    """
    Application with aiohttp session for tearing down
    :param app: app for tearing down
    """
    await app["session"].close()
