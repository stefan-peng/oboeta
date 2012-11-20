#!/usr/bin/env python3

# Present Oboeta Lines from Standard Input as Flashcards (Terminal Version)
# Written in 2012 by 伴上段
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

sm2_num_responses = 6

from argparse import *
from csv import *
from os.path import *
from sys import *

parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, description="""  Review lines from the specified source file as though they were flashcards.
  This program serves flashcards on the localhost via HTTP: You should
  review the cards through a web browser (http://localhost:<port>).

formatting:

  This program expects the source file to be a CSV file.  The -s option controls
  the field delimiter.  The program reads two lines per flashcard: the front
  and the back sides of the card, respectively.  Both are expected to be CSV-
  formatted lines.  Each field in a line will be displayed on its own line
  in the card's display.

  This program writes single-character lines to standard output representing
  the results of card reviews.  For Leitner-system-based reviews, if the line
  is "+", then the user passed the card; if it's "-", then he failed.  If the
  review uses SM-2, then the results will be integers in the range [0,5].
  In either case, if the output is a line containing just "q", then the user
  terminated the quiz.  All such lines end with a single newline
  (\\n) character.

output:

  This program displays cards one at a time to standard output and waits for
  user input via standard input.  The first input merely shows the back side of
  the card.  The second one depends on whether the review is based on the
  Leitner system or SM-2.  If it uses the Leitner system, then the user must
  enter either Y or N to indicate that he passed or failed the card,
  respectively.  On the other hand, if the review uses the SM-2 system, then
  the user must enter an integer in the range [0,5], where 0 means total memory
  blackout and 5 means "Piece of cake!"  In any case, entering Q terminates the
  quiz.  Responses are case-insensitive.""")
parser.add_argument("-s", "--field-sep", default="\t", help="the CSV field separator (default: \\t)")
parser.add_argument("cardsource", help="a file (usually a named pipe) from which cards are read")
parser.add_argument("commandfile", help="a file (usually a named pipe) to which user results will be written")
parser.add_argument("-2", "--use-sm2", default=False, action="store_true", help="use the SM-2 algorithm instead of the Leitner system")

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

front = None
input_prompt = "Correct [" + "/".join(str(v) for v in (range(sm2_num_responses) if args.use_sm2 else "Yn")) + "]? "
sm2_values = "".join(str(v) for v in range(sm2_num_responses))
with open(args.cardsource, 'r') as cardsource:
  with open(args.commandfile, 'w') as commandf:
    try:
      for card in reader(cardsource, delimiter=args.field_sep):
        if front is None:
          front = card
          continue
        stdout.write("\n" + "\n".join(front))
        front = None
        input("\nPress \"Enter\" to see the answer.")
        stdout.write("\n" + "\n".join(card))
        while True:
          answer = input(input_prompt).lower().strip()
          if answer == "q" or answer == "quit":
            commandf.write("q\n")
            commandf.flush()
            exit(0)
          elif args.use_sm2:
            if answer in sm2_values:
              commandf.write(answer + "\n")
              commandf.flush()
              break
          else:
            if answer == "y" or answer == "yes" or answer == "":
              commandf.write("+\n")
              commandf.flush()
              break
            elif answer == "n" or answer == "no":
              commandf.write("-\n")
              commandf.flush()
              break
          stdout.write("Please enter one of the choices (or 'q' to quit).")
    except EOFError:
      stdout.write("\nFinishing early")
      commandf.write("q\n")
    except KeyboardInterrupt:
      stdout.write("\nFinishing early")
      commandf.write("q\n")

