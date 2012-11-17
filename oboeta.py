#!/usr/bin/env python3

license="""
Review Lines from the Selected Deck in Random Order Until All Pass
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
from os.path import *
from random import *
from sys import *

def Main(deckfile, logfile, commandfile, field_sep, front_field_id, back_field_id, date_format, is_dry_run):
  ret = 0
  if isinstance(deckfile, str) and not exists(deckfile):
    stderr.write("deck file does not exist: " + deckfile + "\n")
    ret = 1
  if not exists(logfile):
    stderr.write("log file does not exist: " + logfile + "\n")
    ret = 1
  if not exists(commandfile):
    stderr.write("command file (pipe?) does not exist: " + commandfile + "\n")
    ret = 1
  if front_field_id < 0:
    stderr.write("front side's field index cannot be negative\n")
    ret = 1
  if back_field_id < 0:
    stderr.write("back side's field index cannot be negative\n")
    ret = 1
  if ret != 0:
    return 1;

  maxfield = max(front_field_id, back_field_id)
  reviewing_cards = []
  failed_cards = []

  deckf = None
  try:
    deckf = (open(deckfile, 'r') if isinstance(deckfile, str) else deckfile)
    for lineno, fields in enumerate(reader(deckf, delimiter=field_sep)):
      if len(fields) <= maxfield:
        stderr.write((deckfile if isinstance(deckfile, str) else "deck") + ":" + str(lineno) + ": number of fields is less than front or back field index\n")
        return 2
      reviewing_cards.append([fields[0], fields[front_field_id], fields[back_field_id], False])
  finally:
    if deckf is not None:
      deckf.close()

  shuffle(reviewing_cards)
  with open(commandfile, 'r') as commandf:
    with open(logfile, 'a') as logf:
      while reviewing_cards or failed_cards:
        if not reviewing_cards:
          reviewing_cards, failed_cards = failed_cards, reviewing_cards
          shuffle(reviewing_cards)
        card = reviewing_cards.pop()
        stdout.write(field_sep.join(card[:-1]) + "\n")
        stdout.flush()
        command = commandf.readline()
        if command == "+\n":
          if not (is_dry_run or card[-1]):
            logf.write(card[0] + field_sep + datetime.now().strftime(date_format) + field_sep + "+\n")
        elif command == "-\n":
          if not is_dry_run:
            logf.write(card[0] + field_sep + datetime.now().strftime(date_format) + field_sep + "-\n")
          card[-1] = True
          failed_cards.append(card)
        elif command.lower() == "q\n":
          return 0
        else:
          stderr.write("unrecognized command: " + command + "\n")
          return 2

  return 0

if __name__ == "__main__":
  parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, description="""  Review lines from standard input as though they were flashcards
  and log the results.  Both standard input and the specified log file must be
  CSV files with the same field separator character, which is specified via -s.

formatting:

  This program treats the first field of each nonempty line from the deck as
  that line's unique ID.  Two fields define a card: a front and a back.  Both
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

  This program shuffles cards and prints them to standard output one at a time
  in the following CSV format:

    <ID> <field-separator> <front> <field-separator> <back>

  <ID> is described above.  <front> and <back> are the front and back sides
  of the card, respectively, as determined by the front and back field indicies
  mentioned above.

  After printing a card, this program will wait for a command from the
  specified command file.  Commands are single-character lines terminated
  by standard newline (\\n) characters.  The commands are:

    +   the user passed the card
    -   the user didn't pass the card
    q   the user is terminating the quiz

  All other values are erroneous.""")
  parser.add_argument("-d", "--dry-run", default=False, action="store_true", help="don't log the results of the review")
  parser.add_argument("-f", "--date-format", default="%Y年%m月%d日%H時%M分%S秒", help="the format of dates/timestamps in the log file (uses date/strftime flags, default: %%Y年%%m月%%d日%%H時%%M分%%S秒)")
  parser.add_argument("-s", "--field-sep", default="\t", help="the CSV field separator (default: \\t)")
  parser.add_argument("-l", "--license", default=False, action="store_true", help="print this program's license to stdout and exit")
  parser.add_argument("commandfile", help="a file (usually a named pipe) providing review commands")
  parser.add_argument("logfile", help="a CSV-formatted file containing records for the deck's lines")
  parser.add_argument("front_field_id", type=int, help="the zero-based field index for the front size of the card")
  parser.add_argument("back_field_id", type=int, help="the zero-based field index for the back side of the card")

  if any(arg == "-l" for arg in argv[1:]):
    print(license)
    exit(0)
  args = parser.parse_args()
  try:
    ret = Main(stdin, args.logfile, args.commandfile, args.field_sep, args.front_field_id, args.back_field_id, args.date_format, args.dry_run)
  except KeyboardInterrupt:
    ret = 0
  exit(ret)

