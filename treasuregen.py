# Treasure Generator
# This file takes a given gold amount and generates some treasures from that.

import configparser
import random
import logging
import os



# First, load our configurations.
logging.info("Importing Treasures")
cfg = configparser.ConfigParser()
cfg.read("./config/general.cfg")
treasuredir = cfg["Folders"]["treasurefolder"]
# Now load the treasures
data = configparser.ConfigParser()
dlist = os.listdir("./%s" % treasuredir)
for d in dlist:
    if d[-4:] == ".cfg":
        data.read("./%s/%s" % (treasuredir, d))
        logging.info("Item file ./%s/%s loaded." % (treasuredir, d))
print("Treasure item files loaded.")

# Treasure categories can be user-defined. So we want to make a list of them.
categories = []
for d in data:
    if data.has_option(d, "category"):
        if data[d]["category"] not in categories:
            categories.append(data[d]["category"])


def getTreasureList(category=None, minvalue=None, maxvalue=None):
    # Grabs a list of treasures. Can restrict by category or value.
    ilist = []
    for i in data:
        # All treasures have to have some value.
        if data.has_option(i, "value"):
            if category is not None:
                if not data.has_option(i, "category"):
                    # No category on this item. Bye!
                    continue
                elif data[i]["category"] != category:
                    # It has one, but not a match.
                    continue
            if maxvalue is not None or minvalue is not None:
                v = data[i].getint("value")
            if maxvalue is not None:
                # Check our value ceiling.
                if maxvalue < v:
                    # Sorry, you're too expensive.
                    continue
            if minvalue is not None:
                if minvalue > v:
                    # Too cheap!
                    continue
            ilist.append(i)
    return ilist

class TreasurePile:
    def __init__(self, value, minvalue=None, maxvalue=None):
        self.value = value
        self.minvalue = minvalue
        if self.minvalue is None:
            self.minvalue = 0
        self.maxvalue = maxvalue
        if self.maxvalue is None:
            self.maxvalue = value
        self.contents = {}
        self.makePile()
        self.description = self.getDescription()
        logging.info("Created tresure pile worth %d" % self.getValue())
    
    def makePile(self):
        while self.getBudget() > 0:
            add = self.addItem(self.minvalue, self.maxvalue)
            if add is None:
                break
        return
    
    def addItem(self, minvalue, maxvalue):
        # Add a random item!
        # There's not a lot of control over this. That's intentional.
        # Make sure we're not getting greedy.
        if maxvalue > self.getBudget():
            maxvalue = self.getBudget()
        # Choose from our existing categories.
        category = self.getCategory(minvalue, maxvalue)
        if category == None:
            # We have no items that match.
            return None
        ilist = getTreasureList(category, minvalue, maxvalue)
        if len(ilist) == 0:
            return None
        choice = random.choice(ilist)
        if choice not in self.contents:
            # We have a new item.
            self.contents[choice] = 1
        else:
            # Another of an existing item.
            self.contents[choice] += 1
        return choice
    
    def getCategory(self, minvalue, maxvalue):
        # Grabs a category that has items that fit our filter.
        category = ""
        tries = 0
        while len(getTreasureList(category, minvalue, maxvalue)) == 0:
            category = random.choice(categories)
            tries += 1
            if tries > cfg["Treasuregen"].getint("maxtries"):
                # We've tried too many times.
                return None
        return category
    
    def getBudget(self):
        return self.value - self.getValue()
    
    def getValue(self):
        # Gets the total value of the treasure pile.
        value = 0
        for i in self.contents:
            ivalue = data[i].getint("value")
            qty = self.contents[i]
            value += (ivalue * qty)
        return value
    
    def getDescription(self):
        # Prints an orderly list of each item. Just sorted by name, not fancy.
        clist = []
        desc = []
        for t in self.contents:
            clist.append(t)
        clist.sort()
        for t in clist:
            tdesc = ""
            tname = data[t]["name"]
            qty = self.contents[t]
            value = data[t].getint("value")
            cat = data[t]["category"]
            tdesc += "%sx %s (%s), %s gp each" % (str(qty), tname, cat, str(value))
            if qty > 1:
                tdesc += ", %s gp total." % str(value * qty)
            else:
                tdesc += "."
            desc.append(tdesc)
        return "\n".join(desc)
        #return desc