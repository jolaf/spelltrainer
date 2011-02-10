#!/usr/bin/python
#
# SpellTrainer.py
#
# by Vasily Zakharov (vmzakhar@gmail.com)
# http://code.google.com/p/spelltrainer/
#
# Uses TkInter for GUI: http://wiki.python.org/moin/TkInter
#
# Version 1.03
#
from base64 import b64decode
from getopt import getopt
from os import remove
from random import choice, seed
from sys import argv, exit # exit redefined # pylint: disable=W0622
from tempfile import NamedTemporaryFile
from thread import start_new_thread
from time import sleep

from Tkinter import Frame, Label, StringVar, N, S, E, W

TITLE = 'SpellTrainer v1.02'

SIMPLA = ('Impedimenta', 'Tarantallegra', 'Silencio',		# Protego
          'Rictusempra', 'Incarcero', 'Mento Menores',		# Defendo
          'Stupefy', 'Achelitus', 'Maledicero',			# Enervate
          'Incendio', 'Deluvium', 'Tormencio', 'Conjunctivitus')# VIP

MAXIMA = tuple(s + ' Maxima' for s in SIMPLA) + ('Petrificus Totalus', 'Expelliarmus')

ULTIMA = tuple(s + ' Ultima' for s in SIMPLA)

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
            icoFile.write(b64decode('AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAAAABMLAAATCwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHJSb/8AAAAAAAAAAAAAAAAAAAAAAAAAAP//9v///v////Sy/wAAAAAAAAAA///u/wAAAAAAAAAAAAAAAGIALv+rQgD/gWhg/wAAAAAAAAAA//+w///7/////7T///qg//Cr7v/t5eH/9//D//uX0P///+j/AAAAAD8AF///4m3/vC0A/7m62P///+z///+1////7v//mMj/mtGZ/6DK1v+L4Fb/+G+3/63amP+yws3/7P/6/0sABP//5nf/oBUA/4eU0/8AAAAA/8Sp//+x///Zvqv/epN+//+9z/+Z0Xf/vbbB/5rFv/+zra7/r/53/0kAFP//44v/nhsA/4mX1/8AAAAAAAAAAGj/cP/CrY3/fcaL/+biof9Z3D7//+p1////s/8AAAAA/P/n/0oAL///633/px0A/5+Pf/8AAAAAAAAAAAAAAADilfL/3e5M/7mozv/aoJ7/AAAAAAAAAAAAAAAAAAAAAEgAB///7H//xSQA/zeihv/44/j///TD/wAAAAAAAAAAqu5o/+/p9/8AAAAAAAAAAAAAAAAAAAAAAAAAAD8AHP//5XT/qyEA/2NxqP/4/6z/eKJH//z+0P8AAAAAAAAAAOHh9P8AAAAAAAAAAP//tf8AAAAA///k/2kXNP//AAD/oA0A/4upxv8AAAAAopK8/8isz////+P/AAAAAAAAAAAAAAAAo6aL////vv/Gm6L/A1Fg/+PWsv+tAAD/uQAA/4jD4P8AAAAA//+6//7Q9P978G7//6Te///w7P8AAAAAAAAAAP//zf8AfWT/DRxJ/wBNUv+Cr3D/Ia48/6O6xv8AAAAA///2//7/0/+2fnH/t7OL//7z1P8AAAAAAAAAAP//wv+/kKH/CR1X//KyeP/+/9j/YRMv/2iZn///657/AAAAAAAAAAC8oOz/fPVY/9HIxv////v/AAAAAAAAAAAAAAAAADM+/wBiYv///9n/uef//6ntdv8APFn/yL23/wAAAAD9t73/ddlO/750/////7T////2/wAAAAAAAAAA//+4/wAAAAAAHmL/ciQm/5/6iP8AAAj/rNTY//+mtP+k2lz/eKZM/7q/xP///Lf/AAAAAAAAAAAAAAAAAAAAAAAAAACtuFr/euBr/0hko/8AGjn/ysri/02vAP/j2Oz/yt/q/9bL4f8AAAAA///2/wAAAAAAAAAAAAAAAAAAAAAAAAAA9/P//wAAAAD/44v/0LO8////vP///v//AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//0AAPG4AADAEAAAAAEAAAADAAABBwAADwMAAD4DAABoIwAAgEEAAICDAAAAwwAAgIMAAEAPAACALwAAof8AAA=='))
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
