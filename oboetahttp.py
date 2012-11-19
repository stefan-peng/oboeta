#!/usr/bin/env python3

# Present Oboeta Lines from Standard Input as Flashcards (HTML5 over HTTP Version)
# Written in 2012 by 伴上段
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.

# You should have received a copy of the CC0 Public Domain Dedication along
# with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

from argparse import *
from csv import *
from datetime import *
from http.server import *
from os import *
from os.path import *
from random import *
from sys import *
from threading import *

if __name__ != "__main__":
  stderr.write("This is meant to be run as a program, not loaded as a module.\n")
  exit(1)

parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, description="""  Review lines from standard input as though they were flashcards.
  This program serves flashcards on the localhost via HTTP: You should
  review the cards through a web browser (http://localhost:<port>).

formatting:

  This program expects standard input to be a CSV file.  The -s option controls
  the field delimiter.  The first field is the flashcard's unique ID.  The
  second and third fields are the card's front and back sides, respectively.
  All other fields are ignored.

  This program writes single-character lines to standard output representing
  the results of card reviews.  If the line is "+", then the user passed the
  card; if it's "-", then he failed; and if it's "q", then the user terminated
  the quiz.  All such lines end with a single newline (\\n) character.

output:

  This program will serve HTML via the specified port (-p option).  Use your
  web browser to view the cards.""")
parser.add_argument("-i", "--font-size", default=20, type=int, help="the font size, in points (default: 20)")
parser.add_argument("-n", "--font", default="sans-serif", help="the font used in rendered HTML (default: sans-serif)")
parser.add_argument("-p", "--port", default=1337, type=int, help="the HTTP server's port (default: 1337)")
parser.add_argument("-s", "--field-sep", default="\t", help="the CSV field separator (default: \\t)")

args = parser.parse_args()
ret = 0
if args.font_size <= 0:
  stderr.write("font size must be positive\n")
  ret = 1
if args.port <= 0 or args.port > 65535:
  stderr.write("illegal port number\n")
  ret = 1
if ret != 0:
  exit(ret)

front = None
back = None
showing_back = False
stdinreader = reader(stdin, delimiter=args.field_sep)
cond = Condition()
retcode = 0
running = True

class TServer(BaseHTTPRequestHandler):
  def do_GET(self):
    global front
    global back
    global showing_back
    global stdinreader
    global retcode
    global running
    self.error_content_type = "text/plain"
    if running and self.path != "/favicon.ico":
      if self.path == "/quit":
        stdout.write("q\n")
        stdout.flush()
        stderr.write("Finishing early\n")
        self.Send("text/plain", "Done!")
        with cond:
          running = False
          cond.notify()
        return
      if front is not None:
        if showing_back:
          if self.path.lower() == "/pass":
            stdout.write("+\n")
            stdout.flush()
          else:
            stdout.write("-\n")
            stdout.flush()
          front = None
        else:
          showing_back = True
      if front is None:
        front = next(stdinreader, None)
        back = next(stdinreader, None)
        if front is None or back is None:
          with cond:
            running = False
            cond.notify()
          self.Send("text/plain", "Done!")
          return
        showing_back = False
      self.Send("text/html", """<!DOCTYPE html><html><head><meta charset="UTF-8" /><title>Review</title></head><body style="text-align: center; font: """ + str(args.font_size) + """pt """ + args.font + """"><div>""" + "<br />".join(back if showing_back else front) + """</div>""" + ("""<div><a href="/fail">Fail</a> &middot; <a href="/pass">Pass</a> &middot; <a href="/quit">Quit</a></div>""" if showing_back else """<div><a href="/show">Show</a> &middot; <a href="/quit">Quit</a></div>""") + """</body></html>\r\n""")
    else:
      self.send_error(404)
      self.end_headers()

  def Send(self, mime, message):
    message = bytes(message, encoding="UTF-8")
    self.send_response(200)
    self.send_header("Content-Type", mime)
    self.send_header("Content-Length", str(len(message)))
    self.end_headers()
    left = len(message)
    while left:
      written = self.wfile.write(message)
      message = message[written:]
      left -= written

server = HTTPServer(('', args.port), TServer)
def ServeIt():
  server.serve_forever()
serverthread = Thread(target=ServeIt, daemon=True)
serverthread.start()
try:
  with cond:
    while running:
      cond.wait()
except KeyboardInterrupt as e:
  stdout.write("q\n");

exit(retcode)

