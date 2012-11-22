#!/usr/bin/env python3

# Generate Cloze Deletions from Standard Input
# Written in 2012 by 伴上段
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

from argparse import *
import hashlib
from io import *
from sys import *

parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, description="""  Generate cloze deletions from standard input's lines.

about cloze deletions:

  Cloze deletions are flashcards that omit pieces of information.  The user has
  to guess the contents of the omitted section.  For example, you could
  reformulate this traditional flashcard:

    Q: What is Japan's capital?
    A: Tokyo

  as a cloze deletion:

    Q: (...) is Japan's capital.
    A: Tokyo

  This is very useful in some domains, such as language learning.  For example,
  you could omit certain words from flashcards representing sentences or
  passages and derive the hidden text from the context.

formatting:

  This program is line-oriented: Each line from standard input is treated as
  a single flashcard.  Flashcards cannot be split across multiple lines.  Cloze
  deletions are delimited by matching pairs of curly braces ('{' and '}').
  Cloze deletions may nest.  Curly braces can be escaped with
  single backslashes (\\).  Lines lacking curly braces are ignored.

  NOTE: This program treats lines from standard input as lines: It doesn't
  interpret them in any special way.  Thus it's possible to make cloze deletions
  span multiple CSV fields if standard input provides CSV.  This generally isn't
  a good idea.  If standard input is CSV, then make sure cloze deletions don't
  span multiple fields.

output:

  This program writes generated cloze deletion lines on standard output.
  Each generated line contains at least three CSV fields:

    1. the cloze deletion card's generated ID (a hash digest);
    2. the contents of the line from which the card was generated with a clozed
       section replaced with "(...)"; and
    3. the replaced part of the line.

  The hash function cannot guarantee that a card's ID will be unique across all
  generated cards, but choosing a hash function with a large digest (e.g.,
  SHA-256) will make such collisions extremely improbable.  Paranoid users
  can use other programs (such as a combination of sort(1), cut(1), and uniq(1))
  to detect duplicates.""")
parser.add_argument("-e", "--elision-text", default="(...)", help="the text that replaces clozed sections (default: (...))")
parser.add_argument("-f", "--hash-func", default="sha256", help="the Python hashlib hash function to use to generate cloze card IDs (default: sha256)")
parser.add_argument("-s", "--field-sep", default="\t", help="the output CSV field separator (default: \\t)")

args = parser.parse_args()

if args.hash_func not in hashlib.__dict__:
  stderr.write("unrecognized hash function: " + args.hash_func + "\n")
  exit(1)
hash_class = hashlib.__dict__[args.hash_func]

for lineno, line in enumerate(stdin, start=1):
  cloze_num = 0
  components = []   # list of strings, integers (cloze opening markers), and None values (cloze ending markers)
  clozes = []       # list of clozes in any order
  textbuf = StringIO()
  for col, c in enumerate(line, start=1):
    if c == '{':
      val = textbuf.getvalue()
      if val:
        textbuf = StringIO()
        components.append(val)
      cloze = len(clozes) + 1
      cloze_num += 1
      components.append(cloze)
      clozes.append(cloze)
    elif c == '}':
      if cloze_num == 0:
        stderr.write(str(lineno) + ":" + str(col) + ": cloze termination symbol found outside cloze\n")
        exit(2)
      val = textbuf.getvalue()
      if val:
        textbuf = StringIO()
        components.append(val)
      components.append(None)
      cloze_num -= 1
    elif c != '\n':
      textbuf.write(c)
  if cloze_num != 0:
    stderr.write(str(lineno) + ":" + str(col) + ": " + str(cloze_num) + " clozes not closed\n")
    exit(2)
  if clozes:
    textbuf = textbuf.getvalue()
    if textbuf:
      components.append(textbuf)
    for masked_cloze in clozes:
      textbuf = StringIO()
      clozebuf = StringIO()
      for component in components:
        if cloze_num:
          if isinstance(component, int):
            cloze_num += 1
          elif component is None:
            cloze_num -= 1
          else:
            clozebuf.write(component)
        elif component is masked_cloze:
          cloze_num = 1
          textbuf.write(args.elision_text)
        elif isinstance(component, str):
          textbuf.write(component)
      textbuf = textbuf.getvalue()
      hasher = hash_class()
      hasher.update(bytes(textbuf, encoding="UTF-8"))
      stdout.write(hasher.hexdigest() + args.field_sep + textbuf + args.field_sep + clozebuf.getvalue() + "\n")
      stdout.flush()

