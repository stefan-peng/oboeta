#!/usr/bin/env python3

# Select Lines from a CSV File According to the SuperMemo 2 (SM-2) Algorithm
# Written in 2012 by 伴上段
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

# The core SM-2 algorithm is in TLine.Respond().

from argparse import *
from csv import *
from datetime import *
from itertools import *
from math import *
from os.path import *
from sys import *

parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, description="""  Select CSV-formatted lines from standard input and the specified log file
  according to the SuperMemo 2 (SM-2) algorithm.

  This program is useful for scheduling reviews of flashcards stored within
  CSV files.

about SM-2:

  SM-2 is the scheduling algorithm used in the flashcard program SuperMemo 2.
  It's a spaced repetition scheduling (SRS) algorithm, which means it tries
  to optimally schedule flashcards over increasing intervals to
  improve retention.

  You can read about SM-2 online; see
  <http://www.supermemo.com/english/ol/sm2.htm> for an overview.

formatting:

  This program treats the first field of each nonempty line from standard input
  as that line's unique ID.  (If multiple lines have the same ID, then the last
  line wins.)  It uses the ID to match the line with records scanned from the
  log file.  Each log file line must have the following format:

    <ID> <field-separator> <timestamp> <field-separator> <quality-response>

  where <ID> is the unique ID of the line associated with the record,
  <field-separator> is the CSV field separator, <timestamp> is the record's
  timestamp (you can modify its format via the -f option), and
  <quality-response> is an integer in the range [0,5] representing the
  "quality of review response" described in SM-2 (see above).

output:

  This program prints due lines in no particular order in CSV format.  The
  program appends four additional fields to each line:

    1. the line's "interval number," which indicates how many times the user
       reviewed the line since it was created or since the last time it had
       a quality of review response less than three;
    2. the line's "interval," which is how many days will be added to the line's
       due date if it receives a quality of review response of three or greater
       the next time it's reviewed;
    3. the line's "easiness factor," which is never less than 1.3; and
    4. the line's due date.

  All but (4) are described in the SM-2 link mentioned above.""")
parser.add_argument("-s", "--field-sep", default="\t", help="the CSV field separator (default: \\t)")
parser.add_argument("-f", "--date-format", default="%Y年%m月%d日", help="the format of dates/timestamps in the log file and output (uses date/strftime flags, default: %%Y年%%m月%%d日)")
parser.add_argument("-a", "--show-all", default=False, action="store_true", help="dump all lines to standard output regardless of whether they're due")
parser.add_argument("logfile", help="a CSV-formatted file containing records for the deck's lines")

args = parser.parse_args()

class TLine(object):

  __slots__ = ("fields", "duedate", "interval", "intervalnum", "ef")

  def __init__(self, fields, dateandtime):
    self.fields = fields
    self.duedate = dateandtime
    self.interval = 1
    self.intervalnum = 1
    self.ef = 2.5
    super().__init__()

  def Respond(self, q, now):
    if q < 3:
      self.intervalnum = 1
      self.interval = 1
      self.duedate = now + timedelta(days=self.interval)
    else:
      self.intervalnum += 1
      self.duedate = now + timedelta(days=self.interval)
      self.interval = (6 if self.intervalnum == 2 else ceil(self.interval + self.ef))
    self.ef = max(self.ef + 0.1 - (5 - q) * (0.08 + 0.02 * (5 - q)), 1.3)

# Check arguments for illegal values.
if not exists(args.logfile):
  stderr.write(args.logfile + " does not exist.\n")
  exit(1)

# Process the lines from stdin.
now = datetime.now()
lines = {}
for lineno, fields in enumerate(reader(stdin, delimiter=args.field_sep)):
  if len(fields) != 0:
    lines[fields[0]] = TLine(fields, now)

# Process the log file.
with open(args.logfile, 'r') as logf:
  for lineno, fields in enumerate(reader(logf, delimiter=args.field_sep)):
    if len(fields) != 3:
      stderr.write(args.logfile + ":" + str(lineno) + ": invalid number of fields: " + str(len(fields)) + "\n")
      exit(3)
    entry = lines.get(fields[0], None)
    if entry is not None:
      try:
        logdate = datetime.strptime(fields[1], args.date_format)
      except ValueError as e:
        stderr.write(args.logfile + ":" + str(lineno) + ": invalid date format: " + str(e) + "\n")
        exit(3)
      try:
        q = int(fields[2])
      except ValueError:
        stderr.write(args.logfile + ":" + str(lineno) + ": invalid quality response: " + fields[2] + "\n")
        exit(3)
      if q < 0 or q > 5:
        stderr.write(args.logfile + ":" + str(lineno) + ": invalid quality response: " + fields[2] + "\n")
        exit(3)
      entry.Respond(q, logdate)

csvout = writer(stdout, delimiter=args.field_sep)
for line in lines.values():
  if line.duedate <= now or args.show_all:
    csvout.writerow(tuple(chain(line.fields, (line.intervalnum, line.interval, line.ef, line.duedate.strftime(args.date_format)))))

