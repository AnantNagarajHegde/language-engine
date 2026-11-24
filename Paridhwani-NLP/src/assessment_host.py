"""Explicit local HTTP host; importing/testing this module opens no sockets."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from assessment import AssessmentBoundary, MAX_BODY_BYTES
from matcher import AnswerMatcher

ROUTE = '/v1/assessment/evaluate'


def respond(boundary, path, content_type, body):
    if path != ROUTE:
        return 404, b'{"error":"not_found"}'
    if content_type.lower().replace(' ', '') not in ('application/json', 'application/json;charset=utf-8'):
        return 415, b'{"error":"content_type"}'
    if len(body) > MAX_BODY_BYTES:
        return 413, b'{"error":"body_limit"}'
    return 200, boundary.handle_json(body)


def handler_for(boundary):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(7)
        def log_message(self, *_): pass
        def do_POST(self):
            try:
                self.connection.settimeout(7)
                lengths = self.headers.get_all('Content-Length', [])
                types = self.headers.get_all('Content-Type', [])
                if len(lengths) != 1 or len(types) != 1 or self.headers.get('Transfer-Encoding') or self.headers.get('Content-Encoding'):
                    self.send_error(400); return
                count = int(lengths[0])
                if not 0 <= count <= MAX_BODY_BYTES:
                    self.send_error(413); return
                body = self.rfile.read(count)
                if len(body) != count:
                    self.send_error(400); return
                status, reply = respond(boundary, self.path, types[0], body)
                self.send_response(status)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(reply)))
                self.end_headers(); self.wfile.write(reply)
            except (ValueError, TimeoutError, OSError):
                self.close_connection = True
    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--serve', action='store_true', help='Explicitly bind local development port')
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    if not args.serve: parser.error('--serve is required; no automatic listener')
    if not 1 <= args.port <= 65535: parser.error('invalid port')
    boundary = AssessmentBoundary(AnswerMatcher(Path(__file__).resolve().parents[1]/'data'))
    # Fixed literal loopback only; no wildcard interface or network settings changes.
    with HTTPServer(('127.0.0.1', args.port), handler_for(boundary)) as server:
        print('Assessment v1 local host; content_revision=' + boundary.content_revision, flush=True)
        server.serve_forever()


if __name__ == '__main__': main()
