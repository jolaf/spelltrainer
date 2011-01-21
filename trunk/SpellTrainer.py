#!/usr/bin/python
#
# SpellTrainer.py
#
# by Vasily Zakharov (vmzakhar@gmail.com)
# http://code.google.com/p/spelltrainer/
#
# Uses TkInter for GUI: http://wiki.python.org/moin/TkInter
#
# Version 1.0
#

# ToDo:
# - Allow specifying colors and fonts from command line options
# - Make frequency of appearance depend on level
# - Make delay depend on level
# - Include Hogwarts hooligan spells (to train fast going in close quarters)
# - Include some specialized spells
# - Include support for fast series

from base64 import b64decode
from getopt import getopt
from os import remove
from random import choice, seed
from sys import argv, exit # exit redefined # pylint: disable=W0622
from tempfile import NamedTemporaryFile
from thread import start_new_thread
from time import sleep

from Tkinter import Frame, Label, StringVar, N, S, E, W

TITLE = 'SpellTrainer v1.0'

SPELLS = ('Impedimenta', 'Tarantallegra', 'Silencio',		# Protego
          'Rictusempra', 'Incarcero', 'Mento Menores',		# Defendo
          'Stupefy', 'Achelitus', 'Maledicero',			# Enervate
          'Incendio', 'Deluvium', 'Tormencio', 'Conjunctivitus')# VIP

SIMPLA = SPELLS + ('Expelliarmus',)

MAXIMA = tuple(s + ' Maxima' for s in SPELLS) + ('Petrificus Totalus',)

ULTIMA = tuple(s + ' Ultima' for s in SPELLS)

RULE_OF_N_SPELLS = 3

MODE_ATTACK = 0
MODE_DEFENCE = 1

FONT_NAME = 'Verdana'
FONT_SIZE = 10
FONT_STYLE = 'bold'

ATTACK_BACKGROUND  = 'black'
ATTACK_FOREGROUND  = 'green'
DEFENCE_BACKGROUND = 'red'
DEFENCE_FOREGROUND = 'white'
FLASH_BACKGROUND = 'white'

class SpellTrainer(Frame): # pylint: disable=R0904

    delay = 3

    def __init__(self, master = None):
        '''Parses command line parameters, initializes the GUI and starts the main loop.'''

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
            modes.append(MODE_ATTACK)
        if 'd' in commands:
            modes.append(MODE_DEFENCE)
        if not spells or not modes:
            usage("At least one of s/m/u and one of a/d commands must be specified")
        self.spells = tuple(spells)
        self.modes = tuple(modes)

        # Initializing GUI
        Frame.__init__(self, master)
        self.configureMaster(self.master)
        self.configureFrame(self)
        self.text = StringVar()
        self.text.set(TITLE)
        self.textAspectRatio = self.estimateTextAspectRatio(self.spells + (TITLE,))
        self.label = self.createLabel(self, self.text)
        self.master.bind('<Configure>', self.resize)
        self.master.bind('<Key-Escape>', self.quit)

        # Initializing GUI
        start_new_thread(self.run, ()) # Start activity thread
        self.mainloop()

    @staticmethod
    def configureMaster(master):
        master.title(TITLE)
        master.wm_geometry('235x100')
        master.columnconfigure(0, weight = 1)
        master.rowconfigure(0, weight = 1)
        try: # Setting window icon
            icoFile = NamedTemporaryFile(delete = False)
            icoFile.write(b64decode('AAABAAEAEBAQAAEABAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAAAAAABMLAAATCwAAEAAAAAAAAAA3RkwA6OblAACw9wCLjY0AxszMAK+urQAAAAAA////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAZmZmZmZmZmZnd3d3d3d3dmd3d3d3d3d2Z3d3d3d3dQZnd0EDF3d2dmdAQCB3dwN2ZwdxAFd0Z3ZlF3dXd3Z3dmV3d3d3A3d2Yxd3d3Rnd3ZkB3d3dnd3dmdjd3cFd3d2Z3YAAEd3d3Znd3EXd3d3dmd3d3d3d3d2ZmZmZmZmZmYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'))
            icoFile.close()
            master.wm_iconbitmap(default = icoFile.name)
            remove(icoFile.name)
        except:
            pass # If we can't install icon for some reason, ok with that

    @staticmethod
    def configureFrame(frame):
        frame.grid(sticky = N+S+E+W)
        frame.rowconfigure(0, weight = 1)
        frame.columnconfigure(0, weight = 1)

    @staticmethod
    def createLabel(master, text):
        label = Label(master, textvariable = text, font = (FONT_NAME, FONT_SIZE, FONT_STYLE))
        label.grid(row = 0, column = 0, sticky = N+S+E+W)
        return label

    @staticmethod
    def estimateTextAspectRatio(strings):
        text = StringVar()
        label = Label(None, font = (FONT_NAME, -1000, FONT_STYLE), height = 1, textvariable = text)
        ret = 1000
        for s in strings:
            text.set(s)
            ret = min(ret, float(label.winfo_reqheight()) / label.winfo_reqwidth())
        return 0.78 * ret
    
    def resize(self, event = None): # event is unused # pylint: disable=W0613
        '''Called when window size or contents changes.'''
        self.label.configure(font = (FONT_NAME, -int(min(0.5 * self.winfo_height(), self.textAspectRatio * self.winfo_width())), FONT_STYLE))

    def quit(self, event = None): # event is unused # pylint: disable=W0221, W0613
        '''Overrides standard method to allow using as event handler.'''
        Frame.quit(self)

    def run(self):
        '''Activity method that performs the actual action.
           Must be run in a separate thread.'''
        seed()
        previousSpells = []
        while True:
            try:
                sleep(self.delay)
                self.label.configure(background = FLASH_BACKGROUND, foreground = FLASH_BACKGROUND)
                sleep(0.1)
                mode = choice(self.modes)
                spell = choice(self.spells)
                if mode == MODE_ATTACK:
                    baseSpell = spell.partition(' ')[0]
                    while baseSpell in previousSpells:
                        spell = choice(self.spells)
                        baseSpell = spell.partition(' ')[0]
                    previousSpells = (previousSpells + [baseSpell])[-(RULE_OF_N_SPELLS - 1):]
                    self.label.configure(background = ATTACK_BACKGROUND, foreground = ATTACK_FOREGROUND)
                elif mode == MODE_DEFENCE:
                    self.label.configure(background = DEFENCE_BACKGROUND, foreground = DEFENCE_FOREGROUND)
                else:
                    assert False # this should never happen
                self.text.set(spell)
                self.resize()
            except:
                pass # Sometimes exceptions fall out of Tkinter, just ignore them

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
