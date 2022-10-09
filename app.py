#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import time, sys, getopt, logging
from urllib.parse import urlparse
from urllib.parse import parse_qs

from web3 import Web3, HTTPProvider
from ens import ENS

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]

# Options
options = "hpb:"
# Long options
long_options = ["help", "provider", "basedomain"]

try:
    # Parsing argument
    arguments, values = getopt.getopt(argumentList, options, long_options)
    # checking each argument
    for currentArgument, currentValue in arguments:
 
        if currentArgument in ("-h", "--help"):
            print ("OPTIONS: -b .example.com -p http://rpc.com")

        elif currentArgument in ("-p", "--provider"):
            userProvider = sys.argv[4]
            print ("provider: ", userProvider)

        elif currentArgument in ("-b", "--basedomain"):
            domLen = len(currentValue)
            baseDom = currentValue
            print ("basedomain: ", baseDom)

except getopt.error as err:
    # output error, and return with an error code
    print (str(err))

w3 = Web3(Web3.HTTPProvider(userProvider))
ns = ENS(w3)


hostName = "0.0.0.0"
serverPort = 80

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        domain = parse_qs(urlparse(self.path).query).get('domain', None)
        if domain is not None:
          if domain[0].endswith(baseDom):
            addr = w3.ens.address(domain[0].replace(baseDom, '') + ".eth")
            print (addr)
          else:
            addr = None

          if (addr != None):
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
