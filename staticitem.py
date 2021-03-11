# Static Magic Item Chooser
# This chooses magic items from a list. It pulls their description, their
# rarity, and the like.

import configparser
import random
import logging
import os

# Load our items.
logging.info("Importing static items")
# Get the folder configuration configuration first.
cfg = configparser.ConfigParser()
cfg.read("./config/general.cfg", encoding="cp1252")
staticdir = cfg["Folders"]["staticfolder"]
# Now our own. Reset it, don't want any conflicting data.
cfg = configparser.ConfigParser()
cfg.read("./config/staticconfig.cfg", encoding="cp1252")
# Now the information from static items.
data = configparser.ConfigParser()
dlist = os.listdir("./%s" % staticdir)
for d in dlist:
    if d[-4:] == ".cfg":
        data.read("./%s/%s" % (staticdir, d), encoding="cp1252")
        logging.info("Item file ./%s/%s loaded." % (staticdir, d))
print("Static item files loaded.")

def getCategoryList(category, rarity=None):
    # Grabs a list of items of the specific category.
    ilist = []
    for i in data:
        # Make sure our item has the option before trying to grab it.
        if data.has_option(i, "category"):
            if data[i]["category"] == category:
                # It does. Check if its rarity matches ours.
                if rarity is None:
                    # No rarity filter.
                    ilist.append(i)
                elif data.has_option(i, "rarity"):
                    # We have a rarity, good.
                    if data[i]["rarity"] == rarity:
                        # And it matches.
                        ilist.append(i)
    return ilist
    
class Item:
    def __init__(self, rarity=None, category=None):
        self.id = self.getItem(rarity, category)
        self.name = None
        self.category = None
        self.rarity = None
        self.description = None
        self.info = None
        self.getInfo()
        logging.info("Static item %s selected" % self.name)
        self.source = "Premade Item"
        
    def getInfo(self):
        # Assigns the name, category, rarity, and description of the item's ID.
        if data.has_option(self.id, "name"):
            self.name = data[self.id]["name"]
        if data.has_option(self.id, "category"):
            self.category = data[self.id]["category"]
        if data.has_option(self.id, "rarity"):
            self.rarity = data[self.id]["rarity"]
        if data.has_option(self.id, "description"):
            self.description = data[self.id]["description"].replace("\\n","\n")
        # Information, such as "Armor (medium)" or whatever.
        if data.has_option(self.id, "info"):
            self.info = data[self.id]["info"]
            
    def getCategory(self, rarity):
        # Determines the item's category on the weighted list.
        clist = []
        wlist = []
        for c in cfg[rarity]:
            # Each item in the rarities represents a weight.
            w = cfg[rarity].getint(c)
            if w > 0:
                # Make sure we have items to choose from in this combo.
                if len(getCategoryList(c, rarity)) > 0:
                    clist.append(c)
                    wlist.append(w)
        return random.choices(clist, wlist)[0]
    
    def getRarity(self):
        # Pulls the rarity weights from the config file.
        rlist = ["common","uncommon","rare","veryrare","legendary"]
        wlist = []
        wlist.append(cfg["Rarity"].getint("commonweight"))
        wlist.append(cfg["Rarity"].getint("uncommonweight"))
        wlist.append(cfg["Rarity"].getint("rareweight"))
        wlist.append(cfg["Rarity"].getint("veryrareweight"))
        wlist.append(cfg["Rarity"].getint("legendaryweight"))
        return random.choices(rlist,wlist)[0]
    
    def getItem(self, rarity, category):
        # Check if we have been supplied with rarity and category.
        if rarity is None:
            rarity = self.getRarity()
        else:
            rarity = rarity.lower()
        if category is None:
            category = self.getCategory(rarity)
        else:
            category = category.lower()
        # OK, now get our items.
        ilist = getCategoryList(category, rarity)
        # And, simply, choose one. No need for filters here.
        return random.choice(ilist)
    