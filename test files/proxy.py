from aiohttp import web

async def hello(request):
    print(request)

    print(await request.read())
    print(request.match_info)
    print(request.rel_url)
    return web.Response(text="Hello, world")


app = web.Application()
app.add_routes([web.get('/', hello)])
web.run_app(app)
