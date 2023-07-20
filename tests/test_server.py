# /path/to/server.py

from sanic import Sanic
from sanic.response import text
import multiprocessing as mp
# Sanic.start_method = "fork"
app = Sanic("test")

@app.get("/")
def return_hello(request):
    return text("hello")


if __name__ == '__main__':
    mp.freeze_support()

    app.run(host='0.0.0.0', port=8080, access_log=False, workers=1)
