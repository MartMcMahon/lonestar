from http.server import BaseHTTPRequestHandler, HTTPServer
import time, json

hostName = "localhost"
hostPort = 9000

class Server(BaseHTTPRequestHandler):
  def do_HEAD(s):
    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()

  def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()

    self.wfile.write(bytes(json.dumps({}), "utf-8"))
    #self.wfile.write(bytes("<html><head><title>Title goes here.</title></head>", "utf-8"))
    #self.wfile.write(bytes("<body><p>This is a test.</p>", "utf-8"))
    #self.wfile.write(bytes("<p>You accessed path: %s</p>" % self.path, "utf-8"))
    #self.wfile.write(bytes("</body></html>", "utf-8"))

  def do_POST(self):
    content_len = int(self.headers['content-length'])
    body = json.loads((self.rfile.read(content_len)).decode("utf-8"))
    print(body)

    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()

    #result = dbstuff.getCarsAtDealership(body['index'])
    #result = list(result)
    #list(result)
    #self.wfile.write(bytes(str(result), "utf-8"))
    for car in result:
      self.wfile.write(bytes(json.dumps(car), "utf-8"))

serv = HTTPServer((hostName, hostPort), Server)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
  serv.serve_forever()
except KeyboardInterrupt:
  pass

serv.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))