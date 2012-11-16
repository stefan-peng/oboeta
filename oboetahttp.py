#!/usr/bin/env python3

license="""
Review Lines from the Selected Deck in Random Order Until All Pass (Web Version)
Written in 2012 by 伴上段

To the extent possible under law, the author(s) have dedicated all copyright
and related and neighboring rights to this software to the public domain
worldwide. This software is distributed without any warranty.

You should have received a copy of the CC0 Public Domain Dedication along
with this software. If not, see
<http://creativecommons.org/publicdomain/zero/1.0/>.
"""

from argparse import *
from csv import *
from datetime import *
from http.server import *
from os import *
from os.path import *
from random import *
from sys import *

if __name__ != "__main__":
  stderr.write("This is meant to be run as a program, not loaded as a module.\n")
  exit(1)

parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, description="""  Review lines from standard input as though they were flashcards
  and log the results.  Both standard input and the specified log file must be
  formatted as CSV with the same field separator character, which is specified
  via -s.  This program serves flashcards on the localhost via HTTP: You should
  review the cards through a web browser (http://localhost:<port>).

formatting:

  This program treats the first field of each nonempty line from standard input
  as that line's unique ID.  Two fields define a card: a front and a back.  Both
  must be specified as zero-based indicies as part of this program's parameters.

  New log file entries will have this format:

    <ID> <field-separator> <timestamp> <field-separator> <+>|<->

  where <ID> is the unique ID of the line (card) associated with the record,
  <field-separator> is the CSV field separator, <timestamp> is the record's
  timestamp (you can modify its format via the -f option), and <+> and <-> are
  the '+' and '-' characters.  '+' indicates that the card was successfully
  reviewed at the specified time, whereas '-' indicates that the card wasn't
  successfully reviewed at the specified time.

output:

  This program will serve HTML via the specified port (-p option).  Use your
  web browser to view the cards.  This program will repeatedly serve failed
  cards until you pass all of them or terminate the program.""")
parser.add_argument("-d", "--dry-run", default=False, action="store_true", help="don't log the results of the review")
parser.add_argument("-f", "--date-format", default="%Y年%m月%d日%H時%M分%S秒", help="the format of dates/timestamps in the log file (uses date/strftime flags, default: %%Y年%%m月%%d日%%H時%%M分%%S秒)")
parser.add_argument("-i", "--font-size", default=20, type=int, help="the font size, in points (default: 20)")
parser.add_argument("-n", "--font", default="sans-serif", help="the font used in rendered HTML (default: sans-serif)")
parser.add_argument("-p", "--port", default=1337, type=int, help="the HTTP server's port (default: 1337)")
parser.add_argument("-s", "--field-sep", default="\t", help="the CSV field separator (default: \\t)")
parser.add_argument("-l", "--license", default=False, action="store_true", help="print this program's license to stdout and exit")
parser.add_argument("logfile", help="a CSV-formatted file containing records for the deck's lines")
parser.add_argument("front_field_id", type=int, help="the zero-based field index for the front size of the card")
parser.add_argument("back_field_id", type=int, help="the zero-based field index for the back side of the card")

if any(arg == "-l" for arg in argv[1:]):
  print(license)
  exit(0)
args = parser.parse_args()

ret = 0
if not exists(args.logfile):
  stderr.write("log file does not exist: " + args.logfile + "\n")
  ret = 1
if args.front_field_id < 0:
  stderr.write("front side's field index cannot be negative\n")
  ret = 1
if args.back_field_id < 0:
  stderr.write("back side's field index cannot be negative\n")
  ret = 1
if args.font_size <= 0:
  stderr.write("font size must be positive\n")
  ret = 1
if args.port <= 0 or args.port > 65535:
  stderr.write("illegal port number\n")
  ret = 1
if ret != 0:
  exit(ret)

reviewing_cards = []
failed_cards = []
card = None
showing_back = False
logf = None

class TServer(BaseHTTPRequestHandler):
  def do_GET(self):
    global reviewing_cards
    global failed_cards
    global card
    global showing_back
    global logf
    self.error_content_type = "text/plain"
    if self.path != "/favicon.ico":
      if card is not None:
        if showing_back:
          if self.path.lower() == "/pass":
            if not args.dry_run:
              logf.write(card[0] + "\t" + datetime.now().strftime(args.date_format) + "\t+\n")
              logf.flush()
          else:
            failed_cards.append(card)
            if not args.dry_run:
              logf.write(card[0] + "\t" + datetime.now().strftime(args.date_format) + "\t-\n")
              logf.flush()
          card = None
        else:
          showing_back = True
      if card is None:
        if not reviewing_cards:
          reviewing_cards, failed_cards = failed_cards, reviewing_cards
          if not reviewing_cards:
            self.Send("text/plain", bytes("Done!\r\n", encoding="UTF-8"))
            return
          shuffle(reviewing_cards)
        card = reviewing_cards.pop()
        showing_back = False
      self.Send("text/html", bytes("""<!DOCTYPE html><html><head><meta charset="UTF-8" /><title>Review</title></head><body style="text-align: center; font: """ + str(args.font_size) + """pt """ + args.font + """"><div>""" + card[2 if showing_back else 1] + """</div>""" + ("""<div><a href="/fail">Fail</a> &middot; <a href="/pass">Pass</a></div>""" if showing_back else """<div><a href="/show">Show</a></div>""") + """</body></html>\r\n""", encoding="UTF-8"))
    else:
      self.send_error(404)
      self.end_headers()

  def Send(self, mime, message):
    self.send_response(200)
    self.send_header("Content-Type", mime)
    self.send_header("Content-Length", str(len(message)))
    self.end_headers()
    left = len(message)
    while left:
      written = self.wfile.write(message)
      message = message[written:]
      left -= written

maxfield = max(args.front_field_id, args.back_field_id)
for lineno, fields in enumerate(reader(stdin, delimiter=args.field_sep)):
  if len(fields) <= maxfield:
    stderr.write("stdin:" + str(lineno) + ": number of fields is less than front or back field index\n")
    exit(2)
  reviewing_cards.append((fields[0], fields[args.front_field_id], fields[args.back_field_id]))

shuffle(reviewing_cards)
try:
  logf = open(args.logfile, 'a')
  HTTPServer(('', args.port), TServer).serve_forever()
except KeyboardInterrupt:
  pass
finally:
  if logf is not None:
    logf.flush()
    logf.close()

