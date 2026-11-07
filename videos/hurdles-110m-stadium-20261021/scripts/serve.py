from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import os
p=Path(__file__).resolve().parents[1]
os.chdir(p)
print('110m hurdles preview: http://localhost:8110/outputs/hurdle-110.html',flush=True)
ThreadingHTTPServer(('127.0.0.1',8110),partial(SimpleHTTPRequestHandler,directory=str(p))).serve_forever()
