
# The Oboeta Hybrid Index Card System

This collection of scripts helps users manage simple, plain-text collections of flashcards.  It focuses on the essence of flashcard systems: scheduling, not generation, display, backups, or synchronization.

"Oboeta" is a Japanese verb in the simple past tense.  It means "remembered" or "memorized".

## Background

### The Problem

I love electronic flashcards.  There are so many things to like about them:

1. They're easy to create, modify, and destroy.
2. It's especially easy to automatically generate hordes of cards from a few sentences if they're formatted properly.
3. It's easy to apply changes across electronic flashcard decks.
4. Computers can schedule reviews and track progress more quickly and accurately than humans.
5. Electronic flashcards are easy to back up and transport.
6. They occupy very little physical space.  (Hence (5).)

But I also hate the most popular flashcard programs, such as [Anki][Anki].  They're complex, buggy, too generic, and tied to GUIs and storage formats that make my skin crawl.  (OK, SQLite isn't too bad, but extracting data from it is still a pain in the ass.)  I tried many programs and was never satisfied.  All I wanted was something that operated on plain text and separated flashcards from their metadata.

Plain text is an awesome way to store flashcards and their metadata because:

1. plain text is universal: it'll be around when your grandchildren's grandchildren become worm food;
2. plain text can be easily edited via any text editor;
3. plain text files aren't tied to a particular program or library; and
4. all standard *NIX tools can manipulate plain text files.

And then there's my love for paper flashcards.  I admit that they're a pain to create and manage, but there are reasons to use them:

1. You can format paper flashcards however you want.  No supporting tools or complicated formatting algorithms are necessary: Just write what you want and be done with it.
2. Sometimes paper flashcards are easier to carry around and faster to use than a smart phone.  I have a little plastic pencil case that I bought for about $5 into which my B7-sized flashcards fit perfectly.  All I have to do to access them is unzip the case and pull them out.
3. For people learning new languages with difficult writing systems (such as East Asian languages), paper flashcards forces them to practice writing.  Typing doesn't help.
4. Some people feel better when they use paper flashcards.  I'm one of them.  I don't understand why, but I get that mysteriously good feeling that a lot of people say they have when they use paper products rather than electronic devices (e.g., for reading).
5. Paper flashcards grab attention.  Smart phones and laptops don't do that because they're common and everyone around the user assumes she's playing games, sending messages, or surfing the web.  For language learners, the best thing about grabbing people's attention with flashcards is that it creates opportunities to practice.  Curious people start conversations, which lead to new sentences, which lead to new flashcards.  It's a beautiful circle.

### The Solution

I wrote Oboeta to combine electronic and paper flashcards into a hybrid system.  The scripts are deliberately minimalistic so that you can format the flashcard data however you want.  Although I wrote Oboeta to help me maintain a hybrid flashcard system, I could build a full-featured flashcard program on top of it.  But I don't plan to.  (^_^)

Here's how the system works: You have maintain a collection of paper flashcards.  You can organize them any way you like provided that each one has a unique identifier.  (I use monotonically-increasing positive integers for mine.)  On the electronic side, you maintain two plain UTF-8-encoded text files:

1. a [CSV][CSV] file (the "deck") containing one flashcard per line, each beginning with the flashcard's unique identifier; and
2. a CSV file (the "log") containing records of flashcard reviews.

Oboeta is agnostic about the deck's data: It only expects that the file is a CSV file and that the first field of each line is a unique identifier.  You can format everything else however you want.  This makes adding, editing, and reformatting flashcards a cinch: Just edit the deck file.  You can use any text-manipulating program to do this.

On the other hand, the requirements for the log are more stringent:

1. Each nonempty line must have exactly three fields: a flashcard's identifier, a timestamp, and either of the '+' or '-' characters.
2. The flashcard's identifier need not actually name a flashcard.  (This makes deleting flashcards easy: Just remove them from the deck.  You can remove their entries in the log, too, but you don't have to.)
3. The timestamp can be formatted however you wish, but you must be consistent.
4. The third field must be either a single '+' character or a single '-' character.  '+' indicates that you successfully reviewed the associated flashcard on the date represented by the timestamp, whereas '-' indicates that you failed.

Oboeta uses the log to schedule flashcards for review.  You ask Oboeta to dump a bunch of new or due cards to the screen, select the corresponding paper flashcards, and review them.  When you're finished reviewing your cards, update the log accordingly.

## Requirements

I wrote most of the code in [Python 3][Python].  (Die-hard Python 2 fans can cry me a river: Python 3 is the new standard.  Welcome to the future.)  It runs fine with CPython, the standard implementation.

## The Scripts

* `oleitner` -- process the deck and log files and display flashcards for review on standard output

## Installing

Open a terminal, navigate to the directory containing this collection's source code, and execute the `install.sh` script, passing the directory where you want to install executables as the first parameter.  For example:

    $ ./install.sh /usr/bin

This will copy the scripts to the specified directory.  You might have to change users (e.g., run `sudo`) depending on which installation directory you select.

## Sample Framework Built on Oboeta

If you want an example of a framework built on top of Oboeta, see the "example" subdirectory.  It contains my Japanese flashcard system along with an early snapshot of my sentence deck and log.  I use all of the scripts in the directory; you're free to use them, too.  NOTE: Some of the Japanese-specific scripts depend on [Hinomoto][Hinomoto], a small collection of programs for parsing and tagging Unicode text.  Of course, you can remove these dependencies.

My system works like this: I place the scripts into a directory and create four subdirectories: decks, media, backups, and other.  "decks" contains my deck and log files.  "media" contains two subdirectories: "sds" for downloaded kanji stroke order diagrams and "recordings" for audio recordings of my flashcards.  "backups" is where I store bzipped TAR archives of flashcards and media.  "other" contains miscellaneous stuff.

The most essential scripts are `edeck`, `genline`, `pass`, `fail`, and `grabsome`.  They should be easy to understand: Open them with your favorite text editor and check them out.

## License

All of the files in this collection have been dedicated to the public domain via the Creative Commons CC0 Public Domain Dedication in the hope that they would be circulated widely and without restriction.  I won't make any money from this code and I feel that it's more important that other people are free to use, modify, and distribute it as they please, with or without charge, even if I could make money from this.  Simply put, I like contributing to a healthy public domain.  See the file `COPYING` for a complete copy of the public domain dedication.

## Authors

I wrote these scripts by myself primarily for myself, but I hope that others will find it useful.

-- Joodan Van (伴上段), 2012年11月04日

[Flashcards]: http://en.wikipedia.org/wiki/Flashcards#Systems "Flashcards on Wikipedia"
[Anki]: http://ankisrs.net/ "The Anki SRS Program"
[CSV]: http://en.wikipedia.org/wiki/Comma-separated_values "Comma-Separated Values on Wikipedia"
[Python]: http://www.python.org/download/releases/ "Python Releases"

