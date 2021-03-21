# Hoard name generator.
# How fancy.

import random
#import configparser
import logging
#import os
import configs

general = configs.CFG(configs.GENERAL)
name_data = configs.CFG(configs.HOARD_NAMES)

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
        id_list = []
        for id in name_data.config:
            if id in chosen:
                # We can't choose the same thing again.
                continue
            data = name_data.get(id, option)
            if data is None:
                # Doesn't have our required option.
                continue
            min_lvl = name_data.getInt(id, "min_cr")
            if min_lvl is not None:
                if self.cr < min_lvl:
                    # Our level is too low for this name.
                    continue
            max_lvl = name_data.getInt(id, "max_cr")
            if max_lvl is not None:
                if self.cr > max_lvl:
                    # We're too high for this.
                    continue
            # We've made it past our filters.
            id_list.append(id)
        return random.choice(id_list)
    
    def getName(self):
        # Grabs the prefix, name, and suffix values of our, well. Those.
        name = []
        name.append(name_data.get(self.prefix, "prefix"))
        name.append(name_data.get(self.id, "name"))
        name.append(name_data.get(self.suffix, "suffix"))
        name = " ".join(name)
        return name