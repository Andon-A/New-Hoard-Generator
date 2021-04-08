# New Hoard Generator
# Generates a random, level-dependent hoard based on input configurations.
# Designed to pull from either existing items, or from the random item generator

#import configparser
import random
import logging
import os
#import time
import configs

# Set up our configuration with the new configs files.
general = configs.GENERAL
generators = configs.HOARD_GENERATORS

MAX_CR = general.getInt("Generators", "max_cr")

# Now load our sub-modules.
import staticitem # For static, pre-made magic items
import itemgen # For randomly created magic items
import spellbook # Spellbooks are neat!
import treasuregen # For our treasure pile
import hoardname # For the names. Of our hoards. Of course.


# A function to roll dice.
def rollDice(dice):
    if type(dice) is int:
        qty = 1
        sides = dice
    elif type(dice) is list or type(dice) is tuple:
        qty = dice[0]
        sides = dice[1]
    else:
        # Can't parse this.
        return 0, [0]
    if type(sides) != int:
        return [0] # If we have an error, return an impossible result.
    if sides < 1:
        # Make sure we have a valid argument to not break things.
        sides = 1
    roll = []
    for r in range(0,qty):
        roll.append(random.randint(1,sides))
    return sum(roll), roll

class Hoard:
    # Time to make a hoard!
    def __init__(self, cr=None, seed=None, name=None):
        if type(seed) is str:
            self.seed = seed
        else:
            self.seed = self.makeSeed()
        random.seed(self.seed)
        if type(cr) is int:
            if cr < 0:
                cr = 0
            elif cr > MAX_CR:
                cr = MAX_CR
            self.cr = cr
        else:
            self.cr = random.randint(0, MAX_CR)
        if type(name) is str:
            self.name = hoardname.HoardName(self.cr, name)
        else:
            self.name = hoardname.HoardName(self.cr)
        self.gen = self.getGenerator()
        self.items = []
        self.itemlimit = self.getValue("item")
        self.treasurevalue = round(self.getValue("treasure"), -1) # Round to 10.
        self.treasure = treasuregen.TreasurePile(self.treasurevalue)
        self.gp = self.getValue("hoard")
        self.getItems()
        self.itemlist = self.getItemList()
    
    def getGenerator(self):
        # Returns which generator we're using depending on CR.
        logging.info("Finding generator for CR %d" % self.cr)
        # We already know we're within the max CR bounds from our init
        for gen in generators.config:
            # Get the min and max CRs of the generator.
            mincr = generators.getInt(gen, "min_cr")
            maxcr = generators.getInt(gen, "max_cr")
            if mincr is None or maxcr is None:
                # This isn't a generator. Move along, move along.
                continue
            if mincr <= self.cr and maxcr >= self.cr:
                logging.debug("Using generator %s." % gen)
                return gen
                # We can stop looking now.
        logging.error("No valid generator found. Using default.")
        gen = general.get("Generators", "default_generator")
        return gen
                
    def getValue(self, target):
        if target not in ["hoard", "treasure", "item"]:
            # Defaulting to any of these could be bad, so just return 0.
            return 0
        # Returns a value within the set bounds.
        # Get our values. Make sure they're sane, too.
        dice = generators.get(self.gen, "%s_dice" % target).lower()
        mult = generators.getInt(self.gen, "%s_multiplier" % target)
        if mult is not None:
            mult = max(mult, 1)
        else:
            mult = 1
        div = generators.getInt(self.gen, "%s_divisor" % target)
        if div is not None:
            div = max(div, 1)
        else:
            div = 1
        tries = generators.getInt(self.gen, "%s_tries" % target)
        if tries is not None:
            tries = max(tries, 1)
        else:
            tries = 1
        mod = generators.getInt(self.gen, "%s_modifier" % target)
        if mod is None:
            mod = 0
        maxmin = generators.get(self.gen, "%s_max_min" % target)
        if maxmin is not None:
            if maxmin not in ["max","min"]:
                maxmin = "min"
        else:
            maxmin = "min"
        # Parse our dice. They're given in xdy format, x = quantity, y = size
        logging.info("Rolling %s for %s value" % (dice, target))
        dice = dice.split("d")
        # gpdice[0] is quantity, gpdice[1] is sides. Dice roller expects this.
        dice = (int(dice[0]), int(dice[1]))
        # Now roll those dice!
        value = rollDice(dice)[0]
        if tries > 1:
            for r in range(0, tries-1):
                if maxmin == "min":
                    value = min(value, rollDice(dice)[0])
                elif gpmaxmin == "max":
                    value = max(value, rollDice(dice)[0])
        # Now we have our multiplier, divisor, and modifier. In that order.
        value = value * mult # Our sanity check makes sure we have a good number.
        value = value / div # And here.
        value += mod
        return int(value)
        
    def getItems(self):
        # Determines rarity of the item and where it'll get the items from.
        # But first, some settings.
        rvalues = {}
        rarities = ["common", "uncommon", "rare", "veryrare", "legendary"]
        rweights = []
        for rarity in rarities:
            weight = generators.getInt(self.gen, "%s_weight" % rarity)
            if weight is not None:
                rweights.append(weight)
            else:
                rweights.append(1)
            value = generators.getInt(self.gen, "%s_value" % rarity)
            if value is not None:
                if value < 1:
                    value = 1
                rvalues[rarity] = value
            else:
                rvalues[rarity] = 1
        #TODO: Spellbooks.
        sources = ["static", "random", "spellbook"]
        sweights = []
        for source in sources:
            weight = generators.getInt(self.gen, "%s_weight" % source)
            if weight is not None:
                sweights.append(weight)
            else:
                sweights.append(1)
        # Grab a list of existing items.
        # OK, we have our settings. Get our budget.
        budget = self.itemlimit
        # And start adding items.
        while budget > 0:
            if budget < 3 and rweights[1] == 0:
                # We've run out of budget for our other items.
                # Turn them off, and allow uncommon items.
                rweights[1] = 1
                rweights[2] = 0
                rweights[3] = 0
                rweights[4] = 0
            if budget < 2 and rweights[0] == 0:
                # Similar to the above. We only have the budget for common
                # items but they're turned off. Allow them. And turn off higher
                # things because we can't generate them anyway.
                rweights = [1,0,0,0,0]
            rarity = random.choices(rarities, rweights)[0]
            while rvalues[rarity] > budget:
                rarity = random.choices(rarities, rweights)[0]
            source = random.choices(sources, sweights)[0]
            item = None
            force_rarity = generators.getBool(self.gen, "force_rarity")
            if source == "static":
                # A random static item.
                # The way these work, we don't have to worry about rarity.
                item = staticitem.Item(rarity=rarity)
            elif source == "random":
                # This is unlikely to return an item of lower rarity, but maybe.
                item = itemgen.Item(rarity=rarity)
                if force_rarity:
                    # Make sure we have the rarity we asked for.
                    while item.rarity != rarity:
                        item = itemgen.Item(rarity=rarity)
                else:
                    # Make sure we're not overcosting ourselves. I expect that
                    # items will only ever under-cost themselves, but just in case.
                    while rvalues[item.rarity] > budget:
                        item = itemgen.Item(rarity=rarity)
            elif source == "spellbook":
                item = spellbook.Spellbook(rarity=rarity)
                # Spellbooks should never get a rarity that's different than asked
                # So don't worry about those.
            budget -= rvalues[item.rarity] # The actual item rarity. Just in case it's different.
            self.items.append(item)
        return budget
        
    def getItemList(self):
        # Returns a string of each item's name.
        items = []
        for i in self.items:
            items.append(i.getName())
        items = "\n".join(items)
        return items
        
    def makeSeed(self):
        # Generates a 25-character string for use as a seed.
        # Largely, it's just so it can be re-typed later to generate again.
        seed = ""
        while len(seed) < 25:
            l = random.randint(1,3) # Choose number, uppercase, lowercase
            if l == 1:
                # Numbers
                l = random.randint(48,57)
            elif l == 2:
                # UPPERCASE
                l = random.randint(65,90)
            else:
                # lowercase
                l = random.randint(97,122)
            seed += chr(l)
        return seed
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        