#!/usr/bin/env python3

license="""
Select Lines from a CSV File According to a Leitner Scheduler
Written in 2012 by 伴上段

To the extent possible under law, the author(s) have dedicated all copyright
and related and neighboring rights to this software to the public domain
worldwide. This software is distributed without any warranty.

You should have received a copy of the CC0 Public Domain Dedication along
with this software. If not, see
<http://creativecommons.org/publicdomain/zero/1.0/>.
"""

import argparse, csv, datetime, heapq, itertools, os.path, random, sys

if __name__ != "__main__":
  sys.stderr.write("This is meant to be run as a script, not imported like a library.\n")
  sys.exit(1)

class TRandomSelector(object):

  def __init__(self, capacity):
    self.capacity = int(capacity)
    self.sample = []
    if not self.capacity:
      self.Add = (lambda me: None)

  def __iter__(self):
    for _, _, selected in self.sample:
      yield selected

  def Add(self, o):
    tag = random.random()
    if len(self.sample) < self.capacity:
      heapq.heappush(self.sample, (tag, id(o), o))
    elif tag >= self.sample[0][0]:
      heapq.heapreplace(self.sample, (tag, id(o), o))

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="""  Select CSV-formatted lines from the specified file (called the "deck")
  according to a basic Leitner scheduler.  Both the deck and the specified log
  file must be CSV files with the same field separator character, which is
  specified via -s.

  This program is useful for scheduling reviews of flashcards stored within
  CSV files.

about Leitner scheduling:

  A Leitner scheduler sorts items into numbered "buckets".  Items in the first
  bucket (the one with the lowest numeric ID) are always due now.  Items in
  other buckets might be due now.  If an item is "successfully reviewed"
  (the meaning of that phrase is domain-specific), then it moves to the next
  bucket and it scheduled for a later date.  If an item is not successfully
  reviewed, then the item moves back to the first bucket.  Items in the
  last bucket (the one with the highest numeric ID) that are successfully
  reviewed stay within the last bucket.

  Each bucket has an associated delay in days.  When an item is moved into a
  bucket, the item is scheduled for the current date plus that bucket's delay.
  (The first bucket is implicitly defined and has no delay.)

formatting:

  This program treats the first field of each nonempty line from the deck as
  that line's unique ID.  (If multiple lines have the same ID, then the last
  line wins.)  It uses the ID to match the line with records scanned from the
  log file.  Each log file line must have the following format:

    <ID> <field-separator> <timestamp> <field-separator> <+>|<->

  where <ID> is the unique ID of the line associated with the record,
  <field-separator> is the CSV field separator, <timestamp> is the record's
  timestamp (you can modify its format via the -f option), and <+> and <-> are
  the '+' and '-' characters.  '+' indicates that the line was successfully
  reviewed at the specified time, whereas '-' indicates that the line wasn't
  successfully reviewed at the specified time.  What "successfully reviewed"
  means is domain-specific.

  bucketdelay is a delay in days.  It must be a positive integer or zero.
  The first bucket is implicitly defined with no delay, so you don't have
  to specify a delay for it.

output:

  This program prints randomly-selected, due lines to stdout.""", epilog="""examples:

  $ oleitner flashcards.txt flashcards.log 1 3 7 14

    Schedule lines from flashcards.txt using flashcards.log as the log file.
    This uses five buckets with delays of zero, one, three, seven, and fourteen
    days, respectively.

  $ oleitner -n 20 -e 10 flashcards.txt flashcards.log 1 3 7 14

    Schedule at most 30 lines (at most 20 lines with entries in flashcards.log
    and at most 10 lines without such entries) from flashcards.txt using
    flashcards.log as the log file.  This uses the same buckets as in the
    previous example.

  $ oleitner -s ',' flashcards.txt flashcards.log 1 3 7 14

    Same as the first example, but use a comma as the CSV field separator
    instead of tab characters.

  $ oleitner -f '%Y/%m/%d' flashcards.txt flashcards.log 1 3 7 14

    Same as the first example, but use the log timestamp format '%Y/%m/%d'
    instead of the default.

  $ oleitner -b flashcards.txt flashcards.log 1 3 7 14

    Same as the first example, but skip line selection and dump all lines from
    flashcards.txt to stdout with their bucket numbers prefixed to them.
    (-1 indicates that the line has no records in the log file.)
""")
parser.add_argument("-n", "--num-lines", type=int, default=10, dest="num", help="the maximum number of lines with log records to select (default: 10)")
parser.add_argument("-e", "--num-new-lines", type=int, default=4, dest="new", help="the maximum number of lines without log records to select (default: 4)")
parser.add_argument("-s", "--field-sep", default="\t", help="the CSV field separator (default: \\t)")
parser.add_argument("-f", "--date-format", default="%Y年%m月%d日%H時%M分%S秒", help="the format of dates/timestamps in the log file (uses date/strftime flags, default: %%Y年%%m月%%d日%%H時%%M分%%S秒)")
parser.add_argument("-b", "--show-buckets", default=False, action="store_true", help="just dump the lines to standard output along with their current bucket numbers (the bucket number is the first field of each line in the output, -1 for lines without log entries)")
parser.add_argument("-l", "--license", default=False, action="store_true", help="print this program's license to stdout and exit")
parser.add_argument("deckfile", help="a CSV-formatted file containing scheduled lines")
parser.add_argument("logfile", help="a CSV-formatted file containing records for the deck's lines")
parser.add_argument("bucketdelay", type=int, nargs="+", help="the number of days to add to a line's due date when it's moved to the corresponding Leitner bucket")

if any(arg == "-l" for arg in sys.argv[1:]):
  print(license)
  sys.exit(0)

args = parser.parse_args()

class TBucket(object):

  __slots__ = ("id", "size", "first", "next", "time_offset")

  def __init__(self, myid, first, next, time_offset):
    self.id = myid
    self.size = 0
    self.first = first
    self.next = next
    self.time_offset = time_offset
    super().__init__()

  def Add(self, line, dateandtime):
    line.date = dateandtime + self.time_offset
    self.size += 1

  def RemoveOne(self):
    self.size -= 1

class TLine(object):

  __slots__ = ("id", "date", "bucket", "fields")

  def __init__(self, myid, dateandtime, bucket, fields=None):
    self.id = myid
    self.date = dateandtime
    self.bucket = bucket
    self.fields = fields
    super().__init__()

  def Demote(self, dateandtime):
    self.bucket.RemoveOne()
    self.bucket = self.bucket.first
    self.bucket.Add(self, dateandtime)

  def Promote(self, dateandtime):
    self.bucket.RemoveOne()
    self.bucket = self.bucket.next
    self.bucket.Add(self, dateandtime)

# Check arguments for illegal values.
ret = 0
if args.num < 0:
  sys.stderr.write("The number of lines cannot be negative.\n")
  ret = 2
if args.new < 0:
  sys.stderr.write("The number of lines cannot be negative.\n")
  ret = 2
if any(bucket <= 0 for bucket in args.bucketdelay):
  sys.stderr.write("Zero and negative bucket delays are not allowed.\n")
  ret = 2
if not os.path.exists(args.deckfile):
  sys.stderr.write("The deck " + args.deckfile + " does not exist.\n")
  ret = 2
if not os.path.exists(args.logfile):
  sys.stderr.write("The log " + args.logfile + " does not exist.\n")
  ret = 2
if ret != 0:
  sys.exit(ret)

# Create the list of buckets from the client-specified delays.
bucket = TBucket(0, None, None, datetime.timedelta(days=0))
first_bucket = bucket
bucket.next = bucket
bucket.first = bucket
for bucket_id, delay in enumerate(args.bucketdelay, start=1):
  bucket.next = TBucket(bucket_id, first_bucket, None, datetime.timedelta(days=delay))
  bucket = bucket.next
  bucket.next = bucket

# Process the log file.  Create a TLine for each new unique ID encountered
# and track its progress as it hops across buckets.
lines = {}
with open(args.logfile, 'r') as logf:
  for lineno, fields in enumerate(csv.reader(logf, delimiter=args.field_sep)):
    if len(fields) != 3:
      sys.stderr.write(args.logfile + ":" + str(lineno) + ": invalid number of fields: " + str(len(fields)) + "\n")
      sys.exit(3)
    try:
      date_time = datetime.datetime.strptime(fields[1], args.date_format)
    except ValueError as e:
      sys.stderr.write(args.logfile + ":" + str(lineno) + ": invalid date format: " + str(e) + "\n")
      sys.exit(3)
    entry = lines.get(fields[0], None)
    if entry is None:
      entry = TLine(fields[0], None, first_bucket)
      lines[fields[0]] = entry 
    if fields[2] == '+':
      entry.Promote(date_time)
    elif fields[2] == '-':
      entry.Demote(date_time)
    else:
      sys.stderr.write(args.logfile + ":" + str(lineno) + ": invalid mutation in third field: must be + or -\n")
      sys.exit(3)

# Process the lines from the deck.  Match each line with its record in the
# lines dictionary (if such a record exists).  Lines lacking log entries are
# marked as "new" by setting their buckets to None.
now = datetime.datetime.now()
with open(args.deckfile, 'r') as df:
  for lineno, fields in enumerate(csv.reader(df, delimiter=args.field_sep)):
    if len(fields) == 0:
      continue
    if fields[0] not in lines:
      lines[fields[0]] = TLine(fields[0], now, None, fields)
    else:
      lines[fields[0]].fields = fields

# Early out: If we only need to show the lines and their bucket numbers, then
# do so now and exit.
if args.show_buckets:
  for line in lines.values():
    print(args.field_sep.join(itertools.chain((str(line.bucket.id if line.bucket is not None else "-1"),), line.fields)))
  sys.exit(0)

# Randomly select due lines that have already been reviewed (i.e., lines with
# records in the log file) and new lines (lines lacking such records).
# Combine the results and print them to standard output.
due_selector, new_selector = TRandomSelector(args.num), TRandomSelector(args.new)
for line in (line for line in lines.values() if line.date <= now and line.fields is not None):
  (due_selector if line.bucket else new_selector).Add(line)
for line in itertools.chain(due_selector, new_selector):
  print(args.field_sep.join(line.fields))

