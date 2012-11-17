#!/usr/bin/env python3

license="""
Present Oboeta Lines from Standard Input as Flashcards (Terminal Version)
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
from os.path import *
from sys import *

parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, description="""  Review lines from the specified source file as though they were flashcards.
  This program serves flashcards on the localhost via HTTP: You should
  review the cards through a web browser (http://localhost:<port>).

formatting:

  This program expects the source file to be a CSV file.  The -s option controls
  the field delimiter.  The first field is the flashcard's unique ID.  The
  second and third fields are the card's front and back sides, respectively.
  All other fields are ignored.

  This program writes single-character lines to the specified command file
  representing the results of card reviews.  If the line is "+", then the user
  passed the card; if it's "-", then he failed; and if it's "q", then the user
  terminated the quiz.  All such lines end with a single newline
  (\\n) character.

output:

  This program displays cards one at a time to standard output and waits for
  user input via standard input.  The first input merely shows the back side of
  the card.  The second one must be either Y or N to indicate that the user
  passed or failed the card, respectively, or Q to terminate the quiz.  The
  response is case-insensitive.""")
parser.add_argument("-s", "--field-sep", default="\t", help="the CSV field separator (default: \\t)")
parser.add_argument("-l", "--license", default=False, action="store_true", help="print this program's license to stdout and exit")
parser.add_argument("cardsource", help="a file (usually a named pipe) from which cards are read")
parser.add_argument("commandfile", help="a file (usually a named pipe) to which user results will be written")

if any(arg == "-l" for arg in argv[1:]):
  print(license)
  exit(0)
args = parser.parse_args()

ret = 0
if not exists(args.cardsource):
  stderr.write("command file (pipe?) does not exist: " + args.commandfile + "\n")
  ret = 1
if not exists(args.commandfile):
  stderr.write("command file (pipe?) does not exist: " + args.commandfile + "\n")
  ret = 1
if ret:
  exit(ret)

with open(args.cardsource, 'r') as cardsource:
  with open(args.commandfile, 'w') as commandf:
    try:
      for card in reader(cardsource, delimiter=args.field_sep):
        if len(card) < 3:
          stderr.write("stdin:expected at least 3 fields but got " + str(len(card)) + "\n")
          exit(2)
        print("\n" + card[0] + ": " + card[1] + "\n")
        input("Press \"Enter\" to see the answer.")
        print("\n" + card[2])
        while True:
          answer = input("Correct [Y/n]? ").lower().strip()
          if answer == "y" or answer == "yes" or answer == "":
            commandf.write("+\n")
            commandf.flush()
            break
          elif answer == "n" or answer == "no":
            commandf.write("-\n")
            commandf.flush()
            break
          elif answer == "q" or answer == "quit":
            commandf.write("q\n")
            commandf.flush()
            exit(0)
          else:
            print("Please enter 'y' or 'n' (or 'q' to quit).")
    except EOFError:
      print("\nFinishing early")
      commandf.write("q\n")
    except KeyboardInterrupt:
      print("\nFinishing early")
      commandf.write("q\n")

