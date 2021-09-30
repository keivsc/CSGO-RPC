from http.server import BaseHTTPRequestHandler, HTTPServer
from operator import attrgetter
from threading import Thread
import json, time, traceback, os
from .payload_parser import Parser
from urllib.parse import urlparse, parse_qs
Parser = Parser()
class GSIServer(HTTPServer):
    def __init__(self, server_address, auth_token):
        super(GSIServer, self).__init__(server_address, RequestHandler)
        self.server_address = server_address
        self.auth_token = auth_token
        self.data = {'data':None}
        self.running = False

    def start_server(self):
        try:
            thread = Thread(target=self.serve_forever)
            thread.start()
            first_time = True
            while self.running == False:
                if first_time == True:
                    print("CS:GO GSI Server starting..")
                first_time = False
        except:
            print("Could not start server.")
            os._exit(1)
        
        else:
            print("GSI Server Started")


class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return
    def do_POST(self):
        length = int(self.headers["Content-Length"])
        body = self.rfile.read(length).decode("utf-8")

        payload = json.loads(body)

        if not self.authenticate_payload(payload):
            print("auth_token does not match.")
            return False
        else:
            self.server.running = True
        self.server.data = Parser.parsePayload(payload)

    def do_GET(self):
        try:
            url = urlparse(self.path)
            if url.path == '/data':
                auth = parse_qs(url.query)['auth'][0]
                if auth == self.server.auth_token:
                    return self.write_response(200, bytes(json.dumps(self.server.data, indent=4), encoding='utf8'))
                else:
                    return self.write_response(400, b"Invalid auth token")
            
            elif url.path == '/shutdown':
                self.write_response(200, b"CSGO-RPC has been closed!")
                os._exit(1)
            else:
                return self.write_response(200, bytes("HTTP GSIServer running at http://{0}:{1}".format(self.server.server_address[0], self.server.server_address[1]), encoding='utf8'))
        except:
            traceback.print_exc()
            return self.write_response(400, b"No auth token provided")

    def write_response(self, code, content):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(content)

    def authenticate_payload(self, payload):
        if "auth" in payload and "token" in payload["auth"]:
            return payload["auth"]["token"] == self.server.auth_token
        else:
            return False

def run(address, auth_token):
    GSIServer(address, auth_token).start_server()

