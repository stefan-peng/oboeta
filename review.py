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

import argparse, oboeta, oleitner, os, os.path, sys, tempfile

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="""  Review lines from the specified file as though they were flashcards
  and log the results.  Both the deck and the specified log file must be CSV
  files with the same field separator character, which is specified via -s.

formatting:

  See oboeta and oleitner for formatting requirements.

output:

  See oboeta for the output format.""")
parser.add_argument("-n", "--num-lines", type=int, default=10, dest="num", help="the maximum number of lines with log records to select (default: 10)")
parser.add_argument("-e", "--num-new-lines", type=int, default=4, dest="new", help="the maximum number of lines without log records to select (default: 4)")
parser.add_argument("-d", "--dry-run", default=False, action="store_true", help="don't log the results of the review")
parser.add_argument("-f", "--date-format", default="%Y年%m月%d日%H時%M分%S秒", help="the format of dates/timestamps in the log file (uses date/strftime flags, default: %%Y年%%m月%%d日%%H時%%M分%%S秒)")
parser.add_argument("-s", "--field-sep", default="\t", help="the CSV field separator (default: \\t)")
parser.add_argument("-l", "--license", default=False, action="store_true", help="print this program's license to stdout and exit")
parser.add_argument("deckfile", help="a CSV-formatted file containing scheduled lines")
parser.add_argument("logfile", help="a CSV-formatted file containing records for the deck's lines")
parser.add_argument("bucketdelay", type=int, nargs="+", help="the number of days to add to a line's due date when it's moved to the corresponding Leitner bucket")
parser.add_argument("front_field_id", type=int, help="the zero-based field index for the front size of the card")
parser.add_argument("back_field_id", type=int, help="the zero-based field index for the back side of the card")

def Main(args):
  if any(arg == "-l" for arg in args):
    print(license)
    return 0;
  args = parser.parse_args(args)

  tfile = tempfile.TemporaryFile(mode='w+')
  ret = oleitner.Main(tfile, args.num, args.new, args.bucketdelay, args.logfile, args.deckfile, args.field_sep, args.date_format, False)
  if ret == 0:
    tfile.seek(0)
    ret = oboeta.Main(tfile, args.logfile, args.field_sep, args.front_field_id, args.back_field_id, args.date_format, args.dry_run)
  return ret

if __name__ == "__main__":
  exit(Main(sys.argv[1:]))

