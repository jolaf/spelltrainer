#!/usr/bin/python
#
# SpellTrainer.py
#
# by Vasily Zakharov (vmzakhar@gmail.com)
# http://code.google.com/p/spelltrainer/
#
# Uses TkInter for GUI: http://wiki.python.org/moin/TkInter
#
# Version 0.21
#

# ToDo:
# - Allow adjusting colors and fonts
# - Make frequency of appearance depend on level
# - Make delay depend on level
# - Include Hogwarts hooligan spells
# - Include support for fast series?

from base64 import b64decode
from getopt import getopt
from os import remove
from random import choice, seed
from sys import argv, exit # exit redefined # pylint: disable=W0622
from tempfile import NamedTemporaryFile
from thread import start_new_thread
from time import sleep
from traceback import format_exc

from Tkinter import Button, Frame, Label, StringVar, CENTER, FLAT, N, S, E, W
from tkFont import Font

TITLE = 'SpellTrainer v0.22'

SPELLS = ('Impedimenta', 'Tarantallegra', 'Silencio',			# Protego
          'Rictusempra', 'Incarcero', 'Mento Menores',			# Defendo
          'Stupefy', 'Achelitus', 'Maledicero',				# Enervate
          'Incendio', 'Deluvium', 'Tormencio', 'Conjunctivitus')	# VIP

SIMPLA = SPELLS + ('Expelliarmus',)

MAXIMA = tuple(s + ' Maxima' for s in SPELLS) + ('Petrificus Totalus',)

ULTIMA = tuple(s + ' Ultima' for s in SPELLS)

class SpellTrainer(Frame): # pylint: disable=R0904

    delay = 1

    MODE_ATTACK = 0
    MODE_DEFENCE = 1

    FONT_NAME = 'Verdana'
    FONT_SIZE = 10
    FONT_STYLE = 'bold'

    ATTACK_BACKGROUND  = 'black'
    ATTACK_FOREGROUND  = 'green'
    DEFENCE_BACKGROUND = 'red'
    DEFENCE_FOREGROUND = 'white'

    def __init__(self, master = None):
        # Reading command line options
        try:
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

        # Processing command line commands
        commands = ''.join(args)
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

        # Initializing GUI
        Frame.__init__(self, master)
        self.master.title(TITLE)
        try:
            icoFile = NamedTemporaryFile(delete = False)
            icoFile.write(b64decode('AAABAAEAEBAQAAEABAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAAAAAABMLAAATCwAAEAAAAAAAAAA3RkwA6OblAACw9wCLjY0AxszMAK+urQAAAAAA////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAZmZmZmZmZmZnd3d3d3d3dmd3d3d3d3d2Z3d3d3d3dQZnd0EDF3d2dmdAQCB3dwN2ZwdxAFd0Z3ZlF3dXd3Z3dmV3d3d3A3d2Yxd3d3Rnd3ZkB3d3dnd3dmdjd3cFd3d2Z3YAAEd3d3Znd3EXd3d3dmd3d3d3d3d2ZmZmZmZmZmYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'))
            icoFile.close()
            self.master.wm_iconbitmap(default = icoFile.name)
            remove(icoFile.name)
        except Exception:
            pass
        self.grid(sticky = N+S+E+W)
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight = 1)
        top.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)
        self.text = StringVar()
        self.text.set(TITLE)
        self.button = Button(self, textvariable = self.text, command = self.quit,
                             anchor = CENTER, justify = CENTER, relief = FLAT, borderwidth = 0,
                             font = (self.FONT_NAME, self.FONT_SIZE, self.FONT_STYLE))
        self.button.grid(row = 0, column = 0, sticky = N+S+E+W)
        self.master.wm_geometry('235x100')
        self.master.bind('<Configure>', self.resize)
        start_new_thread(self.run, ()) # Start activity thread
        self.mainloop()

    def resize(self, event = None):
        if event and (event.width < 10 or event.height < 10):
            return # Skip initial resize event to avoid dead loop
        # ToDo: find the longest spell name and adjust the font size for it instead of current spell
        # ToDo: create Label statically
        # ToDo: maybe calculate font proportion once and store THAT statically
        t = Label(self, font = (self.FONT_NAME, -1000, self.FONT_STYLE), height = 1, text = self.text.get())
        height = int(float(self.winfo_width()) / t.winfo_reqwidth() * t.winfo_reqheight())
        self.button.configure(font = Font(family = self.FONT_NAME, size = -int(0.7 * min(self.winfo_height(), height)), weight = self.FONT_STYLE))

    def run(self):
        '''Activity method that performs the actual action.
           Must be run in a separate thread.'''
        seed()
        while True:
            try:
                sleep(self.delay)
                spell = choice(self.spells)
                mode = choice(self.modes)
                if mode == self.MODE_ATTACK:
                    # ToDo: set click background color also, create special method for that
                    self.button.configure(background = self.ATTACK_BACKGROUND, foreground = self.ATTACK_FOREGROUND)
                elif mode == self.MODE_DEFENCE:
                    self.button.configure(background = self.DEFENCE_BACKGROUND, foreground = self.DEFENCE_FOREGROUND)
                else:
                    assert False # this should never happen
                self.text.set(spell)
                self.resize()
            except Exception:
                print format_exc()

def usage(error = None):
    '''Prints usage information (preceded by optional error message) and exits with code 2.'''
    print "\n%s\n" % TITLE
    if error:
        print "Error: %s\n" % error
    print "Usage: python SpellTrainer.py [options] <commands>"
    print "\nCommands:"
    print "\t s  Include Simpla spells"
    print "\t m  Include Maxima spells"
    print "\t u  Include Ultima spells"
    print "\t a  Train attacks (cast spells shown to you in green)"
    print "\t d  Train defence (cast shields against the spells cast at you on red)"
    print "\nOptions:"
    print "\t-d --delay <seconds>   Delay between spells (default is 1 second)"
    print "\t-h --help              Show this help message"
    exit(2)

def main():
    '''Starts the SpellTrainer GUI.'''
    SpellTrainer()

if __name__ == '__main__':
    main()
