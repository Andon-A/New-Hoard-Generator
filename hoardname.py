# Hoard name generator.
# How fancy.

import random
import configparser
import logging
import os

cfg = configparser.ConfigParser()
cfg.read("./config/general.cfg", encoding="cp1252")
# print("Item Generator config loaded")
logging.info("Hoard Name Generator config loaded.")
# Load our item files
dfolder = cfg["Folders"]["hoardfolder"]
data = configparser.ConfigParser()
ilist = os.listdir("./%s" % dfolder)
for i in ilist:
    if i[-4:] == ".cfg":
        # A config file. Load it.
        data.read("./%s/%s" % (dfolder, i))
        # print("Item file %s loaded." % i)
        logging.info("Name file ./%s/%s loaded." % (dfolder, i))
print("Hoard Name Generator files loaded.") 

class HoardName:
    def __init__(self, cr, name=None):
        self.cr = cr
        if type(name) != str:
            self.id = self.getID("name")
            self.prefix = self.getID("prefix", [self.id])
            self.suffix = self.getID("suffix", [self.id, self.prefix])
            self.name = self.getName()
        else:
            self.name = name
        
    def remakeName(self, allowredo=False):
        # Re-creates our name. We can allow re-choosing the same options
        # Or go for completely new.
        avoid = []
        if not allowredo:
            avoid.append(self.id)
            avoid.append(self.prefix)
            avoid.append(self.suffix)
        self.id = self.getID("name", avoid)
        avoid.append(self.id)
        self.prefix = self.getID("prefix", avoid)
        avoid.append(self.prefix)
        self.suffix = self.getID("suffix", avoid)
        self.name = self.getName()
        return self.name
    
    def getID(self, option, chosen=[]):
        # Grabs a base name, prefix, or suffix for our hoard.
        if option not in ["prefix","suffix","name"]:
            return ""
        ids = []
        for id in data:
            if data.has_option(id, option):
                # Well, this thing has a name.
                # See if it's of sufficient level.
                minlvl = data[id].getint("mincr")
                if minlvl is None:
                    minlvl = 0
                if self.cr >= minlvl and id not in chosen:
                    ids.append(id)
        return random.choice(ids)
    
    def getName(self):
        # Grabs the prefix, name, and suffix values of our, well. Those.
        name = []
        name.append(data[self.prefix]["prefix"])
        name.append(data[self.id]["name"])
        name.append(data[self.suffix]["suffix"])
        name = " ".join(name)
        return name