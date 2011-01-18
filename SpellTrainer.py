#!/usr/bin/python
#
# SpellTrainer.py
#
# by Vasily Zakharov (vmzakhar@gmail.com)
# http://code.google.com/p/spelltrainer/
#
# Version 0.5.1
#

# ToDo:
# - Include Hogwarts hooligan spells
# - Allow adjusting colors and fonts
# - Include support for fast series?
# - Make frequency of appearance depend on level
# - Make delay depend on level

from getopt import getopt
from platform import system
from random import choice, seed
from sys import argv, exit # exit redefined # pylint: disable=W0622
from time import sleep

if system() == 'Windows':
    from msvcrt import kbhit				# pylint: disable=F0401
elif system() == 'Linux':
    from fcntl import fcntl, F_SETFL	 		# pylint: disable=F0401
    from os import O_NDELAY, O_NONBLOCK	 		# pylint: disable=F0401
    from sys import stdin
    fcntl(stdin, F_SETFL, O_NDELAY | O_NONBLOCK)
    def kbhit():
        try:
            stdin.read(1)
            return True
        except IOError:
            return False
else:
    raise Exception("Unsupported platform: %s" % system())

TITLE = "\nSpellTrainer v0.1"

SPELLS = ("Impedimenta", "Tarantallegra", "Silencio",			# Protego
          "Rictusempra", "Incarcero", "Mento Menores",			# Defendo
          "Stupefy", "Achelitus", "Maledicero",				# Enervate
          "Incendio", "Deluvium", "Tormencio", "Conjunctivitus")	# VIP

SIMPLA = SPELLS + ("Expelliarmus",)

MAXIMA = tuple(s + " Maxima" for s in SPELLS) + ("Petrificus Totalus",)

ULTIMA = tuple(s + " Ultima" for s in SPELLS)

class SpellTrainer:

    delay = 3

    MODE_ATTACK = 0
    MODE_DEFENCE = 1

    def __init__(self):
        try: # Reading command line options
            (options, args) = getopt(argv[1:], 'd:h', ('delay=', 'help'))
            for (option, value) in options:
                if option in ('-d', '--delay'):
                    try:
                        self.delay = float(value.strip())
                    except ValueError:
                        usage("delay must be numeric (in seconds)")
                else:
                    usage()
        except Exception, e:
            usage("%s" % e)
        if not args:
            usage("At least one of s/m/u and one of a/d commands must be specified")
        if len(args) > 1:
            usage("Too many arguments")
        commands = args[0]
        spells = []
        if 's' in commands:
            spells += SIMPLA
        if 'm' in commands:
            spells += MAXIMA
        if 'u' in commands:
            spells += ULTIMA
        modes = []
        if 'a' in commands:
            modes.append(self.MODE_ATTACK)
        if 'd' in commands:
            modes.append(self.MODE_DEFENCE)
        if not spells or not modes:
            usage("At least one of s/m/u and one of a/d commands must be specified")
        self.spells = tuple(spells)
        self.modes = tuple(modes)

    def run(self):
        print TITLE
        seed()
        while not kbhit():
            spell = choice(self.spells)
            mode = choice(self.modes)
            if mode == self.MODE_ATTACK:
                text = '      DO'
            elif mode == self.MODE_DEFENCE:
                text = 'INCOMING'
            else:
                assert False # this should never happen
            print "\n%s %s" % (text, spell)
            sleep(self.delay)
        print "Done"

def usage(error = None):
    '''Prints usage information (preceded by optional error message) and exits with code 2.'''
    print "%s\n" % TITLE
    if error:
        print "Error: %s\n" % error
    print "Usage: python SpellTrainer.py [-d|--delay <seconds>] [smuad]"
    print "\nCommands:"
    print "\t s  Include Simpla spells"
    print "\t m  Include Maxima spells"
    print "\t u  Include Ultima spells"
    print "\t a  Train attacks (cast spells shown to you in green)"
    print "\t d  Train defence (cast shields against the spells cast at you on red)"
    print "\nOptions:"
    print "\t-d --delay <seconds>   Delay between spells (default is 3 seconds)"
    print "\t-h --help              Show this help message"
    exit(2)

def main():
    SpellTrainer().run()

if __name__ == '__main__':
    main()
