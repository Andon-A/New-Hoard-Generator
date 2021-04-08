#!/usr/bin/env python3

# New Hoard Generator UI
# Take 2. Or: Can I put things into classes to simplify them.


import tkinter as tk
import tkinter.font as tkFont
import tkinter.filedialog as filedialog
from tkinter import ttk
import copy
import logging
import os
import time
import configs
import hoardgen
import pdfwrite
 
 
general = configs.GENERAL 
 
# Setup some constants and other variables.
# default save path. As with the logs, this should be easily modified for use
# with a system-dependent folder method


class Window (tk.Tk):
    # This just has a few other additional options in it.
    def __init__(self):
        tk.Tk.__init__(self)
        self.grid_propagate(0)
        # Some hoard stuff
        self.hoard_saved = False
        self.hoard_edited = False
        self.hoard = None
        # Window things.
        self.minsize(1300, 800)
        self.resizable(False, False)
        self.title("New Hoard Generator v%s" % configs.VERSION)
        self.pack_propagate(0)
        # Set up our columns.
        self.grid_columnconfigure(0, minsize=400)
        self.grid_columnconfigure(1, minsize=450)
        self.grid_columnconfigure(2, minsize=450)
        self.grid_rowconfigure(0, minsize=30)
        self.grid_rowconfigure(1, minsize=385)
        self.grid_rowconfigure(2, minsize=385)
        # And font stuff.
        self.font_family = general.get("UI", "font_family")
        if self.font_family not in list(tkFont.families()):
            self.font_family = "Arial"
        self.title_font = tkFont.Font(family=self.font_family,
            size=general.getInt("UI", "title_font_size"), weight="bold")
        self.large_font = tkFont.Font(family=self.font_family,
            size=general.getInt("UI", "heading_font_size"))
        self.standard_font = tkFont.Font(family=self.font_family,
            size=general.getInt("UI", "standard_font_size"))
        self.small_font = tkFont.Font(family=self.font_family,
            size=general.getInt("UI", "small_font_size"))
    
    def generateHoard(self, name, seed, cr):
        # Push button, get shiny things.
        # It's a lot easier than the previous one.
        self.hoard = hoardgen.Hoard(name=name, seed=seed, cr=cr)
        self.hoard_saved = False
        return self.hoard.name.name, self.hoard.seed, self.hoard.cr
        
    def getHoardItems(self):
        item_list = []
        for item in self.hoard.items:
            item_list.append(item.getName())
        item_list = "\n".join(item_list)
        while "\n\n" in item_list:
            item_list = item_list.replace("\n\n", "\n")
        return item_list
    
    def getHoardTreasures(self, only_gp_value=False):
        treasure_str = "%d total gp value" % (self.hoard.treasure.value + self.hoard.gp)
        treasure_str += "\n%d gold pieces" % self.hoard.gp
        treasure_str += "\n%d gp in treasures" % self.hoard.treasure.value
        if not only_gp_value:
            treasure_str += "\n%s" % self.hoard.treasure.getDescription()
        while "\n\n" in treasure_str:
            treasure_str.replace("\n\n", "\n")
        return treasure_str
        
    
    def centerOnWindow(self, x_size, y_size):
        # Centers the new sub-window on the main window.
        # Should work fine with multiple monitors, but might get fudgy
        # if the window is shoved too far off-screen.
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        window_xpos = self.winfo_x()
        window_ypos = self.winfo_y()
        x_pos = int((window_width/2) - (x_size/2) + window_xpos)
        y_pos = int((window_height/2) - (y_size/2) + window_ypos)
        loc_str = "%dx%d+%d+%d" % (x_size, y_size, x_pos, y_pos)
        return loc_str
    
    def centerOnScreen(self, x_size, y_size):
        # Centers the new sub_window on the main monitor (I think)
        # Should work fine with multi-monitors.
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_pos = int((screen_width/2) - (x_size/2))
        y_pos = int((screen_height/2) - (y_size/2))
        loc_str = "%dx%d+%d+%d" % (x_size, y_size, x_pos, y_pos)
        return loc_str
        
    def exitWindow(self):
        # Do you really want to quit?
        # Warns if the current hoard has not been saved.
        window = tk.Toplevel()
        window.title("Really Quit?")
        if general.getBool("UI", "center_warning_on_window"):
            window.geometry(self.centerOnWindow(250, 100))
        else:
            window.geometry(self.centerOnScreen(250, 100))
        window.resizable(False, False)
        # Set up our text and buttons.
        exit_text = tk.Label(window, text="Do you really want to quit?", font=self.standard_font)
        save_text = tk.Label(window, text="Your current hoard has not been saved!",
            font= self.standard_font)
        yes_button = tk.Button(window, text="Yes", relief=tk.RAISED, font=self.large_font, 
            command=self.destroy)
        no_button = tk.Button(window, text="No", relief=tk.RAISED, font=self.large_font,
            command=window.destroy)
        # Grid time.
        window.grid_columnconfigure(0, minsize=50)
        window.grid_columnconfigure(1, minsize=50)
        window.grid_columnconfigure(2, minsize=50)
        window.grid_columnconfigure(3, minsize=50)
        window.grid_columnconfigure(4, minsize=50)
        #And put things in.
        exit_text.grid(row=0, column=0, columnspan=5)
        if not self.hoard_saved:
            save_text.grid(row=1, column=0, columnspan=5)
        yes_button.grid(row=2, column=1, pady=10)
        no_button.grid(row=2, column=3, pady=10)
        window.focus_force()

class titlePane(tk.Frame):
    # It holds the title!
    def __init__(self, main):
        tk.Frame.__init__(self, master=main, height=1)
        self.grid_propagate(0)
        self.exit_button = tk.Button(self, text="Exit", relief=tk.RAISED,
            font=main.standard_font, command=main.exitWindow)
        self.main_title = ttk.Label(self, text="New Hoard Generator v%s" % configs.VERSION,
            font=main.title_font)
        self.exit_button.pack(side=tk.RIGHT, padx=10, pady=5)
        self.main_title.pack(side=tk.LEFT)
              
class inputPane(tk.Frame):
    # This is the pane where we put all the info. Seed, name, etc.
    def __init__(self, main, item_pane, treasure_pane, edit_pane):
        # Basic setup.
        tk.Frame.__init__(self, master=main)
        self.grid_propagate(0)
        self.item_pane = item_pane
        self.treasure_pane = treasure_pane
        self.edit_pane = edit_pane
        # First, we need all of our inputs. Text inputs first.
        self.name_label = ttk.Label(self, text="Hoard Name", font=main.large_font)
        self.name_entry = tk.Entry(self, font=main.standard_font)
        self.name_entry.configure(state="readonly") # Auto-name will toggle.
        self.seed_label = ttk.Label(self, text="Hoard Seed", font=main.large_font)
        self.seed_entry = tk.Entry(self, font=main.standard_font)
        self.seed_entry.configure(state="readonly")
        self.cr_label = ttk.Label(self, text="Hoard CR", font=main.large_font)
        self.cr_entry = tk.Entry(self, font=main.standard_font, width=3)
        self.cr_entry.configure(state="readonly")
        # Toggle boxes.
        self.auto_name_var = tk.BooleanVar(self, value=True)
        self.auto_name = tk.Checkbutton(self, variable=self.auto_name_var,
            onvalue=True, offvalue=False, text="Auto", font=main.standard_font,
            command=lambda: self.autoChange(self.auto_name_var, self.name_entry))
        self.auto_seed_var = tk.BooleanVar(self, value=True)
        self.auto_seed = tk.Checkbutton(self, variable=self.auto_seed_var,
            onvalue=True, offvalue=False, text="Auto", font=main.standard_font,
            command=lambda: self.autoChange(self.auto_seed_var, self.seed_entry))
        self.auto_cr_var = tk.BooleanVar(self, value=True)
        self.auto_cr = tk.Checkbutton(self, variable=self.auto_cr_var,
            onvalue=True, offvalue=False, text="Auto", font=main.standard_font,
            command=lambda: self.autoChange(self.auto_cr_var, self.cr_entry))
        self.only_gp_var = tk.BooleanVar(self, value=False)
        self.only_gp = tk.Checkbutton(self, variable=self.only_gp_var,
            onvalue=False, offvalue=True, text="Show Treasure", font=main.standard_font,
            command=self.updateTreasures)
        self.generate_button = tk.Button(self, text="Generate Hoard", relief=tk.RAISED,
            font=main.large_font, command=self.generateHoard)
        self.save_button = tk.Button(self, text="Save Hoard", relief=tk.RAISED,
            font=main.large_font, command=self.saveHoard)
        # Configure the grid. 4x 100px wide columns
        self.grid_columnconfigure(0, minsize=100)
        self.grid_columnconfigure(1, minsize=100)
        self.grid_columnconfigure(2, minsize=100)
        self.grid_columnconfigure(3, minsize=100)
        # And put things in it.
        self.name_label.grid(row=0, column=0, columnspan=3, sticky="W", padx=10)
        self.name_entry.grid(row=1, column=0, columnspan=3, sticky="EW", padx=10, pady=10)
        self.auto_name.grid(row=1, column=3, sticky="W")
        self.seed_label.grid(row=2, column=0, columnspan=3, sticky="W", padx=10)
        self.seed_entry.grid(row=3, column=0, columnspan=3, sticky="EW", padx=10, pady=10)
        self.auto_seed.grid(row=3, column=3, sticky="W")
        self.cr_label.grid(row=4, column=0, sticky="W", padx=10)
        self.cr_entry.grid(row=5, column=0, sticky="W", padx=10, pady=10)
        self.auto_cr.grid(row=5, column=0, sticky="E")
        self.only_gp.grid(row=4, column=1)
        self.generate_button.grid(row=7, column=1, columnspan=2, pady=10)
        self.save_button.grid(row=8, column=1, columnspan=2, pady=10)
       
    def saveHoard(self):
        # Saves our hoard.
        files = [("PDF", "*.pdf")]
        hoard = self.master.hoard
        path = general.get("General", "last_save_path")
        if not os.path.isdir(path):
            # The path no longer exists. Return to default.
            path = None
        if path is None:
            path = configs.data_folder
            path += "\\" + general.get("Folders", "save_folder")
            if not os.path.isdir(path):
                os.mkdir(path)
        filename = filedialog.asksaveasfilename(filetypes=files, 
            defaultextension=files, initialdir=path,
            initialfile="%s (%d).pdf" % (hoard.name.name, hoard.cr))
        # Get the folder of the savename and save that as our last save dir.
        general.set("General", "last_save_path", filename[:filename.rfind("/")])
        general.save()
        seed = hoard.seed
        if self.master.hoard_edited:
            seed += " (edited)"
        pdf = pdfwrite.PDF(hoard.name.name, seed, hoard.cr)
        # Get the treasure info and save it.
        treasure_info = "Treasure (%d gp total value)" % (hoard.treasure.value + hoard.gp)
        treasure_desc = "%d gold pieces\n%d gp in treasures" % (hoard.gp, hoard.treasure.value)
        if not self.only_gp_var.get():
            treasure_desc += "\n" + hoard.treasure.getDescription()
        pdf.addItem(iinfo=treasure_info, idesc=treasure_desc, indent=False)
        # And all our files.
        for item in hoard.items:
            indent = True
            if item.id == "spellbook":
                indent = False
            pdf.addItem(iname=item.getName(), iinfo=item.getInfo(),
                idesc=item.getDescription(), indent=indent)
        self.master.hoard_saved = True
        logging.debug("Saved hoard at %s" % filename)
        pdf.output(filename)
       
    def autoChange(self, variable, entry):
        # Changes if the entry is available or not.
        if variable.get():
            entry.configure(state="readonly")
        else:
            entry.configure(state="normal")
            
    def updateTreasures(self):
        # Updates the treasure text.
        # This shouldn't be a surprise, really.
        treasures = self.master.getHoardTreasures(self.only_gp_var.get())
        self.treasure_pane.updateText(treasures)
        
    def updateItems(self):
        # As above, but the items list.
        items = self.master.getHoardItems()
        self.item_pane.updateText(items)
    
    def generateHoard(self):
        # Generates a new hoard!
        # First, collect our data.
        name = None
        if not self.auto_name_var.get():
            name = self.name_entry.get()
        seed = None
        if not self.auto_seed_var.get():
            seed = self.seed_entry.get()
        cr = None
        if not self.auto_cr_var.get():
            cr = self.validateCR()
        # Now make the hoard!
        name, seed, cr = self.master.generateHoard(name, seed, cr)
        logging.debug("Generated hoard with name %s, seed %s, and cr %d" % (name, seed, cr))
        self.master.hoard_saved = False
        # ANd update our items.
        self.updateEntry(self.name_entry, name)
        self.updateEntry(self.seed_entry, seed)
        self.updateEntry(self.cr_entry, cr)
        self.updateTreasures()
        self.updateItems()
        self.edit_pane.updateDropDown()
        self.edit_pane.edit_frame.destroy()
        
    def updateEntry(self, entry, info):
        state = entry["state"]
        if state != "normal":
            entry.configure(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, str(info))
        entry.configure(state=state)
    
    def validateCR(self):
        # Validates the CR to make sure it's right.
        cr_str = self.cr_entry.get()
        try:
            cr_str = int(cr_str)
        except:
            try:
                cr_str = float(cr_str)
            except:
                pass
        if type(cr_str) is float:
            cr_str = round(crstr)
        if type(cr_str) is not int:
            # We've failed the test. No CR for us.
            return None
        max_cr = general.getInt("General", "max_cr")
        if cr_str > max_cr:
            # Too high.
            cr_str = max_cr
        if cr_str < 0:
            # Too low.
            cr_str = 0
        return cr_str

class textBoxPane(tk.Frame):
    # Text info!
    def __init__(self, main, label=None, fixed_width=False):
        tk.Frame.__init__(self, master=main)
        # Configure our components.
        self.grid_propagate(0)
        if label is not None:
            self.label = ttk.Label(self, text=label, font=main.large_font)
            self.label.grid(row=0, column=0, columnspan=2, sticky="NEW")
            self.label.configure(anchor="center")
        if fixed_width:
            self.text_box = tk.Text(self, wrap="word")
        else:
            self.text_box = tk.Text(self, wrap="none")
        self.v_scroll = tk.Scrollbar(self, orient="vertical", command=self.text_box.yview)
        self.h_scroll = tk.Scrollbar(self, orient="horizontal", command=self.text_box.xview)
        # Set up the text box.
        self.text_box.configure(yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set, state="disabled", font=main.standard_font)
        # And pack it all in.
        self.text_box.grid(row=1, column=0, sticky="NSEW")
        self.v_scroll.grid(row=1, column=1, sticky="NS")
        if not fixed_width:
            self.h_scroll.grid(row=2, column=0, sticky="EW")
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, minsize=20)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, minsize=20)
    
    def updateText(self, text=""):
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert("1.0", text)
        self.text_box.configure(state="disabled")

class editPane(tk.Frame):
    def __init__(self, main, label, text_frame, item_frame):
        tk.Frame.__init__(self, master=main)
        self.grid_propagate(0)
        self.edit_item = None
        self.original_item = None
        self.edited = False
        # Set up some basic info. We need to know what text box we'll use.
        self.text_frame = text_frame
        self.item_pane = item_frame # We need to update this occasionally
        # Now, top to bottom. First, the label.
        self.label = ttk.Label(self, text=label, font=main.large_font)
        self.label.configure(anchor="center")
        # For our drop-down menu
        self.var = tk.StringVar(self)
        self.var.set("Select an item to view")
        self.drop_down = tk.OptionMenu(self, self.var, "No items available")
        # We'll put other buttons in here.
        self.edit_frame = tk.Frame(self) # This'll be immediately destroyed, but oh well.
        # Set up the grid.
        self.grid_columnconfigure(0, weight=1)
        # Put our stuff in.
        self.label.grid(row=0, column=0, columnspan=5, sticky="EW")
        self.drop_down.grid(row=1, column=0, columnspan=5, padx=(0,10), sticky="EW")
        
    def updateDropDown(self):
        # Updates the dropdown menu with the list of items
        # First, get our list.
        dropdown = []
        for item in self.master.hoard.items:
            dropdown.append(item)
        # Reset the menu and the text frame
        self.text_frame.updateText()
        menu = self.drop_down["menu"]
        menu.delete(0, tk.END)
        # And add in things from our list.
        for item in dropdown:
            menu.add_command(label=item.getName(), 
                command = lambda value=item: self.inspectItem(value))
        self.var.set("Select an item to view")
        
    def inspectItem(self, item):
        # Gets some information and then shows the item.
        if item.source == "Generated Item" and item != self.edit_item:
            self.edited = False
            self.original_item = item
            self.edit_item = copy.deepcopy(item)
            self.getEditButtons(self.edit_item)
        elif item.source == "Generated Item":
            self.getEditButtons(item)
        else:
            self.edited = False
            self.edit_frame.destroy()
            self.edit_frame = tk.Frame(self)
        self.var.set(item.getName())
        item_desc = ""
        item_desc += item.source + "\n\n"
        if item.getInfo() is not None:
            item_desc += item.getInfo() + "\n\n"
        if item.getDescription() is not None:
            item_desc += item.getDescription().replace("\n","\n\n")
        self.text_frame.updateText(item_desc)
    
    def getEditButtons(self, item):
        # Purge anything we may have previously
        self.edit_frame.destroy()
        # Make ourselves a frame to put everything in.
        self.edit_frame = tk.Frame(self)
        self.edit_frame.grid_columnconfigure(0, weight=1)
        self.edit_frame.grid(row=2, column=0, columnspan=5, sticky="NSEW")
        # Get the information first.
        bonus_frame = tk.Frame(self.edit_frame) # So we don't have to argue with layout
        bonus_frame.grid_columnconfigure(0, minsize=120)
        bonus_frame.grid_columnconfigure(1, minsize=115)
        bonus_frame.grid_columnconfigure(2, minsize=115)
        bonus_frame.grid_columnconfigure(3, minsize=100)
        rarity_var = tk.StringVar(self.edit_frame)
        rarities = ["Common","Uncommon","Rare","Very Rare","Legendary"]
        clean_rarity = item.rarity.capitalize()
        if clean_rarity == "Veryrare":
            clean_rarity = "Very Rare"
        rarity_dropdown = tk.OptionMenu(bonus_frame, rarity_var, clean_rarity)
        menu = rarity_dropdown["menu"]
        menu.delete(0, tk.END)
        for rarity in rarities:
            menu.add_command(label=rarity,
                command = lambda value=rarity : self.setRarity(item, value))
        rarity_var.set(clean_rarity)
        max_bonus_label = ttk.Label(bonus_frame, 
            text="Max Bonus: %d" % item.getMaxBonus(item.rarity), font=self.master.standard_font)
        current_bonus_label = ttk.Label(bonus_frame, text="Current Bonus: %d" % item.getBonus(),
            font=self.master.standard_font)
        avail_bonus_label = ttk.Label(bonus_frame, text="Available: %d" % item.getBudget(),
            font=self.master.standard_font)
        # Put them in the frame.
        rarity_dropdown.grid(row=0, column=0, sticky="EW")
        max_bonus_label.grid(row=0, column=1, sticky="W")
        current_bonus_label.grid(row=0, column=2)
        avail_bonus_label.grid(row=0, column=3, sticky="E", padx=(0, 10))
        # Gets a button for each of the following: Base Item, Material, and any prefixes or suffixes
        item_label = ttk.Label(self.edit_frame, text="Base Item: %s" % item.getItemName(), 
            font = self.master.small_font)
        item_cost_label = ttk.Label(self.edit_frame, text="Bonus: %d" % item.item_bonus, 
            font = self.master.small_font)
        item_reroll_button = tk.Button(self.edit_frame, text="Randomize", relief=tk.RAISED,
            font=self.master.small_font, command = lambda : self.rerollRandomItem(item))
        item_replace_button = tk.Button(self.edit_frame, text="Replace", relief=tk.RAISED,
            font=self.master.small_font,  command = lambda : self.replaceItem(item))
        material_label = ttk.Label(self.edit_frame, text="Material: %s" % str(item.material.name),
            font = self.master.small_font)
        material_cost_label = ttk.Label(self.edit_frame, text="Bonus: %d" % item.material.bonus,
            font = self.master.small_font)
        material_reroll_button = tk.Button(self.edit_frame, text="Randomize", relief=tk.RAISED, 
            font=self.master.small_font, 
            command = lambda : self.rerollRandomEffect(item, item.material))
        material_replace_button = tk.Button(self.edit_frame, text="Replace", relief=tk.RAISED,
            font=self.master.small_font, command = lambda : self.replaceEffect(item, item.material))
        material_remove_button = tk.Button(self.edit_frame, text="Remove", relief=tk.RAISED,
            font=self.master.small_font, command = lambda : self.removeEffect(item, item.material))
        curse_label = ttk.Label(self.edit_frame, text="Curse: %s" % item.curse.name,
            font = self.master.small_font)
        curse_cost_label = ttk.Label(self.edit_frame, text="Bonus: %d" % item.curse.bonus,
            font = self.master.small_font)
        curse_reroll_button = tk.Button(self.edit_frame, text="Randomize", relief=tk.RAISED,
            font=self.master.small_font,
            command = lambda : self.rerollRandomEffect(item, item.curse))
        curse_replace_button = tk.Button(self.edit_frame, text="Replace", relief=tk.RAISED,
            font=self.master.small_font, command = lambda : self.replaceEffect(item, item.curse))
        curse_remove_button = tk.Button(self.edit_frame, text="Remove", relief=tk.RAISED,
            font=self.master.small_font, command = lambda : self.removeEffect(item, item.curse))
        # See if we need to have buttons available.
        if len(item.spells) == 0 and len(item.random_lists) == 0:
            # No random things to randomize.
            item_reroll_button.configure(state="disabled")
        if len(item.material.spells) == 0 and len(item.material.random_lists) == 0:
            material_reroll_button.configure(state="disabled")
        if len(item.material_type) == 0:
            # We'll never get a material type, so turn off that button.
            material_replace_button.configure(state="disabled")
        if item.material is None:
            # Can't remove something that's not there!
            material_remove_button.configure(state="disabled")
        elif item.material.id is None:
            material_remove_button.configure(state="disabled")
        if item.curse is None:
            curse_remove_button.configure(state="disabled")
        elif item.curse.id is None:
            curse_remove_button.configure(state="disabled")
        if len(item.curse.spells) == 0 and len(item.curse.random_lists) == 0:
            curse_reroll_button.configure(state="disabled")
        # Put them in the box.
        bonus_frame.grid(row=0, column=0, columnspan=5, sticky="EW", pady=4)
        item_label.grid(row=2, column=0, columnspan=5, sticky="W")
        item_cost_label.grid(row=2, column=0, sticky="E")
        item_reroll_button.grid(row=2, column=2)
        item_replace_button.grid(row=2, column=3)
        material_label.grid(row=3, column=0, columnspan=5, sticky="W")
        material_cost_label.grid(row=3, column=0, sticky="E")
        material_reroll_button.grid(row=3, column=2)
        material_replace_button.grid(row=3, column=3)
        material_remove_button.grid(row=3, column=4, padx=(0, 10))
        curse_label.grid(row=4, column=0, columnspan=5, sticky="W")
        curse_cost_label.grid(row=4, column=0, sticky="E")
        curse_reroll_button.grid(row=4, column=2)
        curse_replace_button.grid(row=4, column=3)
        curse_remove_button.grid(row=4, column=4, padx=(0, 10))
        # Now. For the effects.
        # We'll need to know what row we're on.
        row = 5
        for effect in item.prefixes + item.suffixes:
            # Get the effect info
            if effect in item.prefixes:
                effect_label = ttk.Label(self.edit_frame, text="Prefix: %s" % effect.prefix,
                    font=self.master.small_font)
            elif effect in item.suffixes:
                effect_label = ttk.Label(self.edit_frame, text="Suffix: %s" % effect.suffix,
                    font=self.master.small_font)
            effect_cost_label = ttk.Label(self.edit_frame, text="Bonus: %d" % effect.bonus,
                font=self.master.small_font)
            effect_reroll_button = tk.Button(self.edit_frame, text="Randomize", relief=tk.RAISED,
                font=self.master.small_font,
                command = lambda value=effect : self.rerollRandomEffect(item, value))
            effect_replace_button = tk.Button(self.edit_frame, text="Replace", relief=tk.RAISED,
                font=self.master.small_font,
                command = lambda value=effect : self.replaceEffect(item, value))
            effect_remove_button = tk.Button(self.edit_frame, text="Remove", relief=tk.RAISED,
                font=self.master.small_font,
                command = lambda value=effect : self.removeEffect(item, value))
            # Do we have to turn any of them off?
            if len(effect.spells) == 0 and len(effect.random_lists) == 0:
                # No randomizations.
                effect_reroll_button.configure(state="disabled")
            # We'll always be able to remove or replace the effect, so don't worry about those.
            # Put them on the grid.
            effect_label.grid(row=row, column=0, columnspan=5, sticky="W")
            effect_cost_label.grid(row=row, column=0, sticky="E")
            effect_reroll_button.grid(row=row, column=2)
            effect_replace_button.grid(row=row, column=3)
            effect_remove_button.grid(row=row, column=4, padx=(0, 10))
            # Increase the row for the next effect
            row += 1
        # Now for the "add effect" box
        add_frame = tk.Frame(self.edit_frame)
        add_frame.grid_columnconfigure(0, minsize=45)
        add_frame.grid_columnconfigure(1, minsize=90)
        add_frame.grid_columnconfigure(2, minsize=90)
        add_frame.grid_columnconfigure(3, minsize=90)
        add_frame.grid_columnconfigure(4, minsize=90)
        add_frame.grid_columnconfigure(5, minsize=45)
        prefix_text = "Prefixes: %d" % len(item.prefixes)
        if item.max_prefix is not None:
            prefix_text += "/%s" % str(item.max_prefix)
        suffix_text = "Suffixes: %d" % len(item.suffixes)
        if item.max_prefix is not None:
            suffix_text += "/%s" % str(item.max_suffix)
        effect_text = "Effects: %d" % len(item.suffixes + item.prefixes)
        max_effects = item.getMaxEffects()
        if max_effects is not None:
            effect_text += "/%d" % max_effects
        prefix_label = ttk.Label(add_frame, text=prefix_text, font=self.master.small_font)
        suffix_label = ttk.Label(add_frame, text=suffix_text, font=self.master.small_font)
        effect_label = ttk.Label(add_frame, text=effect_text, font=self.master.small_font)
        enh_label = ttk.Label(add_frame, text="Enhancement", font=self.master.small_font)
        add_prefix_button = tk.Button(add_frame, text="Add\nPrefix", relief=tk.RAISED,
            font=self.master.standard_font, command = lambda : self.addPrefix(item))
        add_suffix_button = tk.Button(add_frame, text="Add\nSuffix", relief=tk.RAISED,
            font=self.master.standard_font, command = lambda : self.addSuffix(item))
        add_autofill_button = tk.Button(add_frame, text="Autofill\nEffects", relief=tk.RAISED,
            font=self.master.standard_font, command = lambda : self.autofillItem(item))
        enh_increase_button = tk.Button(add_frame, text="Increase", relief=tk.RAISED,
            font=self.master.standard_font, command = lambda : self.adjustEnh(item, 1))
        enh_decrease_button = tk.Button(add_frame, text="Decrease", relief=tk.RAISED,
            font=self.master.standard_font, command = lambda : self.adjustEnh(item, -1))
        # Do any of them need to be disabled?
        if item.enhancement == 0:
            enh_decrease_button.configure(state="disabled")
        if item.enhancement == item.getMaxEnhancement():
            enh_increase_button.configure(state="disabled")
        if not item.can_have_enh:
            enh_increase_button.configure(state="disabled")
        if item.getBudget() < 0:
            # Nope, too many things!
            add_prefix_button.configure(state="disabled")
            add_suffix_button.configure(state="disabled")
        if item.getBudget() <= 0:
            # Autofill shouldn't be used here.
            add_autofill_button.configure(state="disabled")
            enh_increase_button.configure(state="disabled")
        if item.max_effects is not None:
            if len(item.prefixes) + len(item.suffixes) >= max_effects:
                # Too many effects. Sorry, I don't make the rules. (No, wait, I totally do here)
                add_prefix_button.configure(state="disabled")
                add_suffix_button.configure(state="disabled")
                add_autofill_button.configure(state="disabled")
        # Have we brought too many prefixes to the party?
        if item.max_prefix is not None:
            if len(item.prefixes) >= item.max_prefix:
                add_prefix_button.configure(state="disabled")
        # What about suffixes?
        if item.max_suffix is not None:
            if len(item.suffixes) >= item.max_suffix:
                add_suffix_button.configure(state="disabled")
        enh_label.grid(row=0, column=1)
        prefix_label.grid(row=0, column=2)
        suffix_label.grid(row=0, column=3)
        effect_label.grid(row=0, column=4)
        enh_increase_button.grid(row=1, column=1, sticky="NSEW")
        enh_decrease_button.grid(row=2, column=1, sticky="NSEW")
        add_prefix_button.grid(row=1, column=2, rowspan=2, sticky="NSEW")
        add_suffix_button.grid(row=1, column=3, rowspan=2, sticky="NSEW")
        add_autofill_button.grid(row=1, column=4, rowspan=2, sticky="NSEW")
        add_frame.grid(row=row, column=0, columnspan=5, sticky="EW", pady=(10,0))
        row += 1
        
        # Our save and reset buttons for the item
        # Put them in their own frame so we're not stuck with the layout of the above buttons
        save_frame = tk.Frame(self.edit_frame)
        save_frame.grid_columnconfigure(0, minsize=90)
        save_frame.grid_columnconfigure(1, minsize=90)
        save_frame.grid_columnconfigure(2, minsize=90)
        save_frame.grid_columnconfigure(3, minsize=90)
        save_frame.grid_columnconfigure(4, minsize=90)
        save_button = tk.Button(save_frame, text="Save Item", relief=tk.RAISED,
            font=self.master.standard_font, command = lambda value=item : self.saveItem(value))
        reset_button = tk.Button(save_frame, text="Reset Item", relief=tk.RAISED,
            font=self.master.standard_font, command = self.resetItem)
        # If nothing's changed, turn them off.
        if not self.edited:
            reset_button.configure(state="disabled")
            save_button.configure(state="disabled")
        if item.getBudget() < 0:
            save_button.configure(state="disabled")
        save_button.grid(row=0, column=1, sticky="EW")
        reset_button.grid(row=0, column=3, sticky="EW")
        save_frame.grid(row=row, column=0, columnspan=5, sticky="EW")
    
    def updateEdit(self, item):
        # Updates our displays for the new item.
        self.edit_item = item
        self.getEditButtons(item)
        self.inspectItem(item)
    
    def saveItem(self, item):
        # Saves the item to the hoard. The updates our displays.
        self.edit_item = item
        index = -1
        for r in range(0, len(self.master.hoard.items)):
            if self.master.hoard.items[r] == self.original_item:
                self.master.hoard.items[r] = self.edit_item
        self.original_item = self.edit_item
        self.edit_item = copy.deepcopy(self.original_item)
        items = self.master.getHoardItems()
        self.updateDropDown()
        self.var.set(self.edit_item.getName())
        self.inspectItem(self.edit_item)
        self.item_pane.updateText(items)
        self.master.hoard_edited = True
        self.edited = False
    
    def addSuffix(self, item):
        effect = item.getAffix("suffix")
        if effect.id is not None:
            item.suffixes.append(effect)
        self.edited = True
        self.updateEdit(item)
    
    def addPrefix(self, item):
        effect = item.getAffix("prefix")
        if effect.id is not None:
            item.prefixes.append(effect)
        self.edited = True
        self.updateEdit(item)
        
    def autofillItem(self, item):
        item.generateEffects()
        self.edited = True
        self.updateEdit(item)
    
    def resetItem(self):
        # Resets the edited item back to its original state.
        self.edit_item = copy.deepcopy(self.original_item)
        self.edited = False
        self.updateEdit(self.edit_item)
        
    def setRarity(self, item, rarity):
        rarity = rarity.lower().replace(" ","")
        item.rarity = rarity
        self.edited = True
        self.updateEdit(item)
    
    def adjustEnh(self, item, adjust):
        item.enhancement = item.enhancement + adjust
        self.edited = True
        self.updateEdit(item)
    
    def replaceEffect(self, item, effect):
        # Replaces the effect on the item with another one.
        item.replaceAffix(effect)
        self.edited = True
        self.updateEdit(item)
    
    def removeEffect(self, item, effect):
        # Removes the effect from the item
        if effect.category == "material":
            # We always have to have a material, so generate an empty one.
            item.material = item.getEmptyMaterial()
        elif effect.category == "curse":
            # As with materials, generate an empty curse.
            item.curse = item.getEmptyCurse()
        elif effect.category == "effect":
            # These we don't have to replace.
            item.removeEffect(effect)
        self.edited = True
        self.updateEdit(item)
        
    def rerollRandomEffect(self, item, effect):
        # Re-rolls any random choices on the effect.
        effect.rerollRandom(item.id)
        self.edited = True
        self.updateEdit(item)
    
    def replaceItem(self, item):
        # Replaces the base item of the... item.
        item.replaceItem()
        self.edited = True
        self.updateEdit(item)
    
    def rerollRandomItem(self, item):
        # Re-rolls all random choices and spells on the item.
        item.rerollRandom()
        self.edited = True
        self.updateEdit(item)
        pass


class emptyPane(tk.Frame):
    # An empty frame. How exciting.
    def __init__(self, main):
        tk.Frame.__init__(self, master=main)

# Set up our everything.
# Main window and title first.
main_window = Window()
title = titlePane(main_window)
# Center Column. Items and Treasure.
items = textBoxPane(main_window, "Items")
treasures = textBoxPane(main_window, "Treasures")
# Right column. Item Editor and Inspector.
item_inspector = textBoxPane(main_window, fixed_width=True)
item_edit = editPane(main_window, label="Item Editor", text_frame=item_inspector, item_frame=items)
# Left Column. Input ties into the others, so must come last.
input = inputPane(main_window, items, treasures, item_edit)
status = emptyPane(main_window)
# Generate a fresh hoard!
input.generateHoard()

# Now we shove things in their respective boxes.
title.grid(row=0, column=0, columnspan=3, sticky="EW")
input.grid(row=1, column=0, sticky="NSEW")
status.grid(row=2, column=0, sticky="NSEW")
items.grid(row=1, column=1, sticky="NSEW")
treasures.grid(row=2, column=1, sticky="NSEW")
item_edit.grid(row=1, column=2, sticky="NSEW")
item_inspector.grid(row=2, column=2, sticky="NSEW")

main_window.mainloop()













