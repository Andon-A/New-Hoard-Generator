#New Hoard Generator UI
# I hate UIs, but so far this hasn't been terrible.
# Doesn't help that it's simple.

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

import hoardgen

VER = hoardgen.VERSION
CR = hoardgen.MAXCR

stdfont = ("Times New Roman", 15)
boldfont = ("Times New Roman", 20, "bold")
smfont = ("Times New Roman", 8)
croptions = ["Random"]
for cr in range(0, CR+1):
    croptions.append(cr)

# Set all the functions we need here.
def autoName():
    if autoname.get() == 1:
        nameentry.configure(state="disabled")
    else:
        nameentry.configure(state="normal")
    return

def autoSeed():
    if autoseed.get() == 1:
        seedentry.configure(state="disabled")
    else:
        seedentry.configure(state="normal")
    return

# Set up our (main) window
window = tk.Tk()
window.minsize(1200, 800) # Starting size.
window.resizable(False, False) # No resizing. Sorry!
window.title("New Hoard Generator v%s" % VER) # Window title.

# Main title!
mainlabel = ttk.Label(window, text="New Hoard Generator v%s" % VER, font=boldfont)

# Set up our frames.
mainframe = tk.Frame(window, width=400)#, background="green")
#mainframe.grid_propagate(0)
#mainframe.pack_propagate(0)
treasureframe = tk.Frame(window, width=400)
itemframe = tk.Frame(window, width=400)

# Main frame stuff goes here.
# Set the grid up. We want 4x 100 wide columns.
mainframe.grid_columnconfigure(0, minsize=100)
mainframe.grid_columnconfigure(1, minsize=100)
mainframe.grid_columnconfigure(2, minsize=100)
mainframe.grid_columnconfigure(3, minsize=100)

# Name entry bits.
namelabel = ttk.Label(mainframe, text="Hoard Name", font=stdfont)
nameentry = tk.Entry(mainframe, width=60)
autoname = tk.IntVar(mainframe)
autonamecheck = tk.Checkbutton(mainframe, variable=autoname, onvalue=1, offvalue=0,
                    text="Auto", command=autoName) 

# Seed entry bits.                    
seedlabel = ttk.Label(mainframe, text="Seed", font=stdfont)
seedentry = tk.Entry(mainframe, width=60)
autoseed = tk.IntVar(mainframe)
autoseedcheck = tk.Checkbutton(mainframe, variable=autoseed, onvalue=1, offvalue=0,
                    text="Auto", command=autoSeed) 

# CR Entry bits.
crlabel = ttk.Label(mainframe, text="CR", font=stdfont)
crvar = tk.StringVar(mainframe)
crvar.set(croptions[0])
croption = tk.OptionMenu(mainframe, crvar, *croptions)

# Generate New button
newbutton = tk.Button(mainframe, text="Generate Hoard", relief=tk.RAISED, font=stdfont)

# Folder path


# ANd put them inside.
# Name entry
namelabel.grid(row=0, column=0, columnspan=3, sticky="W")
nameentry.grid(row=1, column=0, columnspan=3, sticky="W", pady=10)
# Automatic Name checkbox
autonamecheck.grid(row=1, column=3)
# Seed
seedlabel.grid(row=2, column=0, columnspan=3, sticky="W")
seedentry.grid(row=3, column=0, columnspan=3, sticky="W", pady=10)
# Automatic seed checkbox.
autoseedcheck.grid(row=3, column=3)
# CR Entry
crlabel.grid(row=4, column=0, sticky="W")
croption.grid(row=5, column=0, sticky="W", pady=10)

# Generate Button
newbutton.grid(row=5, column=2, columnspan=2)


# Treasure frame stuff goes here.
# It's a scrollable text area.
treasurelabel = ttk.Label(treasureframe, text="Treasures", font=stdfont)
treasuretext = tk.Text(treasureframe, width=40, height=25, wrap="none")
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

# Item frame stuff goes here.
# It's largely identical to the Treasure stuff.
itemlabel = ttk.Label(itemframe, text="Items", font=stdfont)
itemtext = tk.Text(itemframe, width=40, height=25, wrap="none")
itemvscroll = tk.Scrollbar(itemframe, orient="vertical", command=itemtext.yview)
itemhscroll = tk.Scrollbar(itemframe, orient="horizontal", command=itemtext.xview)
itemtext.configure(yscrollcommand=itemvscroll.set, xscrollcommand=itemhscroll.set, state="disabled")
itemlabel.grid(row=0, column=0, sticky="N")
itemtext.grid(row=1, column=0, sticky="NSEW")
itemvscroll.grid(row=1, column=1, sticky="NS")
itemhscroll.grid(row=2, column=0, sticky="EW")
itemframe.grid_rowconfigure(1, weight=1)
itemframe.grid_columnconfigure(0, weight=1)

# Shove our frames into the main window.
mainlabel.pack(side=tk.TOP, fill=tk.X)
mainframe.pack(side=tk.LEFT, fill=tk.Y, expand=True)
treasureframe.pack(side=tk.LEFT, fill=tk.Y, expand=True)
itemframe.pack(side=tk.LEFT, fill=tk.Y, expand=True)
    

# Run our loop.
window.mainloop()