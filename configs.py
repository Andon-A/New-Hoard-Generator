# A file for handling folders and such.
# It offloads the logging setup from the main UI file, which should simplify things.
# If it's configured for local running, it'll use local files (What a surprise), otherwise it uses
# the appdirs module to store things where they should go.

import os
import shutil
import appdirs
import logging
import time
import configparser

VERSION = "2021.3.28 (Alpha)"

# Our system dirs
dirs = appdirs.AppDirs(appauthor="andon", appname="nhg", version="alpha")

# First, we want to see if we're running in local mode. To do *that*, we need to open our local
# general config.
quick_cfg = configparser.ConfigParser()
quick_cfg.read("./default_config/general.cfg") 

local_mode = quick_cfg["General"].getboolean("local_mode")
if local_mode is None:
    local_mode = False # Default to system folder mode.

# Set up our logging, first.
log_dir = ""
if local_mode:
    log_dir = os.path.abspath("./logs")
else:
    log_dir = dirs.user_log_dir
    
# Make sure the folder exists.
if not os.path.isdir(log_dir):
    os.makedirs(log_dir, exist_ok=True)

# And begin logging.
start_time = start_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
log_level = quick_cfg["General"].getint("logging_level")
logging.basicConfig(filename="%s/output %s.log" % (log_dir, start_time), level=log_level)
logging.info("Beginning log file. Start time: %s" % start_time)
# Trim any excess logs.
log_list = []
for log in os.listdir(log_dir):
    if log.endswith(".log"):
        log_list.append(log)
if len(log_list) > quick_cfg["General"].getint("logs_to_keep"):
    log_list.sort(reverse=True) # They're named by time, so oldest first.
    while len(log_list) > quick_cfg["General"].getint("logs_to_keep"):
        log = log_list.pop()
        os.remove("%s/%s" % (log_dir, log))

# OK, now that we've started our logging. Let's set up those folders.
    
def makeSysPaths():
    # Makes our system files if they don't exist.
    # If they are created, copy our default files into them.
    logging.info("Checking system paths.")
    data_dir = dirs.user_data_dir
    if not os.path.isdir(data_dir):
        logging.info("Creating data directory.")
        os.makedirs(data_dir, exist_ok=True)
    for folder in quick_cfg["Folders"]:
        folder = quick_cfg["Folders"].get(folder)
        if not os.path.isdir(data_dir + "\\%s" % folder):
            logging.info("Creating data folder %s" % folder)
            shutil.copytree("./%s" % folder, data_dir + "\\%s" % folder)
    # Why this instead of user_config_dir?
    # on Windows, it just dumps it all into the user data directory.
    # So rather than having to code only for windows, this keeps it system-universal,
    # At a cost of not *quite* conforming to what's usual for systems.
    if not os.path.isdir(data_dir + "\\config"):
        logging.info("Creating config folder")
        shutil.copytree("./default_config", data_dir + "\\config")

if not local_mode:
    makeSysPaths()

# We don't need to have the local config loaded any further.
del(quick_cfg)

if local_mode:
    # Set ourselves up for local working.
    print("Local")
    cfg_folder = "./default_config"
    data_folder = "./data"
else:
    # For system folders.
    print("System")
    data_folder = dirs.user_data_dir
    cfg_folder = data_folder + "\\config"

# Start loading some configs. Check to see if they exist.


for cfg_file in ["general", "item_generator", "hoard_generators", "static_items"]:
    if not os.path.isfile(cfg_folder + "\\%s.cfg" % cfg_file):
        logging.critical("Critical Error: Configuration file %s.cfg not found. The program cannot continue." % cfg_file)
        raise SystemExit("Critical Error: Configuration file %s.cfg not found. The program cannot continue." % cfg_file)
# By now, they exist. Cool.

# Start with general config.
GENERAL = configparser.ConfigParser()
GENERAL.read(cfg_folder + "\\general.cfg", encoding="cp1252")
logging.debug("Loaded general.cfg")

# Item generator
ITEM_GEN_CFG = configparser.ConfigParser()
ITEM_GEN_CFG.read(cfg_folder + "\\item_generator.cfg", encoding="cp1252")
logging.debug("Loaded item_generator.cfg")

# Hoard generator list
HOARD_GENERATORS = configparser.ConfigParser()
HOARD_GENERATORS.read(cfg_folder + "\\hoard_generators.cfg", encoding="cp1252")
logging.debug("Loaded hoard_generators.cfg")

# Static item config
STATIC_GEN_CFG = configparser.ConfigParser()
STATIC_GEN_CFG.read(cfg_folder + "\\static_items.cfg", encoding="cp1252")
logging.debug("Loaded static_items.cfg")

# Now we need our various data
# But first, a repeatable way to load them.
def readFiles(folder):
    # Reads all the data files in the selected folder into the selected config.
    # First, check the folder.
    folder = data_folder + "\\%s" % folder
    if not os.path.isdir(folder):
        logging.critical("Critical Error: Folder not found: %s" % folder)
        raise SystemExit("Critical Error: Folder not found: %s" % folder)
    flist = os.listdir(folder)
    config = configparser.ConfigParser()
    filesloaded = 0
    for file in flist:
        # Filter out the non-configs.
        if file.endswith(".cfg"):
            config.read("%s\\%s" % (folder, file), encoding="cp1252")
            filesloaded += 1
    # Now we should have our files loaded.
    if filesloaded < 1:
        # But there weren't any to load.
        logging.critical("Critical Error: There were no information files in %s" % folder)
        raise SystemExit("Critical Error: There were no information files in %s" % folder)
    return config
    
# Now load it up.
# Start with item generator
folder = GENERAL["Folders"]["item_folder"]
ITEM_DATA = readFiles(folder)
logging.debug("Loaded Item Generator information files.")
# And hoard names.
folder = GENERAL["Folders"]["hoard_name_folder"]
HOARD_NAMES = readFiles(folder)
logging.debug("Loaded Hoard Name Generator information files.")
# Treasures
folder = GENERAL["Folders"]["treasure_folder"]
TREASURE_DATA = readFiles(folder)
logging.debug("Loaded Treasure informationiles")
# Static Items
folder = GENERAL["Folders"]["static_folder"]
STATIC_DATA = readFiles(folder)
logging.debug("Loaded Static Item information files")
# Spell Data
folder = GENERAL["Folders"]["spell_folder"]
SPELL_DATA = readFiles(folder)
logging.debug("Loaded Spell data files")

# Now a class to have our information used more easily.
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