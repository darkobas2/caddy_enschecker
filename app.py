#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import time, sys, getopt, logging
from codecs import decode
from urllib.parse import urlparse
from urllib.parse import parse_qs
from threading import Timer
import requests,urllib
import os

from web3 import Web3, HTTPProvider
from ens import ENS
import argparse


# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("-b", "--basedomain",type=str, help = "base domain to remove from inquiry")
parser.add_argument("-u", "--beeurl", type=str, default='', help = "beeurl for checking cids")
parser.add_argument("-p", "--provider", type=str, help = "rpc provider url")
parser.add_argument("-a", "--allow", action=argparse.BooleanOptionalAction, help="use allow list", required=False, default=False)

# Read arguments from command line
args = parser.parse_args()

if args.basedomain:
    domLen = len(args.basedomain)
    print ("basedomain: ", args.basedomain)

if args.beeurl:
    args.beeurl = os.path.join(args.beeurl, '')
    print ("beeurl: ", args.beeurl)

if args.provider:
    print ("provider: ", args.provider)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

w3 = Web3(Web3.HTTPProvider(args.provider))
ns = ENS.fromWeb3(w3)



hostName = "0.0.0.0"
serverPort = 80
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        global status
        status = ''
        addr = '0x0000000000000000000000000000000000000000'
        parsed_path = urlparse(self.path)
        domain = parse_qs(urlparse(self.path).query).get('domain', None)
        if domain is not None:
          with open(r"allowlist", 'r') as allowList:
            content = allowList.read()
            short = domain[0].replace(args.basedomain, '')
            if (short in content) or (args.allow is False):
              if domain[0].endswith(args.basedomain):
                try:
                    addr = ns.owner(short + ".eth")
                    print ("addr ", str(addr))
                    if addr != '0x0000000000000000000000000000000000000000':
                        print ("addr ", str(addr))
                except BaseException as e:
                    print('Error, ens domain owner not found', str(e))
              print(type(args.beeurl))
              if ((addr == '0x0000000000000000000000000000000000000000') and (args.beeurl != '')):
                print('we are here ')
                r = requests.get(args.beeurl + short + "/")
                status = r.status_code == requests.codes.ok
                print ("CID ", status)
              if (addr != '0x0000000000000000000000000000000000000000') or (status):
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes("OK", "utf-8"))
              else:
                self.send_response(403)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes("None", "utf-8"))
            else:
              self.send_response(404)
              self.send_header("Content-type", "text/html")
              self.end_headers()
              self.wfile.write(bytes("Err", "utf-8"))

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

def downloader():
    urllib.request.urlretrieve('https://raw.githubusercontent.com/darkobas2/caddy_enschecker/master/allowlist', 'allowlist')

if __name__ == "__main__":
    dl = RepeatedTimer(86400, downloader)
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        dl.stop()

    webServer.server_close()
    print("Server stopped.")
