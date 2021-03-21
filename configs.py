# Ok, so. Each of our various generators loaded their own configurations.
# Which... Honestly, works. But there was some duplication.
# A single file is likely to be better.
# It also offloads a lot of the initial startup stuff that each generator did.

import configparser
import logging
import os
# import ui_toolbox as ui

VERSION = "2021.3.21 (Alpha)"

# Start with our actual configurations.
# We are going to need:
# General Configuration
# Generator Configuration
# Itemgen configuration
# Static Item Configuration

# First, see if our files exist.
for cfgfile in ["general", "item_generator", "hoard_generators", "static_items"]:
    if not os.path.isfile("./config/%s.cfg" % cfgfile):
        logging.critical("Critical Error: Configuration file %s.cfg not found. The program cannot continue." % cfgfile)
        # ui.errorbox() # TODO: Implement the UI toolbox.
        exit()

# OK, they do. So load them.

# Start with general.
GENERAL = configparser.ConfigParser()
GENERAL.read("./config/general.cfg", encoding="cp1252")
logging.debug("Loaded general configuration file.")

# Item generator
ITEM_GEN_CFG = configparser.ConfigParser()
ITEM_GEN_CFG.read("./config/item_generator.cfg", encoding="cp1252")
logging.debug("Loaded Item Generator configuration file.")

# Hoard generator list
HOARD_GENERATORS = configparser.ConfigParser()
HOARD_GENERATORS.read("./config/hoard_generators.cfg", encoding="cp1252")
logging.debug("Loaded Hoard Generator configuration file.")

# Static item config
STATIC_GEN_CFG = configparser.ConfigParser()
STATIC_GEN_CFG.read("./config/static_items.cfg", encoding="cp1252")
logging.debug("Loaded Static Item selector configuration file.")

#Spell data config.

# OK, now we need our various datas.
# We'll need hoard names, item generator information, static items, & treasures

# First, we'll need a repeatable way to load them. We'll need a list of files.
def readFiles(folder):
    # Reads all the data files in the selected folder into the selected config.
    # First, check the folder.
    if not os.path.isdir("./%s" % folder):
        logging.critical("Critical Error: The %s folder was not found." % folder)
        # ui.errorbox()
        exit()
    flist = os.listdir("./%s" % folder)
    config = configparser.ConfigParser()
    filesloaded = 0
    for file in flist:
        # Filter out the non-configs.
        if file.endswith(".cfg"):
            config.read("./%s/%s" % (folder, file), encoding="cp1252")
            filesloaded += 1
    # Now we should have our files loaded.
    if filesloaded < 1:
        # But there weren't any to load.
        logging.critical("Critical Error: There were no information files in the %s folder" % folder)
        # ui.errorbox()
        exit()
    return config

# Now load our information.
# Start with item generator
folder = GENERAL["Folders"]["itemfolder"]
ITEM_DATA = readFiles(folder)
logging.debug("Loaded Item Generator information files.")
# And hoard names.
folder = GENERAL["Folders"]["hoardnamefolder"]
HOARD_NAMES = readFiles(folder)
logging.debug("Loaded Hoard Name Generator information files.")
# Treasures
folder = GENERAL["Folders"]["treasurefolder"]
TREASURE_DATA = readFiles(folder)
logging.debug("Loaded Treasure informationiles")
# Static Items
folder = GENERAL["Folders"]["staticfolder"]
STATIC_DATA = readFiles(folder)
logging.debug("Loaded Static Item information files")
# Spell Data
folder = GENERAL["Folders"]["spellfolder"]
SPELL_DATA = readFiles(folder)
logging.debug("Loaded Spell data files")

# Now for our information gathering.

class CFG:
    # A class for easy retrieval of data.
    def __init__(self, config):
        self.config = config
    
    def getList(self, section, option):
        # Grabs, cleans, and returns an option that's a semicolon-separated list.
        raw_data = self.config[section].get(option)
        if raw_data is None:
            return []
        else:
            raw_data = raw_data.split(";")
            data = []
            for raw in raw_data:
                data.append(raw.strip())
            return data
    
    def getInt(self, section, option):
        # Simply returns the requested integer.
        data = self.config[section].getint(option)
        return data
    
    def getBool(self, section, option):
        data = self.config[section].getboolean(option)
        return data
    
    def getFloat(self, section, option):
        data = self.config[section].getfloat(option)
        return data
        
    def get(self, section, option):
        data = self.config[section].get(option)
        return data
    
    def set(self, section, option, value):
        # Sets data.
        self.config.set(section, option, value)
        return
        
    def getOptionList(self, option, optionvalue):
        # Grabs a list of info that has the selected option and said option
        # is the given value.
        if type(optionvalue) is not str or type(option) is not str:
            raise TypeError("All inputs must be strings!")
        data = []
        for item in self.config:
            value = self.config[item].get(option)
            if value == optionvalue:
                data.append(item)
        return data