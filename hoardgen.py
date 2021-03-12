# New Hoard Generator
# Generates a random, level-dependent hoard based on input configurations.
# Designed to pull from either existing items, or from the random item generator

import configparser
import random
import logging
import os
import time

# Some cnstants.
VERSION = "2021.3.11 (Alpha)" # Just a version number. Calendar Version.

print("New Hoard Generator starting...")

"""# First, set up logging.
starttime = time.strftime("%Y %m %d %H %M %S", time.localtime(time.time()))
# Make sure our logging folder exists.
if not os.path.isdir("./logs"):
    os.mkdir("./logs")
# And start logging.
logging.basicConfig(filename="./logs/output %s.log" % starttime, filemode='w', level=logging.DEBUG)
logging.info("Beginning log file for session starting: %s" % starttime)"""

# Now load our configuration.
cfg = configparser.ConfigParser()
cfg.read("./config/general.cfg")
logging.info("Config file loaded: ./config/general.cfg")

# Our max CR. Referenced in Hoard and also from other things (AKA the UI)
MAXCR = cfg["General"].getint("maxcr")

generators = configparser.ConfigParser()
generators.read("./config/generators.cfg", encoding="cp1252")
logging.info("Generator config file loaded.")

"""# Remove any excess log files.
llist = []
for l in os.listdir("./logs"):
    if l[-4:] == ".log":
        llist.append(l)
if len(llist) > cfg["General"].getint("logstokeep"):
    llist.sort(reverse=True) # Sort by oldest, since they're named by time.
    logs = len(llist)
    while len(llist) > cfg["General"].getint("logstokeep"):
        log = llist.pop()
        os.remove("./logs/%s" % log)
    logging.info("Removed %d old log files." % (logs - len(llist)))"""

# Now load our sub-modules.
import staticitem # For static, pre-made magic items
import itemgen # For randomly created magic items
import treasuregen # For our treasure pile
import hoardname # For the names. Of our hoards. Of course.
import pdfwrite # For saving our hoards.
pdfwrite.NHGVER = VERSION # Tells the PDF generator our main generator version

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
            elif cr > MAXCR:
                cr = MAXCR
            self.cr = cr
        else:
            self.cr = random.randint(0, MAXCR)
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
        #self.description = self.getDescription()
    
    def getGenerator(self):
        # Returns which generator we're using depending on CR.
        logging.info("Finding generator for CR %d" % self.cr)
        # We already know we're within the max CR bounds from our init
        for gen in generators:
            # Get the min and max CRs of the generator.
            mincr = generators[gen].getint("mincr")
            maxcr = generators[gen].getint("maxcr")
            if mincr is None or maxcr is None:
                # This isn't a generator. Move along, move along.
                continue
            if mincr <= self.cr and maxcr >= self.cr:
                logging.debug("Using generator %s." % gen)
                return gen
                # We can stop looking now.
        logging.error("No valid generator found. Using default.")
        gen = cfg["General"]["defaultgenerator"]
        return gen
                
    def getValue(self, target):
        if target not in ["hoard", "treasure", "item"]:
            # Defaulting to any of these could be bad, so just return 0.
            return 0
        # Returns a value within the set bounds.
        # Get our values. Make sure they're sane, too.
        dice = generators[self.gen]["%sdice" % target].lower()
        mult = generators[self.gen].getint("%smultiplier" % target)
        if mult is not None:
            mult = max(mult, 1)
        else:
            mult = 1
        div = generators[self.gen].getint("%sdivisor" % target)
        if div is not None:
            div = max(div, 1)
        else:
            div = 1
        tries = generators[self.gen].getint("%stries" % target)
        if tries is not None:
            tries = max(tries, 1)
        else:
            tries = 1
        mod = generators[self.gen].getint("%smodifier" % target)
        if mod is None:
            mod = 0
        if generators.has_option(self.gen, "%smaxmin" % target):
            maxmin = generators[self.gen]["%smaxmin" % target].lower()
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
        for r in rarities:
            weight = generators[self.gen].getint("%swt" % r)
            if weight is not None:
                rweights.append(weight)
            else:
                rweights.append(1)
            value = generators[self.gen].getint("%svalue" % r)
            if value is not None:
                if value < 1:
                    value = 1
                rvalues[r] = value
            else:
                rvalues[r] = 1
        sources = ["static", "random"]
        sweights = []
        for s in sources:
            weight = generators[self.gen].getint("%swt" % s)
            if weight is not None:
                sweights.append(weight)
            else:
                sweights.append(1)
        forcescroll = generators[self.gen].getboolean("forcerandomscroll")
        if forcescroll is None:
            forcescroll = False
        # Grab a list of existing items.
        inames = []
        for i in self.items:
            inames.append(i.name)
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
            if source == "static":
                # A random static item.
                item = staticitem.Item(rarity=rarity)
                # No duplicates.
                if forcescroll and "Spell Scroll" in item.name:
                    # We have a spell scroll. Give us one with a random spell.
                    # But first, figure out which one it is.
                    slevel = int(item.id[-1])
                    item = itemgen.ForceScroll(slevel)
            elif source == "random":
                # Depending on settings, this can return an item of lower rarity
                # But that's dealt with later.
                item = itemgen.getItem(rarity=rarity)
                while item.name in inames:
                    item = itemgen.getItem(rarity=rarity)
            budget -= rvalues[item.rarity]
            inames.append(item.name)
            self.items.append(item)
        return budget
        
    def getItemList(self):
        # Returns a string of each item's name.
        items = []
        for i in self.items:
            items.append(i.name)
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

    def getSaveName(self):
        # Gets a filename for the, well. File.
        # Simply removes forbidden characters.
        forbidden = [";",":","/","\\","<",">",'"',"'","|","?","*",",","!"]
        name = self.name.name
        for f in forbidden:
            name.replace(f, "")
        while name[-1] == " ":
            name = name[:-1]
        while name[-1] == ".":
            name = name[:-1]
        name += " (CR %d)" % self.cr
        return name
    
    def saveHoard(self, savename=None, savedir=None):
        # Pulls information and shoves it into the pdf writer for, uh. Writing.
        # First, set up the basic information.
        pdf = pdfwrite.PDF(self.name.name, self.seed, self.cr)
        # Now we're going to print the information on the gold and treasure.
        trdesc = "%d gold pieces\n" % self.gp + self.treasure.description
        trinfo = "Treasure (%d gp value):" % (self.treasure.value + self.gp)
        pdf.addItem(iinfo=trinfo, idesc=trdesc, indent=False)
        # And now the items.
        for i in self.items:
            indent = True
            if i.id == "spellbookitem":
                # Don't indent our list of spells.
                indent = False
            pdf.addItem(iname=i.name, iinfo=i.info, idesc=i.description, indent=indent)
        # And save it.
        if type(savename) is not str:
            savename = self.getSaveName() + ".pdf"
        if savename[-4:] != ".pdf":
            savename += ".pdf"
        folder = cfg["Folders"]["savefolder"]
        if not os.path.exists("./%s" % folder):
            os.mkdir("./%s" % folder)
        if savedir is None:
            savename = "./%s/%s" % (folder, savename)
        else:
            savename = "%s/%s" % (savedir, savename)
        pdf.output(savename)
        return True
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        