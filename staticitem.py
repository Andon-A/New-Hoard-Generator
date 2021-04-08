# Static Magic Item Chooser
# This chooses magic items from a list. It pulls their description, their
# rarity, and the like.

import random
import logging
import configs
import spells

general = configs.GENERAL
item_data = configs.STATIC_DATA
cfg = configs.STATIC_GEN_CFG
    
class Item:
    def __init__(self, rarity=None, category=None):
        self.id = self.getItem(rarity, category)
        self.name = None
        self.name_set = False
        self.category = None
        self.rarity = None
        self.description = None
        self.info = None
        self.getItemInfo()
        logging.info("Static item %s selected" % self.name)
        self.source = "Premade Item"
    
    # For compatibility with the random item generator, getInfo, getName, and
    # getDescription should be functions
    def getInfo(self):
        return self.info
    
    def getName(self):
        name = self.name
        if cfg.getBool("General", "gen_scroll_spells") and self.category == "scroll" and not self.name_set:
            # Scrolls are all "Spell scroll (X Level)" so that's easy to replace.
            p1 = name.find("(")
            if p1 != -1:
                level = name[p1+1]
                if level.lower() == "c":
                    level = 0
                else:
                    level = int(level)
                spell = spells.Spell(level=level)
                name = self.name[:p1] + "(%s)" % spell.name      
                self.name = name # Lock our spell scroll in.
                self.name_set = True
        return name
    
    def getDescription(self):
        return self.description
        
    
    def getItemInfo(self):
        # Assigns the name, category, rarity, and description of the item's ID.
        self.name = item_data.get(self.id, "name")
        self.category = item_data.get(self.id, "category")
        self.rarity = item_data.get(self.id, "rarity")
        self.description = item_data.get(self.id, "description").replace("\\n","\n")
        self.info = item_data.get(self.id, "info")
            
    def getCategory(self, rarity):
        # Determines the item's category on the weighted list.
        clist = []
        wlist = []
        for category in cfg.config[rarity]:
            # Each item in the rarities represents a weight.
            weight = cfg.getInt(rarity, category)
            if weight > 0:
                # Make sure we have items to choose from in this category.
                cat_list = item_data.getOptionList("category", category)
                for item in cat_list:
                    if item_data.get(item, "rarity") == rarity:
                        clist.append(category)
                        wlist.append(weight)
                        break # We only need to make sure there's one item.
        return random.choices(clist, wlist)[0]
    
    def getRarity(self):
        # Pulls the rarity weights from the config file.
        rlist = ["common","uncommon","rare","veryrare","legendary"]
        wlist = []
        for rarity in rlist:
            wlist.append(cfg.getInt("Rarity", "%s_weight" % rarity))
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
        filtered_list = []
        item_list = item_data.getOptionList("category", category)
        for item in item_list:
            if item_data.get(item, "rarity") == rarity:
                filtered_list.append(item)
        # And, simply, choose one. No need for filters here.
        return random.choice(filtered_list)
    