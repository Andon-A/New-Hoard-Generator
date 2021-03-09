#New Hoard Generator UI
# I hate UIs, but so far this hasn't been terrible.
# Doesn't help that it's simple.

import tkinter as tk
from tkinter import ttk
import os

import logging
import time
import configparser

# Start our logging. This needs to happen before we import the hoard generator
# (And it imports everything else)

starttime = time.strftime("%Y %m %d %H %M %S", time.localtime(time.time()))
# Make sure our logging folder exists.
if not os.path.isdir("./logs"):
    os.mkdir("./logs")
# And start logging.
logging.basicConfig(filename="./logs/output %s.log" % starttime, filemode='w', level=logging.DEBUG)
logging.info("Beginning log file for session starting: %s" % starttime)

# Now load our general configuration
cfg = configparser.ConfigParser()
cfg.read("./config/general.cfg")
logging.info("Config file loaded: ./config/general.cfg")

# And remove any excess log files.
llist = []
for l in os.listdir("./logs"):
    if l[-4:] == ".log":
        llist.append(l)
if len(llist) > cfg["General"].getint("logstokeep"):
    llist.sort(reverse=True) # Sort by oldest, since they're named by time.
    logs = len(llist)
    while len(llist) > cfg["General"].getint("logstokeep"):
        log = llist.pop()
        os.remove("./logs/%s" % log)
    logging.info("Removed %d old log files." % (logs - len(llist)))

# Now for the rest of the program.

import hoardgen

VER = hoardgen.VERSION
CR = hoardgen.MAXCR
DEFAULTPATH = os.path.abspath("./%s" % cfg["Folders"]["savefolder"])
# Make sure that default path exists.
if not os.path.isdir(DEFAULTPATH):
    os.mkdir(DEFAULTPATH)

lgfont = ("Times New Roman", 15)
stdfont = ("Times New Roman", 12)
boldfont = ("Times New Roman", 20, "bold")
smfont = ("Times New Roman", 8)
croptions = ["Random"]
for cr in range(0, CR+1):
    croptions.append(cr)

hoardsaved = False # If we've saved our hoard or not.
hoard = None # We'll put our current hoard here.

# Various functions we need.

def generateHoard():
    # This is what happens when we push our buttons.
    global hoard, nameentry, autoname, seedentry, autoseed, crentry, autocr, hoardsaved
    # Check if we're on automatic mode. CR first.
    if autocr.get() == 1:
        cr = None
    else:
        cr = validateCR(crentry)
    if autoname.get() == 1:
        name = None
    else:
        name = nameentry.get()
    if autoseed.get() == 1:
        seed = None
    else:
        seed = seedentry.get()
    hoard = hoardgen.Hoard(name=name, seed=seed, cr=cr)
    # Update our entries. Name first.
    nameentry.configure(state="normal")
    nameentry.delete(0, tk.END)
    nameentry.insert(0, hoard.name.name)
    if autoname.get() == 1:
        nameentry.configure(state="disabled")
    seedentry.configure(state="normal")
    seedentry.delete(0, tk.END)
    seedentry.insert(0, hoard.seed)
    if autoseed.get() == 1:
        seedentry.configure(state="disabled")
    crentry.configure(state="normal")
    crentry.delete(0, tk.END)
    crentry.insert(0, "%d" % hoard.cr)
    if autocr.get() == 1:
        crentry.configure(state="disabled")
    fillTreasures()
    fillItems()
    hoardsaved = False
    return

def fillTreasures():
    # Fills the "Treasures" text area with our treasures.
    global treasuretext
    trstr = ""
    trstr += "%d gp total value\n" % (hoard.treasure.value + hoard.gp)
    trstr += "%d gold pieces\n" % hoard.gp
    trstr += hoard.treasure.description
    treasuretext.configure(state="normal")
    treasuretext.delete("1.0", tk.END)
    treasuretext.insert("1.0", trstr)
    treasuretext.configure(state="disabled")
    return

dropdown = {}

def fillItems():
    # fills the "Items" text area with our items.
    global itemtext, inspectordropdown, inspectvar, dropdown
    istr = ""
    dropdown = {}
    for i in hoard.items:
        r = i.rarity
        if r == "veryrare":
            r = "very rare"
        istr += "%s\n" % i.name
        dropdown[i.name] = i
    itemtext.configure(state="normal")
    itemtext.delete("1.0", tk.END)
    itemtext.insert("1.0", istr)
    itemtext.configure(state="disabled")
    # Update the dropdown box.
    menu = inspectordropdown["menu"]
    menu.delete(0, tk.END)
    for i in dropdown:
        menu.add_command(label=i, command = lambda value=dropdown[i]: inspectItem(value))
    inspectvar.set("Select an item to view")
    inspectortext.configure(state="normal")
    inspectortext.delete("1.0", tk.END)
    inspectortext.configure(state="disabled")
    return

def inspectItem(i):
    global hoard, inspectvar, inspectortext
    inspectvar.set(i.name)
    istr = ""
    if i is not None:
        inspectvar.set(i.name)
        # We have an item!
        istr += i.source + "\n"
        if i.info is not None:
            istr += i.info + "\n"
        if i.description is not None:
            istr += i.description
    else:
        inspectvar.set(i)
    istr = istr.replace("\n", "\n\n") # Separating things further helps.
    # Clean up the box.
    inspectortext.configure(state="normal")
    inspectortext.delete("1.0", tk.END)
    inspectortext.insert("1.0", istr)
    inspectortext.configure(state="disabled")
    return

def resetPath(path):
    path.delete(0,tk.END)
    path.insert(0, DEFAULTPATH)
    return

def autoChange(var, entry):
    # Turns the given entry on or off.
    if var.get() == 1:
        entry.configure(state="disabled")
    else:
        entry.configure(state="normal")
    return

def validateCR(cr):
    crstr = cr.get()
    try:
        crstr = int(crstr)
    except:
        try:
            crstr = float(crstr)
        except:
            pass
    if type(crstr) == float:
        # Round it.
        crstr = round(crstr)
    if type(crstr) != int:
        # Bad info.
        crstr = 0
    if crstr > CR:
        # Too high.
        crstr = CR
    elif crstr < 0:
        # Too low.
        crstr = 0
    # Clean out the old.
    cr.delete(0, tk.END)
    # Insert the new
    cr.insert(0, "%d" % crstr)
    return crstr

def saveHoard(fpath):
    global hoard, hoardsaved
    # Saves the hoard!
    # Make sure we have a valid save path.
    path = validatePath(fpath)
    if not path:
        warnBox("Invalid Path!\nCheck spelling and device connection.")
        return
    # We have a valid path. Get our save name.
    sname = hoard.getSaveName() + ".pdf"
    # Do we exist?
    if os.path.isfile(path + "\\" + sname):
        warnBox("%s\nThis file already exists in the folder\n%s" % (sname, path), width=500, height=120)
        return
    # OK, cool. Now we can save the file.
    hoard.saveHoard(savedir=path)
    warnBox("File saved!\n%s saved in\n%s" % (sname, path), width=500, height=120)
    hoardsaved = True
    return
    
def validatePath(fpath):
    # Validates the given file path.
    # Returns true if the path exists. False if it doesn't.
    fstr = fpath.get()
    abspath = os.path.abspath(fstr)
    if os.path.isdir(abspath):
        return abspath
    else:
        return False

def centerScreen(tkwindow, xsize, ysize):
    # Returns the required string to open the window in the middle of the screen.
    screenwidth = tkwindow.winfo_screenwidth()
    screenheight = tkwindow.winfo_screenheight()
    xpos = int((screenwidth/2) - (xsize/2))
    ypos = int((screenheight/2) - (ysize/2))
    locstr = "%dx%d+%d+%d" % (xsize, ysize, xpos, ypos)
    return locstr

def centerScreenOnScreen(tkwindow, xsize, ysize):
    # Returns coordinates for a window of given size to be centered on the 
    # passed window argument.
    winwidth = tkwindow.winfo_width()
    winheight = tkwindow.winfo_height()
    wxpos = tkwindow.winfo_x()
    wypos = tkwindow.winfo_y()
    xpos = int((winwidth/2) - (xsize/2) + wxpos)
    ypos = int((winheight/2) - (ysize/2) + wypos)
    locstr = "%dx%d+%d+%d" % (xsize, ysize, xpos, ypos)
    return locstr

def warnBox(text, width=250, height=100):
    global window
    # Warns the user of... something.
    win = tk.Toplevel()
    win.title("Path Error")
    win.geometry(centerScreenOnScreen(window, width, height))
    win.minsize(width, height)
    warntext = tk.Label(win, text=text, font=stdfont)
    okbutton = tk.Button(win, text="OK", relief=tk.RAISED, font=lgfont, command=win.destroy)
    mincol = round(width/5)
    win.grid_columnconfigure(0, minsize=mincol)
    win.grid_columnconfigure(1, minsize=mincol)
    win.grid_columnconfigure(2, minsize=mincol)
    win.grid_columnconfigure(3, minsize=mincol)
    win.grid_columnconfigure(4, minsize=mincol)
    warntext.grid(row=0, column=0, columnspan=5)
    okbutton.grid(row=2, column=2)
    win.focus_force()
    

def exitWindow():
    global window, hoardsaved
    # An exit confirmation button.
    win = tk.Toplevel()
    win.title("Really Quit?")
    win.geometry(centerScreenOnScreen(window, 250, 100))
    win.minsize(250, 100)
    win.resizable(False, False)
    exittext = tk.Label(win, text="Do you really want to exit?", font=stdfont)
    savetext = tk.Label(win, text="Your Hoard has not been saved!", font=stdfont)
    yesbutton = tk.Button(win, text="Yes", relief=tk.RAISED, font=lgfont, command=window.destroy)
    nobutton = tk.Button(win, text="No", relief=tk.RAISED, font=lgfont, command=win.destroy)
    win.grid_columnconfigure(0, minsize=50)
    win.grid_columnconfigure(1, minsize=50)
    win.grid_columnconfigure(2, minsize=50)
    win.grid_columnconfigure(3, minsize=50)
    win.grid_columnconfigure(4, minsize=50)
    exittext.grid(row=0, column=0, columnspan=5)
    if not hoardsaved:
        savetext.grid(row=1, column=0, columnspan=5)
    yesbutton.grid(row=2, column=1, pady=10)
    nobutton.grid(row=2, column=3, pady=10)
    win.focus_force()

# Set up our (main) window
window = tk.Tk()
window.minsize(1300, 800) # Starting size.
window.resizable(False, False) # No resizing. Sorry!
window.title("New Hoard Generator v%s" % VER) # Window title.
window.pack_propagate(0)

# Main title!
# Make the frame
titleframe = tk.Frame(window, height=1)
# Exit button
exitbutton = tk.Button(titleframe, text="Exit", relief=tk.RAISED, font=stdfont,
                    command=exitWindow)
# And of course, the title.
mainlabel = ttk.Label(titleframe, text="New Hoard Generator v%s" % VER, font=boldfont)
exitbutton.pack(side=tk.RIGHT, padx=10)
mainlabel.pack(side=tk.LEFT)

# Set up our frames.
mainframe = tk.Frame(window, width=400)
treasureframe = tk.Frame(window, width=450)
rightframe = tk.Frame(window, width=450)
itemframe = tk.Frame(rightframe)
inspectorframe = tk.Frame(rightframe)

# Main frame stuff goes here.
# Set the grid up. We want 4x 100 wide columns.
mainframe.grid_columnconfigure(0, minsize=100)
mainframe.grid_columnconfigure(1, minsize=100)
mainframe.grid_columnconfigure(2, minsize=100)
mainframe.grid_columnconfigure(3, minsize=100)

# Name entry bits.
namelabel = ttk.Label(mainframe, text="Hoard Name", font=stdfont)
nameentry = tk.Entry(mainframe, width=60)
nameentry.configure(state="disabled")
autoname = tk.IntVar(mainframe, value=1)
autonamecheck = tk.Checkbutton(mainframe, variable=autoname, onvalue=1, offvalue=0,
                    text="Auto", command= lambda: autoChange(autoname, nameentry))

# Seed entry bits.                    
seedlabel = ttk.Label(mainframe, text="Seed", font=stdfont)
seedentry = tk.Entry(mainframe, width=60)
seedentry.configure(state="disabled")
autoseed = tk.IntVar(mainframe, value=1)
autoseedcheck = tk.Checkbutton(mainframe, variable=autoseed, onvalue=1, offvalue=0,
                    text="Auto", command= lambda: autoChange(autoseed, seedentry))

# CR Entry bits.
crlabel = ttk.Label(mainframe, text="CR", font=stdfont)
crentry = tk.Entry(mainframe, width=4)
crentry.configure(state="disabled")
autocr = tk.IntVar(mainframe, value=1)
autocrcheck = tk.Checkbutton(mainframe, variable=autocr, onvalue=1, offvalue=0,
                    text="Random", command= lambda: autoChange(autocr, crentry)) 

# Generate New button
newbutton = tk.Button(mainframe, text="Generate Hoard", relief=tk.RAISED,
                font=lgfont,
                command= generateHoard)

# Folder path
pathlabel = ttk.Label(mainframe, text="File Path", font=stdfont)
pathentry = tk.Entry(mainframe, width=60)
# Ger our default path and insert it.
pathentry.insert(0, DEFAULTPATH)
pathreset  = tk.Button(mainframe, text="Reset", relief=tk.RAISED, font=stdfont,
                command= lambda: resetPath(pathentry))

# Save button.
savehoard = tk.Button(mainframe, text="Save Hoard", relief=tk.RAISED,
                font=stdfont, command = lambda: saveHoard(pathentry))

# And put them inside.
# Name entry
namelabel.grid(row=0, column=0, columnspan=3, sticky="W", padx=10)
nameentry.grid(row=1, column=0, columnspan=3, sticky="W", padx=10, pady=10)
# Automatic Name checkbox
autonamecheck.grid(row=1, column=3)
# Seed
seedlabel.grid(row=2, column=0, columnspan=3, sticky="W", padx=10)
seedentry.grid(row=3, column=0, columnspan=3, sticky="W", padx=10, pady=10)
# Automatic seed checkbox.
autoseedcheck.grid(row=3, column=3)
# File path
pathlabel.grid(row=4, column=0, columnspan=3, sticky="W", padx=10)
pathentry.grid(row=5, column=0, columnspan=3, sticky="W", padx=10, pady=10)
pathreset.grid(row=5, column=3)
#autopathcheck.grid(row=5, column=3)
# CR Entry
crlabel.grid(row=6, column=0, sticky="W", padx=10)
crentry.grid(row=7, column=0, sticky="W", padx=10, pady=10)
autocrcheck.grid(row=7, column=0, sticky="E")
#croption.grid(row=7, column=0, sticky="W", pady=10)
# Generate Button
newbutton.grid(row=7, column=1, columnspan=2)
# Save button
savehoard.grid(row=7, column=3, pady=10)

# And now for some "fun" stuff.
# Count how many things of everything we have.
itemct = 0
for t in hoardgen.itemgen.itemtypes:
    itemct += len(hoardgen.itemgen.getCategoryList(t))
effectct = len(hoardgen.itemgen.getCategoryList("effect"))
prefixct = len(hoardgen.itemgen.getCategoryList("effect", "prefix"))
suffixct = len(hoardgen.itemgen.getCategoryList("effect", "suffix"))
treasurect = len(hoardgen.treasuregen.getTreasureList())
staticct = 0
for t in hoardgen.staticitem.cfg["common"]:
    staticct += len(hoardgen.staticitem.getCategoryList(t))
# Now make some labels.
itemctlabel = ttk.Label(mainframe, text="Base Items: %d" % itemct, font=stdfont)
effectctlabel = ttk.Label(mainframe, text="Effects: %d" % effectct, font=stdfont)
prefixctlabel = ttk.Label(mainframe, text="Prefixes: %d" % prefixct, font=stdfont)
suffixctlabel = ttk.Label(mainframe, text="Suffixes: %d" % suffixct, font=stdfont)
treasurectlabel = ttk.Label(mainframe, text="Treasures: %d" % treasurect, font=stdfont)
staticctlabel = ttk.Label(mainframe, text="Premade Items: %d" % staticct, font=stdfont)
# And put them in.
itemctlabel.grid(row=9, column=0, sticky="W")
effectctlabel.grid(row=10, column=0, sticky="W")
prefixctlabel.grid(row=9, column=1, sticky="W")
suffixctlabel.grid(row=10, column=1, sticky="W")
treasurectlabel.grid(row=9, column=2, sticky="W")
staticctlabel.grid(row=10, column=2, sticky="W")


# Treasure frame stuff goes here.
# It's a scrollable text area.
treasurelabel = ttk.Label(treasureframe, text="Treasures", font=stdfont)
treasuretext = tk.Text(treasureframe, width=50, height=25, wrap="none")
treasurevscroll = tk.Scrollbar(treasureframe, orient="vertical", command=treasuretext.yview)
treasurehscroll = tk.Scrollbar(treasureframe, orient="horizontal", command=treasuretext.xview)
treasuretext.configure(yscrollcommand=treasurevscroll.set, xscrollcommand=treasurehscroll.set, state="disabled")
# Put them all inside.
treasurelabel.grid(row=0, column=0, sticky="N")
treasuretext.grid(row=1, column=0, sticky="NSEW")
treasurevscroll.grid(row=1, column=1, sticky="NS")
treasurehscroll.grid(row=2, column=0, sticky="EW")
treasureframe.grid_rowconfigure(1, weight=1)
treasureframe.grid_columnconfigure(0, weight=1)


# Right hand frame. Has the item frame and inspector frame.

# First, the item frame.
# It's largely identical to the Treasure stuff.
itemlabel = ttk.Label(itemframe, text="Items", font=stdfont)
itemtext = tk.Text(itemframe, width=50, height=10, wrap="none")
itemvscroll = tk.Scrollbar(itemframe, orient="vertical", command=itemtext.yview)
itemhscroll = tk.Scrollbar(itemframe, orient="horizontal", command=itemtext.xview)
itemtext.configure(yscrollcommand=itemvscroll.set, xscrollcommand=itemhscroll.set, state="disabled")

itemlabel.grid(row=0, column=0, sticky="N")
itemtext.grid(row=1, column=0, sticky="NSEW")
itemvscroll.grid(row=1, column=1, sticky="NS")
itemhscroll.grid(row=2, column=0, sticky="EW")
itemframe.grid_rowconfigure(1, weight=1)
itemframe.grid_columnconfigure(0, weight=1)
itemframe.pack(side=tk.TOP, fill=tk.X, expand=True, anchor="n")

# Now the inspectorframe.
inspectorlabel = ttk.Label(inspectorframe, text="Item Inspector", font=stdfont)
inspectortext = tk.Text(inspectorframe, width=50, height=25, wrap="word")
inspectorvscroll = tk.Scrollbar(inspectorframe, orient="vertical", command=inspectortext.yview)
inspectorspacer = ttk.Label(inspectorframe)
inspectvar = tk.StringVar(inspectorframe)
inspectvar.set("Select an item to view")
inspectordropdown = tk.OptionMenu(inspectorframe, inspectvar, "Select an item to view")
inspectortext.configure(yscrollcommand=inspectorvscroll.set, state="disabled")

inspectorlabel.grid(row=0, column=0, sticky="N")
inspectordropdown.grid(row=1, column=0, sticky="NEW")
inspectortext.grid(row=2, column=0, sticky="NSEW")
inspectorvscroll.grid(row=2, column=1, sticky="NS")
inspectorspacer.grid(row=3, column=0, sticky="EW")
inspectorframe.grid_rowconfigure(2, weight=1)
inspectorframe.grid_columnconfigure(0, weight=1)
inspectorframe.pack(side=tk.TOP, fill=tk.BOTH, expand=True, anchor="n")


# Shove our frames into the main window.
# And also the exit button.
titleframe.pack(side=tk.TOP, fill=tk.X)
mainframe.pack(side=tk.LEFT, fill=tk.Y, expand=True)
treasureframe.pack(side=tk.LEFT, fill=tk.Y, expand=True)
rightframe.pack(side=tk.LEFT, fill=tk.Y, expand=True)
#itemframe.pack(side=tk.LEFT, fill=tk.Y, expand=True)
window.focus_force()

generateHoard()

# Run our loop.
window.mainloop()