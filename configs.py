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
startup_cfg = configparser.ConfigParser()
startup_cfg.read("./config/startup.cfg") 

local_mode = startup_cfg["General"].getboolean("local_mode")
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
log_level = startup_cfg["General"].getint("logging_level")
logging.basicConfig(filename="%s/output %s.log" % (log_dir, start_time), level=log_level)
logging.info("Beginning log file. Start time: %s" % start_time)
# Trim any excess logs.
log_list = []
for log in os.listdir(log_dir):
    if log.endswith(".log"):
        log_list.append(log)
if len(log_list) > startup_cfg["General"].getint("logs_to_keep"):
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
            shutil.copytree("./data/%s" % folder, data_dir + "\\%s" % folder)
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
    logging.info("Using Local Folders")
    cfg_folder = "./default_config"
    data_folder = "./data"
else:
    # For system folders.
    logging.info("Using System Folders")
    data_folder = dirs.user_data_dir
    cfg_folder = data_folder + "\\config"

class CFG:
    # A class to open, read, manage, and save our configs.
    def __init__(self, path, filename=None):
        self.path = path
        if not os.path.isdir(self.path):
            logging.critical("Critical Error: Folder not found: %s" % self.path)
            raise SystemExit("Critical Error: Folder not found: %s" % self.path)
        if type(filename) is not str:
            self.filename = None
        else:
            self.filename = filename
        self.config = self.getConfig()
        
    def getConfig(self):
        # Opens either a folder of configs (Which can't be saved)
        # Or a single config file (Which can be saved)
        config = configparser.ConfigParser()
        if self.filename is None:
            # Read all the files in the given path.
            flist = os.listdir(self.path)
            filesloaded = 0
            for file in flist:
                if file.endswith(".cfg"):
                    config.read(self.path + "\\%s" % file, encoding="cp1252")
                    logging.debug("Loaded %s" % file)
                    filesloaded += 1
            if filesloaded < 1:
                logging.critical("Critical Error: No information files in %s" % self.path)
                raise SystemExit("Critical Error: No information files in %s" % self.path)
        else:
            load = config.read(self.path + "\\" + self.filename, encoding="cp1252")
            if load == []:
                logging.critical("Critical Error: File %s not found." % self.filename)
                raise SystemExit("Critical Error: File %s not found." % self.filename)
            logging.debug("Loaded %s" % self.filename)
        return config
        
    def save(self):
        # If we're a single file, save that file. Otherwise, just fail.
        if self.filename is None:
            return False
        with open(self.path + "\\" + self.filename, "w") as cfg_file:
            self.config.write(cfg_file)
        return True
    
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
        
# Now load our configs. Config folder first.
GENERAL = CFG(cfg_folder, "general.cfg")
ITEM_GEN_CFG = CFG(cfg_folder, "item_generator.cfg")
HOARD_GENERATORS = CFG(cfg_folder, "hoard_generators.cfg")
STATIC_GEN_CFG = CFG(cfg_folder, "static_item_cfg.cfg")

# And our regular information.
ITEM_DATA = CFG(data_folder + "\\" + GENERAL.get("Folders", "item_folder"))
HOARD_NAMES = CFG(data_folder + "\\" + GENERAL.get("Folders", "hoard_name_folder"))
TREASURE_DATA = CFG(data_folder + "\\" + GENERAL.get("Folders", "treasure_folder"))
STATIC_DATA = CFG(data_folder + "\\" + GENERAL.get("Folders", "static_item_folder"))
SPELL_DATA = CFG(data_folder + "\\" + GENERAL.get("Folders", "spell_folder"))