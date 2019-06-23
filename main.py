from aiohttp import web

from routes import routes
from db import init_conn, close_conn

app = web.Application()
app.add_routes(routes)
app.on_startup.append(init_conn)
app.on_cleanup.append(close_conn)
web.run_app(app)
