#!/usr/bin/env python3
"""Loopback-only local output server, with byte ranges for MP4 seeking."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]/'outputs'

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def send_head(self):
        self.remaining=None
        path=Path(self.translate_path(self.path))
        requested=self.headers.get('Range')
        if not requested or not path.is_file():
            return super().send_head()
        size=path.stat().st_size
        match=re.fullmatch(r'bytes=(\d*)-(\d*)',requested)
        if not match:
            self.send_error(416); return None
        first,last=match.groups()
        start=int(first) if first else max(0,size-int(last))
        end=min(int(last),size-1) if first and last else size-1
        if start>=size or end<start:
            self.send_error(416); return None
        handle=path.open('rb');handle.seek(start)
        self.send_response(206)
        self.send_header('Content-Type',self.guess_type(str(path)))
        self.send_header('Accept-Ranges','bytes')
        self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length',str(end-start+1));self.end_headers()
        self.remaining=end-start+1
        return handle
    def copyfile(self,source,outputfile):
        if self.remaining is None:
            return super().copyfile(source,outputfile)
        while self.remaining:
            data=source.read(min(self.remaining,256*1024))
            if not data: break
            outputfile.write(data);self.remaining-=len(data)

print('U-Net player: http://localhost:3211/preview.html',flush=True)
ThreadingHTTPServer(('127.0.0.1',3211),Handler).serve_forever()
