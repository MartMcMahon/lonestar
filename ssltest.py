from http.server import BaseHTTPRequestHandler, HTTPServer
import time, json, ssl
import subprocess
from subprocess import PIPE, STDOUT
import busstuff

hostName = ""
hostPort = 80

class Server(BaseHTTPRequestHandler):
  def do_HEAD(s):
    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()

  def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()

    self.wfile.write(bytes("<html><body>hello!</body></html>"), "utf-8"))
    

serv = HTTPServer((hostName, hostPort), Server)
serv.socket = ssl.wrap_socket(serv.socket, certfile='./fullchain.pem', server_side=True)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

dh = DataHandler()

try:
  serv.serve_forever()
except KeyboardInterrupt:
  pass

serv.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))



