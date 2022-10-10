#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import time, sys, getopt, logging
from codecs import decode
from urllib.parse import urlparse
from urllib.parse import parse_qs
import requests

from web3 import Web3, HTTPProvider
from ens import ENS

import argparse


# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("-b", "--basedomain",type=str, help = "base domain to remove from inquiry")
parser.add_argument("-u", "--beeurl", type=str, default='', help = "beeurl for checking cids")
parser.add_argument("-p", "--provider", type=str, help = "rpc provider url")

# Read arguments from command line
args = parser.parse_args()

if args.basedomain:
    domLen = len(args.basedomain)
    print ("basedomain: ", args.basedomain)

if args.beeurl:
    print ("beeurl: ", args.beeurl)

if args.provider:
    print ("provider: ", args.provider)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

w3 = Web3(Web3.HTTPProvider(args.provider))
ns = ENS(w3)


hostName = "0.0.0.0"
serverPort = 80

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        domain = parse_qs(urlparse(self.path).query).get('domain', None)
        if domain is not None:
          if domain[0].endswith(args.basedomain):
            short = domain[0].replace(args.basedomain, '')
            addr = w3.ens.address(short + ".eth")
            print ("address ", addr)
          else:
            addr = None
          if (addr == None):
            r = requests.get(args.beeurl + short + "/")
            status = r.status_code == requests.codes.ok
            print ("CID ", status)
          if (addr != None) or (status):
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
 

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
