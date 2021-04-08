# Treasure Generator
# This file takes a given gold amount and generates some treasures from that.

import random
import logging
import configs

general = configs.GENERAL
item_data = configs.TREASURE_DATA

# Treasure categories can be user-defined. So we want to make a list of them.
categories = []
for item in item_data.config:
    category = item_data.get(item, "category")
    if category is not None and category not in categories:
        categories.append(category)


def getTreasureList(category=None, min_value=None, max_value=None):
    # Grabs a list of treasures. Can restrict by category or value.
    item_list = []
    for item in item_data.config:
        item_value = item_data.getInt(item, "value")
        item_category = item_data.get(item, "category")
        # Check our category
        if category is not None:
            if category != item_category:
                continue
        # Check our value
        if min_value is not None:
            if item_value < min_value:
                continue
        if max_value is not None:
            if item_value > max_value:
                continue
        item_list.append(item)
    return item_list

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
            if tries > general.getInt("Treasuregen", "max_tries"):
                # We've tried too many times.
                return None
        return category
    
    def getBudget(self):
        return self.value - self.getValue()
    
    def getValue(self):
        # Gets the total value of the treasure pile.
        value = 0
        for item in self.contents:
            item_value = item_data.getInt(item, "value")
            qty = self.contents[item]
            value += (item_value * qty)
        return value
    
    def getDescription(self):
        # Prints an orderly list of each item. Just sorted by name, not fancy.
        item_list = []
        desc = []
        for item in self.contents:
            item_list.append(item)
        item_list.sort()
        for item in item_list:
            item_name = item_data.get(item, "name")
            item_qty = self.contents[item]
            item_value = item_data.getInt(item, "value")
            item_category = item_data.get(item, "category")
            item_desc = "%sx %s (%s), %s gp each" % (str(item_qty), item_name, item_category, str(item_value))
            if item_qty > 1:
                item_desc += ", %s gp total." % str(item_value * item_qty)
            else:
                item_desc += "."
            desc.append(item_desc)
        return "\n".join(desc)
        #return desc