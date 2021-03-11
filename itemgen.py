import random
import configparser
import os
import logging
import time

""" This program generates a specified magic item with random properties.
These properties are similar to the ones found in various editions, with
additional properties added that would seem cool or neat or otherwise
fun.

The program is simply a generator, and doesn't choose what to generate.
That's the purview of a different file. It'll generate, say, an
Uncommon Weapon when you tell it to, but you can't tell it to "Make an
item"."""

# We don't need to do any logging setup since this will be a sub-file.
# But we do need config stuff.
general = configparser.ConfigParser()
general.read("./config/general.cfg")
cfg = configparser.ConfigParser()
cfg.read("./config/itemgen.cfg", encoding="cp1252")
# print("Item Generator config loaded")
logging.info("Item Generator config loaded.")
# Load our item files
dfolder = general["Folders"]["itemfolder"]
data = configparser.ConfigParser()
ilist = os.listdir("./%s" % dfolder)
for i in ilist:
    if i[-4:] == ".cfg":
        # A config file. Load it.
        data.read("./%s/%s" % (dfolder, i), encoding="cp1252")
        # print("Item file %s loaded." % i)
        logging.info("Item file ./%s/%s loaded." % (dfolder, i))
print("Item generator files loaded.")
    
# A variable that lists every type of equipment we generate.
# It's used a few times so best to put it where everyone can reach it.
itemtypes = ["ammunition", "armor", "belt", "boots", "bracers", "eyewear",
        "hat", "ring", "rod", "shield", "staff", "trinket", "wand", "weapon",
        "cloak", "gloves", "scroll", "spellbook"]

def getItem(rarity=None, itemtype=None, forcerarity=False):
    # Returns a random item!
    # First get our weights
    weights = {}
    for i in itemtypes:
        weights[i] = cfg["Itemweights"].getint(i)
        if weights[i] is None:
            weights[i] = 1
    # Alright, now let's choose our choices.
    if type(itemtype) is tuple or type(itemtype) is list:
        # We've had our choices narrowed, but still take the item types.
        wlist = []
        tlist = []
        for i in itemtype:
            # Make sure it's only valid item types.
            i = i.lower()
            if i in weights:
                tlist.append(i)
                wlist.append(weights[i])
        if len(tlist) == 0:
            itemtype = None # We'll just pick a completely random one.
        else:
            itemtype = random.choices(tlist, wlist)[0]
    # If we have made no choices, choose from any.
    if type(itemtype) is not str:
        wlist = []
        tlist = []
        for w in weights:
            tlist.append(w)
            wlist.append(weights[w])
            itemtype  = random.choices(tlist, wlist)[0]
    itemtype = itemtype.lower() # Just to make sure.
    if itemtype == "ammunition":
        return Ammunition(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "armor":
        return Armor(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "belt":
        return Belt(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "boots":
        return Boots(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "bracers":
        return Bracers(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "eyewear":
        return Eyewear(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "hat":
        return Hat(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "ring":
        return Ring(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "rod":
        return Rod(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "shield":
        return Shield(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "staff":
        return Staff(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "trinket":
        return Trinket(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "wand":
        return Wand(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "weapon":
        return Weapon(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "cloak":
        return Cloak(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "gloves":
        return Gloves(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "scroll":
        return Scroll(rarity=rarity, forcerarity=forcerarity)
    elif itemtype == "spellbook":
       return Spellbook(rarity=rarity, forcerarity=forcerarity)
    else:
        # When all else fails, give us a fancy shiny.
        # This means we'll always get SOMETHING.
        return WondrousItem(rarity=rarity, forcerarity=forcerarity)

# A variable for classes and one for spell schools. Used for spells.
# These are both assigned later.
classes = []
spellschools = []

def getList(section, option, config=data):
    # Several of the keys used are semicolon-separated lists.
    # This makes it easier to grab them.
    if config.has_option(section, option):
        # We haven't done a oops.
        l = config[section][option]
        l = l.split(";")
        return l
    else:
        logging.debug("Section %s does not have option %s" % (section, option))
        return []

def getData(section, option, config=data):
    # Gets the data, or returns None if none available.
    if config.has_option(section, option):
        return config[section][option]
    else:
        logging.debug("Section %s does not have option %s" % (section, option))
        return []

def getSet(item):
    # Turns something into a set. This happens more than a few times.
    # So having it as one thing makes it easier.
    if type(item) == set:
        return item # Well that was easy.
    elif type (item) == str:
        # Strings are all going to be semicolon separated.
        return set(item.split(";"))
    elif type(item) == list or type(item) == tuple:
        # Easy peasy.
        return set(item)
    else:
        logging.error("Can only convert strings, lists, or tuples to sets!")
        raise ValueError("Can only convert strings, lists, or tuples to sets!")

def getCategoryList(category, hasoption=None, config=data):
        # Grabs a list of items, effects, etc of a specific category
        ilist = []
        for i in config:
            # Make sure we have the key in question
            if config.has_option(i, "category"):
                # And make sure it matches.
                if config[i]["category"] == category:
                    # Good, it does. Add it to the list.
                    if hasoption is None:
                        ilist.append(i)
                    elif hasoption is not None and config.has_option(i, hasoption):
                        ilist.append(i)
        # Now return the full list.
        return ilist

# Now that the appropriate function exists, let's grab ourselves a spell list.
# We'll use this to populate our class and school lists.
for s in getCategoryList("spell"):
    school = data[s]["group"]
    clist = getList(s, "class")
    if school not in spellschools:
        spellschools.append(school)
    for c in clist:
        if c not in classes:
            classes.append(c)

# Changes the dice size. Not sure if I'll need this outside the item class, but
# there's really no reason for it to be in there so. Here it is.
def changeDiceSize(workstr, increase=True):
    workstr = workstr.lower()
    if "d" not in workstr and increase:
        # We have a number.
        # Hopefully.
        # Since we don't care what the number is, we can add things.
        # In this case, the amount of damage, in d4s.
        return workstr + "d4"
    elif "d" not in workstr:
        # We don't reduce non-dice amounts.
        return workstr
    dice = workstr.split("d")
    dice[1] = int(dice[1])
    if not increase and dice[1] in [6,8,10,12]:
        # These are the only ones we can reduce.
        dice[1] -= 2
    elif increase and dice[1] in [4,6,8,10]:
        # Simialrly, we only increase these.
        dice[1] += 2
    elif increase and dice[1] == 3:
        # Well, a special case here. No standar weapons are D3s,
        # But sometimes homebrew.
        dice[1] += 1
    dice[1] = str(dice[1])
    workstr = "d".join(dice)
    return workstr

def compareDice(dice1, dice2):
    # Compares two sets of dice (YdX) using their average rolls, then returns
    # the set with the higher average. If they are the same, it uses the max.
    if type(dice1) is not str or type(dice2) is not str:
        # We can't compare it.
        return None
    dice1 = dice1.lower()
    dice2 = dice2.lower()
    if "d" not in dice1:
        # Stupid blowgun not using dice.
        dice1str = dice1
        dice1avg = int(dice1)
        dice1max = int(dice1)
    else:
        # Get the components of the dice string.
        dice1str = dice1
        dice1 = dice1.split("d")
        dice1[0] = int(dice1[0])
        dice1[1] = int(dice1[1])
        # For dice, the average is always Sides / 2 + 0.5.
        # Then multiply that by the number of dice.
        dice1avg = ((dice1[1] / 2) + 0.5) * dice1[0]
        dice1max = dice1[1] * dice1[0]
    if "d" not in dice2:
        dice2str = dice2
        dice2avg = int(dice2)
        dice2max = int(dice2)
    else:
        dice2str = dice2
        dice2 = dice2.split("d")
        dice2[0] = int(dice2[0])
        dice2[1] = int(dice2[1])
        dice2avg = ((dice2[1] / 2) + 0.5) * dice2[0]
        dice2max = dice2[1] * dice2[0]
    # Now our comparisons.
    if dice1avg == dice2avg:
        # Have the same average. Go for the max.
        if dice2max > dice1max:
            return dice2str
        else:
            # At this point, either they're the same (And probably identical)
            # Or set 1 is bigger. Either way, it doesn't matter.
            return dice1str
    elif dice2avg > dice1avg:
        return dice2str
    else:
        
        return dice1str

def checkAttunement(id1, id2):
    # Make sure our data is valud.
    if id1 not in data:
        logging.debug("Effect %s does not exist." % id1)
        return False
    if id2 not in data:
        logging.debug("Effect %s does not exist." % id2)
        return False
    if not data.has_option(id1, "attunement"):
        # No attunement requirement can be combined with any attunement.
        return True
    if not data.has_option(id2, "attunement"):
        # Same as above.
        return True
    # Now get our information for actual checking.
    attune1 = data[id1]["attunement"].lower()
    attune2 = data[id2]["attunement"].lower()
    restrict1 = None
    restrict2 = None
    if attune1 == "false" or attune2 == "false":
        # One or the other has no attunement requirements.
        # So it doesn't matter.
        return True
    # Now see if any of our joins are false.
    if data.has_option(id1, "attunementjoin"):
        if not data[id1].getboolean("attunementjoin"):
            # Can't join with this one.
            return False
    if data.has_option(id2, "attunementjoin"):
        if not data[id2].getboolean("attunementjoin"):
            return False
    # Now check if we have descriptions that don't match.
    if attune1 == "desc":
        # A description.
        if not data.has_option(id1, "attunementrestriction"):
            # But none provided.
            attune1 = "true"
        else:
            restrict1 = data[id1]["attunementrestriction"]
    if attune2 == "desc":
        if not data.has_option(id2, "attunementrestriction"):
            attune2 = "true"
        else:
            restrict2 = data[id1]["attunementrestriction"]
    # Now we have our restrictions in place, if they exist.
    if attune1 == "desc" and attune2 == "desc":
        # Two descriptions.
        if restrict1 == restrict2:
            # Identical descriptions can be combined.
            return True
        else:
            # Different ones cannot.
            return False
    elif attune1 == "desc" and attune2 == "true":
        # Good to go.
        return True
    elif attune2 == "desc" and attune1 == "true":
        # Same here.
        return True
    elif attune1 == "true" and attune2 == "true":
        # Still good.
        return True
    else:
        # Honestly not sure how we got here. Buuut. Just in case.
        return False

# We're going to make a class
# Maybe there will be students?

class Spell:
    # For use on scrolls, staffs, and wands. Maybe rods?
    def __init__(self, school=None, level=None, maxlevel=None, minlevel=None,
                chclass=None, itemtype=None, id=None):
        self.id = self.getSpell(school, level, minlevel, maxlevel, chclass,
                itemtype, id)
        if self.id is not None:
            self.name = data[self.id]["name"]
            self.level = data[self.id].getint("level")
            self.school = data[self.id]["group"]
            self.classlist = getList(self.id, "class")
        else:
            self.name = ""
            self.level = None
            self.school = None
            self.classlist = []
    
    def getSpell(self, school, level, minlevel, maxlevel, chclass, items, id):
        # Finds a random spell of the given school, level that is on the given
        # class's spell list.
        slist = getCategoryList("spell")
        if id is not None:
            id = id.lower()
            # Check the one we've been given. Ignore filters for it.
            if id in slist:
                return id
            else:
                logging.debug("Spell %s does not exist. Ignoring." % id)
        # If we have these items, then we need to make sure they're right.
        if school is not None:
            if type(school) is str:
                school = school.lower()
            school = getSet(school)
        if level is not None:
            level = int(level)
            if level < 0 or level > 9:
                # Out of bounds.
                # This can be used to intentionally generate a "None" spell.
                logging.debug("Level value out of bounds. Returning None.")
                return None
        if minlevel is not None:
            if level is not None:
                # Specific level will override.
                minlevel = None 
            minlevel = int(minlevel)
            if minlevel <= 0:
                # This is the same as no filter.
                minlevel = None
            elif minlevel > 9:
                # This will filter out everything.
                logging.debug("Minimum level higher than 9. Ignoring.")
                minlevel = None
        if maxlevel is not None:
            if level is not None:
                # Again, specific will override.
                maxlevel = None
            maxlevel = int(maxlevel)
            if maxlevel < 0:
                # We'll filter out everything.
                logging.debug("Maximum level lower than 0. Ignoring.")
                maxlevel = None
            elif maxlevel >= 9:
                # Same as no filter, so ignore it.
                maxlevel = None
        if chclass is not None:
            if type(chclass) is str:
                chclass = chclass.lower()
            chclass = getSet(chclass)
        if items is not None:
            items = getSet(items)
        # Since we have the list, now we need to filter it.
        flist = []
        for s in slist:
            # Items. Can this spell go on this item?
            if items is not None:
                spvalue = getSet(getList(s, "itemtype"))
                if not items.issubset(spvalue):
                    # Our itemtype is not in the list.
                    continue
            # School filter.
            if school is not None:
                # A school filter. We have a list of schools, make sure that
                # the spell's school is in it.
                spvalue = getSet(data[s]["group"].lower())
                if not spvalue.issubset(school):
                    # Our school is not included.
                    continue 
            # Now for level filters.
            if level is not None or minlevel is not None or maxlevel is not None:
                spvalue = data[s].getint("level")
            if level is not None:
                # A level filter.
                if spvalue != level:
                    # It's not the level we want.
                    continue
            if minlevel is not None:
                if spvalue < minlevel:
                    # Too low!
                    continue
            if maxlevel is not None:
                if spvalue > maxlevel:
                    # Too high!
                    continue
            # Alright, now we've got our goldilocks level just right.
            # Class time.
            if chclass is not None:
                spvalue = getSet(getList(s, "class"))
                if chclass.isdisjoint(spvalue):
                    # None of our filter classes are present.
                    continue
            # Hooray, if we've made it this far, we can start adding to the list!
            flist.append(s)
        if len(flist) == 0:
            # No spell for us.
            logging.debug("Filters returned no spells.")
            return None
        spell = random.choice(flist)
        return spell

class Modifier:
    def setup(self):
        self.name = ""
        self.prefix = ""
        self.suffix = ""
        self.bonus = 0
        self.modifiers = {}
        self.randomlists = {}
        self.choice = None
        self.spells = [None] * 10 # Ten empty spell sockets.
        self.attunement = None
        self.attunementjoin = True # Default to allowing joining.
        
    def getAttunement(self):
        # Assigns the attunement information.
        if data.has_option(self.id, "attunement"):
            a = data[self.id]["attunement"].lower()
            if a == "true":
                # We have attunement.
                if data.has_option(self.id, "attunementrequirements"):
                    self.attunement = getList(self.id, "attunementrequirements")
                else:
                    self.attunement = True
                if data.has_option(self.id, "attunementjoin"):
                    # See if we can combine it with other (like) attunements.
                    self.attunementjoin = data[self.id].getboolean("attunementjoin")
                return True
            elif a == "desc":
                if data.has_option(self.id, "attunementrequirements"):
                    self.attunement = data[self.id]["attunementrequirements"]
                else:
                    self.attunement = True
                if data.has_option(self.id, "attunementjoin"):
                    # See if we can combine it with other (like) attunements.
                    self.attunementjoin = data[self.id].getboolean("attunementjoin")
                return True
            else:
                # No attunement for this item.
                self.attunement = False
                return False
        else:
            # None defaults to no attunement
            self.attunemenet = False
            return False
    
    def getModifiers(self):
        # Pulls the pre-programmed effects if they're available.
        mods = {}
        for c in ["armor", "item", "weapon", "ammunition", "shield"]:
            if data.has_option(self.id, c + "modifiers"):
                # There are effects, but we need to parse them.
                parsed = []
                effect = data[self.id][c + "modifiers"]
                effect = effect.split(";")
                for i in effect:
                    # We are parsing, not validating.
                    if i.find("(") == -1:
                        # This one has no arguments.
                        # Put it into a list, though.
                        parsed.append([i]) 
                    else:
                        # Find our arguments
                        p1 = i.find("(")
                        p2 = i.find(")")
                        l = [] # We'll be putting the parsed stuff in here.
                        l.append(i[:p1]) # The command.
                        l += i[p1+1:p2].split(",") # Split the arguments.
                        parsed.append(l)
                mods[c] = parsed
        return mods
        
    def getRandomLists(self):
        # Retrieves the random lists
        lists = {}
        for i in range(0,10):
            if data.has_option(self.id, "randomlist%d" % i):
                lists["R%d" % i] = getList(self.id, "randomlist%d" % i)
        return lists
        
    def chooseRandom(self):
        # Gets a random number, from 0 to the minimum length of one of the lists.
        # They SHOULD all be the same length, but. Well. This way it still works.
        length = -1
        for r in self.randomlists:
            if len(self.randomlists[r]) < length or length == -1:
                length = len(self.randomlists[r])
        if length > 0:
            return random.randint(0,length-1)
        else:
            return None
    
    def replaceRandom(self, workstr):
        # Replaces the randomly generated things, both from lists and spells.
        if workstr is None:
            # Just in case.
            return ""
        elif workstr == "":
            # Nothing to replace here.
            return ""
        # Random choices.
        if self.choice is not None:
            for r in range(0, 10):
                if "R%d" % r in self.randomlists:
                    insert = self.randomlists["R%d" % r][self.choice]
                    workstr = workstr.replace("@R%d" % r, insert).replace("@r%d" % r, insert)
        for r in range(0,10):
            if self.spells[r] is not None:
                ins = self.spells[r].name
                workstr = workstr.replace("@spell%d" % r, ins)
        return workstr
    
    def updateText(self):
        # Updates the text if it needs to be.
        # Useful for things like spells, where they're generated after the
        # effect is.
        self.name = self.replaceRandom(self.name)
        self.prefix = self.replaceRandom(self.prefix)
        self.suffix = self.replaceRandom(self.suffix)
    
    def getDescription(self, category):
        # Returns the description for the appropriate category, if applicable.
        descs = {}
        for i in itemtypes:
            if data.has_option(self.id, i + "description"):
                descs[i] = data[self.id][i + "description"].replace("\\n", "\n")
        if category not in descs:
            # No description here.
            return None
        # Now get the description.
        desc = descs[category]
        # And substitutions.
        for i in itemtypes:
            if i in descs:
                desc = desc.replace("@%sdescription" % i, descs[i])
        # And random choices.
        desc = self.replaceRandom(desc)
        return desc
        
class Material(Modifier):
    def __init__(self, category=None, subtype=None, itemid=None,
        damagetype=None, materialtype=None, group=None, properties=None,
        maxbonus=None):
        self.setup()
        # Grab a random material fitting the filters.
        self.id = self.getMaterial(category, subtype, itemid, damagetype,
        materialtype, group, properties, maxbonus)
        # Set ourselves appropriately
        self.setValues()
        self.getAttunement()
    
    def setValues(self):
        if self.id is None:
            self.materialtype = None
            return True
        self.randomlists = self.getRandomLists()
        self.choice = self.chooseRandom()
        self.name = data[self.id]["name"]
        self.name = self.replaceRandom(self.name)
        self.bonus = data[self.id].getint("bonus")
        self.modifiers = self.getModifiers() # Dict for effects.
        self.materialtype = getList(self.id, "materialtype")        
    
    def getMaterial(self, category, subtype, itemid, damagetype, materialtype,
        group, properties, maxbonus):
        # Gets a list of materials and then filters by several things.
        # If our filters return nothing, we return None.
        # If a filter is passed as "None" then it is ignored.
        mlist = getCategoryList("material")
        flist = [] # Filtered list. Suitable materials get put here.
        wlist = [] # Chance weights
        for m in mlist:
            # Add filters here.
            # Category filter.
            if category is not None:
                # We have a category of item to pick a material for.
                # Grab our own list.
                allow = getSet(getList(m, "itemtype"))
                if category not in allow and len(allow) > 0:
                    # Nope, our category doesn't match.
                    continue
            # Subtype filter
            if subtype is not None:
                # We have a subtype filter to match.
                # We only need to worry about matching one of them.
                subtype = getSet(subtype)
                allow = getSet(getList(m, "itemsubtype"))
                restrict = getSet(getList(m, "subtypeconflict"))
                if not subtype.isdisjoint(restrict):
                    # One or more of our subtypes is prohibited.
                    continue
                if len(allow) > 0 and allow.isdisjoint(subtype):
                    # Our material only applies to certain subtypes, and this
                    # is not one of them.
                    continue
            # Item ID filter.
            if itemid is not None:
                # Sometimes, materials disallow specific items.
                restrict = getList(m, "itemconflict")
                if itemid in restrict:
                    continue
            # Damagetype filter.
            if damagetype is not None:
                # Can be both required or restricted.
                allow = getList(m, "damagetype")
                restrict = getList(m, "damagetypeconflict")
                if damagetype not in allow and len(allow) > 0:
                    # Sorry, we don't fit.
                    continue
                if damagetype in restrict:
                    # We're not welcome.
                    continue
            # Materialtype filter
            if materialtype is not None:
                # Fairly simple here. Make sure the material can be used
                # for this item.
                materialtype = getSet(materialtype)
                allow = getSet(getList(m, "materialtype"))
                if materialtype.isdisjoint(allow):
                    # There's nothing in common here.
                    continue
            # Group filter
            if group is not None:
                # Make sure one of our groups is allowed and none are restricted
                group = getSet(group)
                allow = getSet(getList(m, "group"))
                restrict = getSet(getList(m, "groupconflict"))
                if not allow.issubset(group) or not group.isdisjoint(restrict):
                    # We're either not on the list, or rejected.
                    continue
            # Properties filter
            if properties is not None:
                # Make sure we have the required properties and none are restricted
                properties = getSet(properties)
                allow = getSet(getList(m, "properties"))
                restrict = getSet(getList(m, "propertyconflict"))
                if not allow.issubset(properties):
                    # Material requires other properties.
                    continue
                if not restrict.isdisjoint(properties):
                    # One or more of our properties are forbidden
                    continue
            # Maximum bonus filter
            if maxbonus is not None:
                if data.has_option(m, "bonus"):
                    if data[m].getint("bonus") > maxbonus:
                        continue
            # End of filters.
            # Add the item to the approved list.
            flist.append(m)
            # Grab the item's weight and append that.
            if data.has_option(m, "chance"):
                wlist.append(data[m].getfloat("chance"))
            else:
                # Default to a chance of 1.
                wlist.append(1)
        if len(flist) == 0:
            logging.debug("Filters eliminated all materials.")
            return None
        mat = random.choices(flist, wlist)[0] # It returns a list. Of one thing.
        return mat

class Effect(Modifier):
    def __init__(self, category=None, affix=None, subtype=None, itemid=None,
        damagetype=None, materialtype=None, group=None, properties=None,
        materialid=None, effectids=None, maxbonus=None, minbonus=None,
        effectid=None):
        self.setup()
        # Grab a random material fitting the filters.
        self.id = self.getEffect(category, affix, subtype, itemid, damagetype,
        materialtype, group, properties, materialid, effectids, maxbonus,
        minbonus, effectid)
        # Set ourselves appropriately
        self.setValues()
        self.getAttunement()
        self.prefix = self.replaceRandom(self.prefix)
        self.suffix = self.replaceRandom(self.suffix)
    
    def setValues(self):
        if self.id is not None:
            if data.has_option(self.id, "prefix"):
                self.prefix = data[self.id]["prefix"]
            if data.has_option(self.id, "suffix"):
                self.suffix = data[self.id]["suffix"]
            if data.has_option(self.id, "bonus"):
                self.bonus = data[self.id].getint("bonus")
            self.modifiers = self.getModifiers() # Dict for effects.
            self.randomlists = self.getRandomLists()
            self.choice = self.chooseRandom()
        else:
            # prefix, suffix, bonus, description, modifiers are all set
            self.randomlists = {}
            self.choice = None
        
    def getRandoms(self):
        # Returns the choices from the random lists.
        choices = {}
        for r in self.randomlists:
            choices[r] = r[self.choice]
        return choices
    
    def getEffect(self, category, affix, subtype, itemid, damagetype, 
        materialtype, group, properties, materialid, effectids, maxbonus,
        minbonus, effectid):
        # Functions similar to the materials.
        # If our filters return nothing, we return None.
        # If a filter is passed as "None" then it is ignored.
        mlist = getCategoryList("effect", affix) # If affix is None it's fine.
        # Now check our effectid that we've been given.
        if effectid is not None:
            if effectid in mlist:
                return effectid
            else:
                # Let us know that the effect failed.
                return None
        flist = [] # Filtered list. Suitable materials get put here.
        wlist = [] # Chance weights
        for m in mlist:
            # Add filters here.
            # Category filter.
            if category is not None:
                # We have a category of item to pick an effect for.
                # Grab our own list.
                allow = getSet(getList(m, "itemtype"))
                if category not in allow and len(allow) > 0:
                    # Nope, our category doesn't match.
                    continue
            # Subtype filter
            if subtype is not None:
                # We have a subtype filter to match.
                # We only need to worry about matching one of them.
                subtype = getSet(subtype)
                allow = getSet(getList(m, "itemsubtype"))
                restrict = getSet(getList(m, "subtypeconflict"))
                if not subtype.isdisjoint(restrict):
                    # One or more of our subtypes is prohibited.
                    continue
                if len(allow) > 0 and allow.isdisjoint(subtype):
                    # Our effect only applies to certain subtypes, and this
                    # is not one of them.
                    continue
            # Item ID filter.
            if itemid is not None:
                # Sometimes, effects disallow specific items.
                restrict = getList(m, "itemconflict")
                if itemid in restrict:
                    continue
            # Damagetype filter.
            if damagetype is not None:
                # Can be both required or restricted.
                allow = getList(m, "damagetype")
                restrict = getList(m, "damagetypeconflict")
                if damagetype not in allow and len(allow) > 0:
                    # Sorry, we don't fit.
                    continue
                if damagetype in restrict:
                    # We're not welcome.
                    continue
            # Material ID filter
            if materialid is not None:
                # Sometimes we don't want to work on a specific material
                restrict = getList(m, "materialconflict")
                if materialid in restrict and len(restrict) > 0:
                    # Like now.
                    continue
            # Materialtype filter
            if materialtype is not None:
                # Effects treat materialtypes differently than, well, materials.
                # It's the materialtype of the material that is passed.
                materialtype = getSet(materialtype)
                allow = getSet(getList(m, "materialtype"))
                restrict = getSet(getList(m, "materialtypeconflict"))
                if not materialtype.isdisjoint(restrict):
                    # There's an overlap with our restrictions. Drat!
                    continue
                # For allowing, there only needs to be an overlap.
                if allow.isdisjoint(materialtype) and len(allow) > 0:
                    # But there is none.
                    continue
            # Group filter
            if group is not None:
                # Make sure one of our groups is allowed and none are restricted
                group = getSet(group)
                allow = getSet(getList(m, "group"))
                restrict = getSet(getList(m, "groupconflict"))
                if not allow.issubset(group) or not group.isdisjoint(restrict):
                    # We're either not on the list, or rejected.
                    continue
            # Properties filter
            if properties is not None:
                # Make sure we have the required properties and none are restricted
                properties = getSet(properties)
                allow = getSet(getList(m, "properties"))
                restrict = getSet(getList(m, "propertyconflict"))
                if not allow.issubset(properties):
                    # Material requires other properties.
                    continue
                if not restrict.isdisjoint(properties):
                    # One or more of our properties are forbidden
                    continue
            if maxbonus is not None:
                if data.has_option(m, "bonus"):
                    if data[m].getint("bonus") > maxbonus:
                        continue
            # And for minimum bonus.
            if minbonus is not None:
                if data.has_option(m, "bonus"):
                    if data[m].getint("bonus") < minbonus:
                        continue
                elif minbonus > 0:
                    continue
            # Effect and attunement filter.
            # This one is a little complicated. effectids is a list of effects
            # already on the item.
            if effectids is not None:
                effectids = getSet(effectids)
                restrict = getSet(getList(m, "effectconflict"))
                if not restrict.isdisjoint(effectids):
                    # One of our existing effects conflicts with this effect.
                    continue
                # Now we need to get the list of effects our existing effects
                # have restricted.
                restrict = []
                for e in effectids:
                    restrict += getList(e, "effectconflict")
                if m in restrict:
                    # One of them restricts this effect.
                    continue
                if m in effectids:
                    # We already have this effect.
                    continue
                # Now we do attunement
                # For this we also want the effectids.
                if data.has_option(m, "attunement"):
                    # If it doesn't have this, we're fine.
                    restrict = []
                    for e in effectids:
                        restrict.append(checkAttunement(e, m))
                    if False in restrict:
                        # One of them can't attune.
                        continue      
            # Now the filter on the effect itself.
            if data.has_option(m, "requireaffix"):
                if effectids is None:
                    # We were given no effects so cannot guarantee things.
                    continue
                # However, if we have effectids, they'll already be in a list.
                # Useful.
                elif len(effectids) == 0:
                    # No effects generated at this time. So, sorry.
                    continue
            # End of filters.
            # Add the item to the approved list.
            flist.append(m)
            # Grab the item's weight and append that.
            if data.has_option(m, "chance"):
                wlist.append(data[m].getfloat("chance"))
            else:
                # Default to a chance of 1.
                wlist.append(1)
        if len(flist) == 0:
            logging.debug("Filters eliminated all effects.")
            return None
        effect = random.choices(flist, wlist)[0]
        return effect

# This is a basic "Item" class. There are more specific ones for
# things like weapons, shields, etc.
class Item:
    def __init__(self, rarity=None):
        # Clean up the rarities.
        rarities = ["common", "uncommon", "rare", "veryrare", "legendary"]
        if rarity is None:
            # Assign a random rarity.
            rarity = random.choice(rarities)
        # Lowercase and remove spaces (Such as for Very Rare).
        rarity = rarity.lower().replace(" ","")
        if rarity not in rarities:
            logging.error("Invalid rarity %s given." % rarity)
            raise ValueError("Item rarity must be common, uncommon, rare, very rare, or legendary.")
        self.rarity = rarity
        # Grab the maximum bonus an item can have.
        self.maxbonus = cfg["Rarity"].getint(self.rarity)
        self.maxenhancement = len(getList("Effects", "enhanceweights", cfg))
        self.maxprefix = cfg["Effects"].getint("maxprefix")
        self.maxsuffix = cfg["Effects"].getint("maxsuffix")
        # And the maximum number of times we can try for a given rarity before
        # giving up and accepting our lower rarity item.
        self.maxtries = cfg["Rarity"].getint("maxtries")
        self.itemname = ""
        # Total enhancement bonus. Only for weapons, armors, and shields, but
        # hey. Is what it is.
        self.enhancement = 0
        # And the other properties. Weight is the only common thing.
        self.weight = 0
        # These will be assigned by the child class.
        # Keep them around just in case something tries to reference them.
        self.charges = 0
        self.wondrous = False
        self.recharge = None
        self.rechargemod = None
        self.destroyonempty = False
        self.category = None
        self.material = None
        self.group = None
        self.properties = []
        self.subtype = None
        self.quantity = None
        self.subtype = None
        self.damage = None
        self.damagetype = None
        self.damagevers = None
        self.shortrange = None
        self.longrange = None
        self.info = ""
        self.materialtype = [] # If this is "None" then it'll treat it as "Any"
                               # instead of, well. "None"
        self.ac = None
        self.maxdexterity = None
        self.minstrength = None
        self.stealthpenalty = None
        self.randomlists = {}
        self.choice = None
        self.prefixes = []
        self.suffixes = []
        self.attunement = None
        self.spell = None # For the spell we may add.
        self.name = "item" # This will become the item's name, eventually.
        self.source = "Generated Item" # Used to tell between these and "static" items.
    
    def getRarity(self):
        # Returns the rarity based on the item's current bonus.
        bonus = self.getBonus()
        common = cfg["Rarity"].getint("common")
        uncommon = cfg["Rarity"].getint("uncommon")
        rare = cfg["Rarity"].getint("rare")
        veryrare = cfg["Rarity"].getint("veryrare")
        legendary = cfg["Rarity"].getint("legendary")
        if bonus >= legendary:
            return "legendary"
        elif bonus >= veryrare:
            return "veryrare"
        elif bonus >= rare:
            return "rare"
        elif bonus >= uncommon:
            return "uncommon"
        else:
            return "common"
    
    def getRandomLists(self):
        # Retrieves the random lists
        lists = {}
        for i in range(0,10):
            if data.has_option(self.id, "randomlist%d" % i):
                lists["R%d" % i] = getList(self.id, "randomlist%d" % i)
        return lists
        
    def chooseRandom(self):
        # Gets a random number, from 0 to the minimum length of one of the lists.
        # They SHOULD all be the same length, but. Well. This way it still works.
        length = -1
        for r in self.randomlists:
            if len(self.randomlists[r]) < length or length == -1:
                length = len(self.randomlists[r])
        if length > 0:
            return random.randint(0,length-1)
        else:
            return None
            
    def replaceRandom(self, workstr):
        if workstr is None:
            # Just in case.
            return ""
        elif workstr == "":
            # Nothing to replace here.
            return ""
        if self.choice is None:
            # No randoms to replace.
            return workstr
        # Alright, we've weeded out stuff we don't have to work on.
        # So let's get to work.
        for r in range(0, 10):
            if "R%d" % r not in self.randomlists:
            # This random list does not exist.
                continue
            insert = self.randomlists["R%d" % r][self.choice]
            workstr = workstr.replace("@R%d" % r, insert).replace("@r%d" % r, insert)
        return workstr
    
    def parseModifiers(self, effect):
        # Parses the pre-programmed modifier list of the given object.
        # Mostly this is applying the modifiers to the parent item, but they
        # can also affect the modifier as well.
        modifiers = []
        cat = self.category
        if cat not in ["weapon", "armor", "shield", "ammunition"]:
            cat = "item" # Weapon, armors, and shields have their own modifiers.
        for m in effect.modifiers:
            if m == cat:
                for mod in effect.modifiers[cat]:
                    modifiers.append(mod)
        for mod in modifiers:
            # OK, this one will be a long one.
            # Let's start with the universal modifier of weight.
            if self.weight > 0 and mod[0] == "changeweight":
                # Changeweight. Multiplies weight by a given amount.
                if len(mod) > 1:
                    logging.debug("Weight modified by %s" % mod[1])
                    self.weight = round(self.weight * float(mod[1]), 2)
            # Give some charges.
            if mod[0] == "charges" and len(mod) > 1:
                # We take the *greatest* number of charges/
                if self.charges < int(mod[1]):
                    self.charges = int(mod[1])
                if "charges" not in self.properties:
                    self.properties.append("charges")
            # Modify charges.
            if mod[0] == "modifycharges" and len(mod) > 1:
                # Adjust the number of charges. But only if we HAVE charges.
                if self.charges > 0:
                    self.charges += int(mod[1])
                # But we can't go below 1 charge.
                    if self.charges < 1:
                        self.charges = 1
            # Set a recharge. It's split into dice and bonus, and will use the
            # larger of both of them. That is, if one effect is 1d3+1 and the
            # other is 1d6-1, you'll end up with 1d6+1
            if mod[0] == "recharge" and len(mod) > 1:
                if self.recharge is None:
                    self.recharge = mod[1]
                else:
                    self.recharge = compareDice(self.recharge, mod[1])
                if len(mod) > 2:
                    if self.rechargemod is None:
                        self.rechargemod = int(mod[2])
                    else:
                        self.rechargemod = max(self.rechargemod, int(mod[2]))
            # A lot of wands and staffs (And rods? haven't got that far)
            # have a chance to be destroyed when you use the last charge.
            # This adds the property that is checked when getting
            # the description.
            if mod[0] == "destroyonempty":
                self.destroyonempty = True
            # Generate ourselves a random spell.
            if mod[0][:-1] == "randspell" and len(mod) > 2:
                spellnum = int(mod[0][-1:])
                # Find the level boundaries and assign them appropriately.
                lvl = [int(mod[1]), int(mod[2])]
                lvl.sort()
                minlvl = lvl[0]
                maxlvl = lvl[1]
                spclass = None
                spschool = None
                if len(mod) > 3:
                    var = mod[3].split(":")
                    for v in var:
                        if v in classes:
                            spclass = var
                            # We have a class match. Don't continue.
                            break
                        elif v in spellschools:
                            spschool = var
                            break
                    if len(mod) > 4:
                        var = mod[4].split(":")
                        for v in var:
                            if v in classes:
                                spclass = var
                                break
                            elif v in spellschools:
                                spchool = var
                                break
                # Now we have our four variables.
                effect.spells[spellnum] = Spell(school=spschool, minlevel=minlvl,
                            maxlevel=maxlvl, chclass=spclass, itemtype=self.category)
                effect.updateText()
            # Ammunition effects
            if self.category in ["ammunition","weapon"] and self.quantity is not None:
                # Simple. Sets the quantity to an amount.
                if mod[0] == "setquantity" and len(mod) > 1:
                    self.quantity = int(mod[1])
                if mod[0] == "modifyquantity" and len(mod) > 1:
                    self.quantity = round(self.quantity * float(mod[1]))
                if mod[0] == "addquantity" and len(mod) > 1:
                    self.quantity = self.quantity + int(mod[1])
                # And now make sure we have our minimum quantity.
                if self.quantity < 2:
                    self.quantity = 2
            # Now for weapon ones.
            if self.category == "weapon":
                # Change the damage type. Pretty simple.
                if mod[0] == "changedmgtype" and len(mod) > 1:
                    self.damagetype = mod[1]
                # Add properties. Versatile and ranged stuff add complexity.
                if mod[0] == "addproperty" and len(mod) > 1:
                    if mod[1] not in self.properties:
                        if mod[1] == "versatile":
                            if self.damagevers is None and len(mod) > 2:
                                logging.debug("%s property added." % mod[1])
                                self.properties.append(mod[1])
                                self.damagevers = mod[2]
                        elif mod[0] in ["ammunition", "thrown"]:
                            if self.shortrange is None:
                                logging.debug("%s property added." % mod[1])
                                self.properties.append(mod[1])
                                self.shortrange = int(mod[2])
                                if len(mod) > 3:
                                    self.longrange = int(mod[3])
                                else:
                                    self.longrange = int(mod[2])
                        else:
                            logging.debug("%s property added." % mod[1])
                            self.properties.append(mod[1])
                # Remove a property. Easy enough if we have it.
                if mod[0] == "removeproperty" and len(mod) > 1:
                    if mod[1] in self.properties:
                        logging.debug("%s property removed." % mod[1])
                        self.properties.remove(mod[1])
                if mod[0] == "addpropertyif" and len(mod) > 3:
                    if mod[1] not in self.properties:
                        check = mod[3].lower()
                        if check == "false" or check == "0":
                            check = False
                        else:
                            check = True
                        present = mod[2] in self.properties
                        if present == check:
                            if mod[1] not in ["versatile","ammunition","thrown"]:
                                logging.debug("%s property added." % mod[1])
                                self.properties.append(mod[1])
                            elif mod[1] == "versatile" and len(mod) > 4:
                                logging.debug("%s property added." % mod[1])
                                self.properties.append(mod[1])
                                self.damagevers = mod[4]
                            elif mod[1] in ["ammunition","thrown"] and len(mod) > 4:
                                logging.debug("%s property added." % mod[1])
                                self.properties.append(mod[1])
                                self.shortrange = int(mod[4])
                                if len(mod) > 5:
                                    self.longrange = int(mod[5])
                                else:
                                    self.longrange = int(mod[4])
                # Range multiplying
                if mod[0] == "multiplyrange1" and len(mod) > 1 and self.shortrange is not None:
                    if self.shortrange > 0:
                        logging.debug("Standard range multiplied by %s" % mod[1])
                        self.shortrange = round(self.shortrange * float(mod[1]), -1)
                if mod[0] == "multiplyrange2" and len(mod) > 1 and self.longrange is not None:
                    if self.longrange > 0:
                        logging.debug("Long range multiplied by %s" % mod[1])
                        self.longrange = round(self.longrange * float(mod[1]), -1)
                # Range adding.
                if mod[0] == "addrange1" and len(mod) > 1 and self.shortrange is not None:
                    if self.shortrange > 0:
                        logging.debug("Adding %s to standard range" % mod[1])
                        self.shortrange = self.shortrange + int(mod[1])
                if mod[0] == "addrange2" and len(mod) > 1 and self.longrange is not None:
                    if self.longrange > 0:
                        logging.debug("Adding %s to long range" % mod[1])
                        self.longrange = self.longrange + int(mod[1])
                # Changing the damage dice.
                if self.damage is not None:
                    if mod[0] == "changedmgdice" and len(mod) > 1:
                        logging.debug("Changing damage dice by %s steps." % mod[1])
                        change = int(mod[1])
                        if change < 0:
                            dir = False
                        else:
                            dir = True
                        change = abs(change)
                        for r in range(0, change):
                            self.damage = changeDiceSize(self.damage, dir)
                if self.damagevers is not None:
                    if mod[0] == "changeversatile" and len(mod) > 1:
                        logging.debug("Changing Versatile damage dice by %s steps." % mod[1])
                        change = int(mod[1])
                        if change < 0:
                            dir = False
                        else:
                            dir = True
                        change = abs(change)
                        for r in range(0, change):
                            self.damagevers = changeDiceSize(self.damagevers, dir)
            # That's it for weapons! Now on to armor (And shields)
            if self.category in ["armor","shield"]:
            # There's one that overlaps here.
                if mod[0] == "changeac" and len(mod) > 1:
                    logging.debug("Changing AC by %s" % mod[1])
                    self.ac += int(mod[1])
            # Now for the armor ones.
            if self.category == "armor":
                # Add (or remove) the Stealth disadvantage.
                if mod[0] == "stealthpenalty" and len(mod) > 1:
                    logging.debug("Adjusting Stealth Penalty to %s" % mod[1])
                    self.stealthpenalty = bool(mod[1])
                    if not self.stealthpenalty and "stealthpenalty" in self.properties:
                        self.properties.remove("stealthpenalty")
                    elif self.stealthpenalty and "stealthpenalty" not in self.properties:
                        self.properties.append("stealthpenalty")
                # Set the strength requirement to an amount. Setting to 0 removes.
                if mod[0] == "setstrength" and len(mod) > 1:
                    logging.debug("Setting Strength requirement to %s" % mod[1])
                    self.minstrength = int(mod[1])
                    if self.minstrength > 0 and "strengthreq" not in self.properties:
                        self.properties.append("strengthreq")
                    elif self.minstrength <= 0 and "strengthreq" in self.properties:
                        self.properties.remove("strengthreq")
                # Adjusts the Strength requirement, if it exists.
                if mod[0] == "adjstrength" and len(mod) > 1:
                    logging.debug("Adjusting Strength requirement by %s" % mod[1])
                    if self.minstrength >= 1:
                        self.minstrength += int(mod[1])
                        # No need for setting properties here.
                # Sets the maximum Dexterity.
                if mod[0] == "setdexmax" and len(mod) > 1:
                    logging.debug("Setting maximum dexterity to %s" % mod[1])
                    self.maxdexterity = int(mod[1])
                    if self.maxdexterity == 0:
                        self.maxdexterity = False
                        if "limitdexterity" in self.properties:
                            self.properties.remove("limitdexterity")
                        if "nodexterity" not in self.properties:
                            self.properties.append("nodexterity")
                    if self.maxdexterity == -1:
                        self.maxdexterity = True
                        if "limitdexterity" in self.properties:
                            self.properties.remove("limitdexterity")
                        if "nodexterity" in self.properties:
                            self.properties.remove("nodexterity")
                    else:
                        if "limitdexterity" not in self.properties:
                            self.properties.append("limitdexterity")
                        if "nodexterity" in self.properties:
                            self.properties.remove("nodexterity")
                # And adjust the maximum dexterity.
                if mod[0] == "adjdexmax" and len(mod) > 1:
                    logging.debug("Adjusting maximum dexterity by %s" % mod[1])
                    if type(self.maxdexterity) == int:
                        self.maxdexterity += int(mod[1])
                        # Also no need for setting properties here.
        return True
    
    def getSpell(self, level, minlevel=None, maxlevel=None, chclass=None):
        # Finds a spellwith the given restrictions.
        self.spell = Spell(level=level, minlevel=minlevel, maxlevel=maxlevel,
                        chclass=chclass)
        if self.spell.id is None:
            return False
        return True
        
    
    def getMaterial(self):
        # This as a function lets us regenerate a material without re-doing
        # all of the other things.
        # We'll automatically calculate our budget.
        budget = self.maxbonus - self.getBonus() # Our max bonus minus our current.
        if hasattr(self.material, "bonus"):
            # We already have a material, so take its current bonus too.
            budget += self.material.bonus
        # Get our new material!
        newmat = Material(category=self.category, subtype=self.subtype,
            itemid=self.id, damagetype=self.damagetype, group=self.group,
            materialtype=self.materialtype, properties=self.properties,
            maxbonus=budget)
        self.material = newmat
        self.parseModifiers(self.material)
        logging.debug("Selected %s" % self.material.name)
        return True
    
    def getEffect(self, affix=None, range=None):
        # Generates a random effect
        effects = [] # Our existing effects
        for e in self.prefixes + self.suffixes:
            effects.append(e.id)
        budget = self.maxbonus - self.getBonus() # As above, but no replacement.
        # Go get it!
        if type(range) is int:
            # We have a range for our budget.
            range = abs(range)
            minbudget = max(0, budget-range)
        else:
            minbudget = range
        neweffect = Effect(category=self.category, affix=affix, 
        subtype=self.subtype, itemid=self.id, damagetype=self.damagetype,
        materialtype=self.material.materialtype, effectids=effects,
        materialid=self.material.id, group=self.group,
        properties=self.properties, maxbonus=budget, minbonus=minbudget)
        self.parseModifiers(neweffect)
        logging.debug("Selected %s" % neweffect.id)
        return neweffect
    
    def getEnhancement(self):
        # Returns a generated enhancement bonus of at least +1
        # Unless the budget is 0, in which case. It returns 0.
        # But if we're not armor, a weapon, or a shield, it should return 0 too.
        if self.category not in ["armor", "weapon", "shield", "ammunition",
                                "wand", "staff"]:
            return 0
        budget = self.maxbonus - self.getBonus()
        if budget == 0:
            return 0
        weights = getList("Effects", "enhanceweights", cfg)
        weights = list(map(int, weights)) # We need INTS!
        enh = random.choices(range(1,len(weights)+1), weights)[0]
        while enh > budget:
            enh = random.choices(range(1,len(weights)+1), weights)[0]
        return enh
    
    def fillEnhancement(self):
        # Attempts to fill the remaining bonus with enhancement.
        # Ignore for non-weapon/armor
        if self.category not in ["armor", "weapon", "shield", "ammunition",
                                "wand", "staff"]:
            return 0
        # Adds in our current enhancement just to be sure.
        budget = self.maxbonus - self.getBonus() + self.enhancement
        if budget == 0:
            # No need for anything fancy.
            return 0
        elif budget <= self.maxenhancement:
            # We can fill it.
            return budget
        else:
            # Still too big. But hey, we tried.
            return self.maxenhancement
    
    def getGenerateList(self, length=10):
        # Returns a list of the given length of enhancement, prefix, and
        # suffix. The generator will cycle through it and attempt to generate
        # an effect of the appropriate type.
        genlist = []
        enh = max(cfg["Effects"].getint("enhancechance"), 1)
        pre = max(cfg["Effects"].getint("prefixchance"), 1)
        suf = max(cfg["Effects"].getint("suffixchance"), 1)
        wlist = [enh, pre, suf]
        items = ["enhancement", "prefix", "suffix"]
        lastchoice = None
        while length > 0:
            choice = random.choices(items, wlist)[0]
            while choice == lastchoice:
                choice = random.choices(items, wlist)[0]
            genlist.append(choice)
            lastchoice = choice
            length -= 1
        return genlist
    
    def redoEffects(self):
        self.prefixes = []
        self.suffixes = []
        bonus = self.addAllEffects()
        return bonus
    
    def addAllEffects(self):
        # Automatically generates our effects and enhancements.
        order = self.getGenerateList() # The order in which we do them.
        enhance = True # Are we still generating enhancements?
        prefix = True # Are we still generating prefixes?
        suffix = True # And same for suffixes
        # Now check if we can get effects. If not, just dill enhancement.
        maxeffects = cfg["Effects"].getint("max%s" % self.rarity)
        noeffects = cfg["Effects"].getint("noeffect%s" % self.rarity)
        if noeffects == 0:
            noeffects = False
        elif self.category not in ["armor","weapon","shield","ammunition"]:
            # Only armor, ammo, weapons, and shields have enhancements.
            # Technically, wands and staffs do too, but those having less
            # frequent enhancements is a good thing.
            noeffects = False
        else:
            echance = random.randint(1,100)
            if echance < noeffects:
                # This item is "just" going to be a +X weapon.
                noeffects = True 
            else:
                noeffects = False
        if maxeffects < 1:
            noeffects = True
        if noeffects:
            # No effects. Get that maximum enhancement bonus!
            self.enhancement = self.fillEnhancement()
            logging.debug("Enhancement: +%d" % self.enhancement)
            return self.maxbonus - self.getBonus()
        for e in order:
            if e == "enhancement" and enhance:
                # Generate an enhancement, because we haven't yet.
                self.enhancement = self.getEnhancement()
                if self.enhancement > 0:
                    self.properties.append("enhancement")
                enhance = False # We only do this once.
            elif e == "prefix" and prefix:
                # Generate an enhancement, because we still have room.
                x = self.addPrefix()
                if not x:
                    # We failed, which means we can't add more.
                    prefix = False
                if len(self.prefixes) >= self.maxprefix:
                    # Our prefixes are full. Sorry.
                    prefix = False
            elif e == "suffix" and suffix:
                # Same as prefixes.
                x = self.addSuffix()
                if not x:
                    suffix = False
                if len(self.suffixes) >= self.maxsuffix:
                    suffix = False
            if self.getBonus() >= self.maxbonus:
                # No more space available!
                enhance = False
                prefix = False
                suffix = False
        if self.getBonus() < self.maxbonus:
            # We still have bonus spare. Fill it up if we can.
            self.enhancement = self.fillEnhancement()
            if self.enhancement > 0:
                self.properties.append("enhancement")
        logging.debug("Enhancement: +%d" % self.enhancement)
        return self.getBonus() # Give us how much bonus is left.
    
    def addPrefix(self):
        # Generates and adds a prefix.
        if len(self.prefixes) >= self.maxprefix:
            # We can't add anymore!
            return False
        # Get our budget.
        if self.wondrous:
            # We want larger effects on our wondrous items.
            prefix = self.getEffect(affix="Prefix", range=2)
        else:
            prefix = self.getEffect(affix="Prefix")
        if prefix.id is None:
            # No prefix available.
            return False
        self.prefixes.append(prefix)
        return True
    
    def addSuffix(self):
        # Generates and adds a prefix.
        if len(self.suffixes) >= self.maxsuffix:
            # We can't add anymore!
            return False
        # Get our budget.
        if self.wondrous:
            suffix = self.getEffect(affix="Suffix", range=2)
        else:
            suffix = self.getEffect(affix="Suffix")
        if suffix.id is None:
            # No prefix available.
            return False
        self.suffixes.append(suffix)
        return True
    
    def getBonus(self):
        item = self.enhancement
        if self.material is not None:
            material = self.material.bonus
        else:
            material = 0
        effects = 0
        for effect in self.prefixes + self.suffixes:
            effects += effect.bonus
        return item + material + effects
    
    def getName(self):
        # Gets the prefixes, suffixes, enhancement, materials, and item
        # Enhancement bonus
        # First, enhancement bonus.
        if self.enhancement > 0:
            # Add our enhancement.
            enhstr = "+%d " % self.enhancement
        else:
            enhstr = ""
        # Prefixes
        prelst = []
        if len(self.prefixes) > 0:
            for p in self.prefixes:
                prelst.append(p.prefix)
        prelst = " ".join(prelst)
        # Suffixes
        suflst = []
        if len(self.suffixes) > 0:
            for s in self.suffixes:
                suflst.append(s.suffix)
        suflst = " and ".join(suflst)
        # Quantity (For ammunition):
        if self.quantity is not None:
            qtystr = str(self.quantity)
        else:
            qtystr = ""
        # We have our info, now let's add it together.
        if "@material" in self.itemname:
            name = [qtystr, enhstr, prelst, self.itemname, suflst]
        else:
            name = [qtystr, enhstr, prelst, self.material.name, self.itemname, suflst]
        name = " ".join(name)
        #name = self.replaceVars(name)
        # And some cleanup.
        # First, any double spaces.
        while "  " in name:
            name = name.replace("  "," ")
        # Now, leading and trailing spaces.
        name = name.strip()
        # And replace any variables.
        name = self.replaceVars(name)
        return name
    
    def replaceVars(self, workstr, lowercase=False):
        # Parses the provided string for existing variables.
        if "@" not in workstr:
            # No variables found.
            return workstr
        # Standard variables.
        workstr = workstr.replace("@enh", str(self.enhancement))
        if self.spell is not None:
            spellname = self.spell.name
        else:
            spellname = ""
        if lowercase:
            workstr = workstr.replace("@item", self.itemname.lower())
            workstr = workstr.replace("@material", str(self.material.name.lower()))
            workstr = workstr.replace("@spell", spellname.lower())
        else:
            workstr = workstr.replace("@item", self.itemname)
            workstr = workstr.replace("@material", str(self.material.name))
            workstr = workstr.replace("@spell", spellname)
        workstr = workstr.replace("@category", self.category)
        workstr = workstr.replace("@weight", str(self.weight))
        workstr = workstr.replace("@charges", str(self.charges))
        rechargestr = str(self.recharge)
        if self.rechargemod is not None:
            if self.rechargemod > 0:
                rechargestr += "+%d" % self.rechargemod
            elif self.rechargemod < 0:
                rechargestr += str(self.rechargemod)
        workstr = workstr.replace("@recharge", rechargestr)
        if self.category == "weapon":
            # Weapon-only replacements.
            workstr = workstr.replace("@dmg", str(self.damage))
            workstr = workstr.replace("@dmgtype", str(self.damagetype))
            workstr = workstr.replace("@vdmg", str(self.damagevers))
        if self.category == "armor" or self.category == "shield":
            # Armor and Shield replaces
            workstr = workstr.replace("@ac", str(self.ac + self.enhancement))
            workstr = workstr.replace("@rawac", str(self.ac))
        if self.category == "armor":
            # Armor only replaces
            workstr = workstr.replace("@reqstr", str(self.minstrength))
            if self.maxdexterity == True:
                workstr = workstr.replace("@maxdex", "Dex Modifier")
            else:
                workstr = workstr.replace("@maxdex", "Dex Modifier (max %s)" % self.maxdexterity)
        workstr = workstr.replace("\\n", "\n") # Any of these need to be replaced, might as well do it here.
        return workstr
    
    def getDescription(self):
        # Returns the description from the effects and material.
        desc = []
        # We're an item, so don't bother checking for other descriptions.
        # Just take ours and apply the random replacer.
        if data.has_option(self.id, self.category + "description"):
            selfdesc = data[self.id][self.category + "description"]
            selfdesc = self.replaceRandom(selfdesc)
            desc.append(selfdesc)
        if self.enhancement > 0:
            desc.append(cfg["Descriptions"]["%senhdescription" % self.category])
        if self.charges > 0:
            if self.charges == 1:
                chargestr = cfg["Descriptions"]["onechargedescription"]
            else:
                chargestr = cfg["Descriptions"]["chargedescription"]
            if self.recharge is not None:
                chargestr += " %s" % cfg["Descriptions"]["rechargedescription"]
            if self.destroyonempty:
                chargestr += " %s" % cfg["Descriptions"]["destroyonemptydescription"]
            desc.append(chargestr)
        if self.material.id is not None:
            matdes = self.material.getDescription(self.category)
            if matdes is not None:
                desc.append(matdes)
        for p in self.prefixes:
            predes = p.getDescription(self.category)
            if predes is not None:
                desc.append(predes)
        for s in self.suffixes:
            sufdes = s.getDescription(self.category)
            if sufdes is not None:
                desc.append(sufdes)
        # Put them all in one string.
        desc = "\n".join(desc)
        # Replace any variables.
        desc = self.replaceVars(desc, lowercase=True)
        # Aaaand back to a list.
        #desc = desc.split("\\")
        return desc
    
    def getInfo(self):
        # Takes our item type, our sub-type (If applicable), rarity, and
        # attunement and puts them into a single string. (A stringle?)
        # First, the item type. The *official* types are: Armor, Potion,
        # Rings, Rods, Scrolls, Staffs, Wands, Weapons, or Wondrous Item.
        desc = ""
        if self.category in ("weapon", "armor", "ammunition"):
            desc += "%s (%s), " % (self.category, self.itemname.lower())
        elif self.category in ("potion", "ring", "rod", "scroll", "staff", "wand"):
            desc += "%s, " % self.category
        elif self.category == "shield":
            # Shields are technically armor, according to the game.
            desc += "Armor (shield), "
        else:
            desc += "wondrous item (%s), " % self.category
        #Now, add our rarity.
        if self.rarity == "veryrare":
            desc += "very rare"
        else:
            desc += self.rarity
        # Attunement.
        at = self.getAttuneDesc()
        if at != "":
            desc += " (%s)" % at
        # And fix the capitalization. DMG only has first word capitalized, and
        # that's easy to replicate.
        desc = self.replaceVars(desc)
        desc = desc.capitalize()
        return desc
    
    def getAttuneDesc(self):
        # Takes our attunement and turns it into a string.
        if self.attunement is None or self.attunement is False:
            # Either way, no attunement.
            return ""
        elif self.attunement is True:
            # Generic attunement ahoy!
            return "requires attunement"
        elif type(self.attunement) is str:
            # A description!
            return "requires attunement by " + self.attunement
        elif type(self.attunement) is not list:
            # Hmm, something error'd here.
            # Assume no attunement.
            return ""
        # Now we know we have a list.
        astr = "requires attunement by a "
        if len(self.attunement) == 1:
            astr += self.attunement[0]
        elif len(self.attunement) == 2:
            astr += " or ".join(self.attunement)
        else:
            astr += ", ".join(self.attunement[:-1])
            astr += ", or " + self.attunement[-1]
        return astr
        
    
    def getAttunement(self):
        # Assigns the appropriate attunement.
        attune = False
        alist = []
        for e in self.prefixes + self.suffixes + [self.material]:
            # For each effect, figure out the attunement.
            if e.attunement is not None:
                if e.attunement is True:
                    attune = True
                elif type(e.attunement) is str:
                    # A description. We should only ever have one of these.
                    # Or multiples, if they're... identical so it doesn't matter.
                    # It'll be sorted later.
                    attune = True
                    alist += [e.attunement]
                elif type(e.attunement) is list:
                    # Combine the lists. We'll sort out duplicates later.
                    attune = True
                    alist += e.attunement
        # Now we have our list of attunements. Time to return.
        if not attune:
            # No attunement required!
            return attune
        elif attune:
            # Hey, we have attunement!
            if len(alist) == 0 :
                # no requirements.
                return True
            else:
                # Turn it into a set. This returns it as uniques.
                # But we want to sort it, so back into a list.
                alist = list(set(alist))
                alist.sort()
                # We'll deal with stringifying it later.
                return alist
                
    
# Now lets make a weapon class.
class Weapon(Item):
    def __init__(self, rarity=None, group=None, weapontype=None,
        damagetype=None, properties=None, materialtype=None, weapon=None,
        forcerarity=True):
        # First, the item bits.
        Item.__init__(self, rarity)
        self.category = "weapon" # This might be handy.
        self.id = self.getWeapon(group, weapontype, damagetype, properties,
            materialtype, weapon)
        self.getWeaponInfo() # Pull our info of the weapon.
        logging.debug("Selected %s" % self.itemname)
        self.getMaterial() # Assign ourselves a material.
        bonus = self.addAllEffects() # Get us some effects!
        if bonus < self.maxbonus and forcerarity:
            tries = 0
            while bonus < self.maxbonus:
                bonus = self.redoEffects()
                tries += 1
                if tries >= self.maxtries:
                    break
        if bonus < self.maxbonus:
            self.rarity = self.getRarity()
        self.attunement = self.getAttunement()
        self.name = self.getName()
        self.info = self.getInfo()
        self.description = self.getDescription()
        
    def getWeapon(self, group, weapontype, damagetype, properties, materialtype,
                weapon):
        # Now pick our weapon. First get our list of weapons.
        weplist = getCategoryList("weapon")
        if weapon is not None:
            # Oooh, we have one picked out for us!
            if type(weapon) is not str:
                # Something wrong here.
                logging.error("Invalid argument %s for weapon override. Ignoring." % str(weapon))
            # OK, so now we have a string. Make sure it's in the right format.
            if weapon not in weplist:
                # Can't find that weapon. Perhaps capitalization is wrong?
                logging.error("Weapon %s not found. Ignoring.\nPerhaps capitalization?" % weapon)
            else:
                # We have a string, and it's in the list. We have a valid weapon!
                logging.debug("Weapon %s chosen, any filters have been ignored." % weapon)
                return weapon
        if damagetype is not None:
            # This isn't a list. So, check it.
            if type(damagetype) is not str:
                logging.error("Incorrect argument %s for damage type. Ignoring." % str(damagetype))
                damagetype = None
        if group is not None:
            group = getSet(group)
        if weapontype is not None:
            weapontype = getSet(weapontype)
        if properties is not None:
            properties = getSet(properties)
        if materialtype is not None:
            materialtype = getSet(materialtype)
        flist = []
        for w in weplist:
            if data.has_option(w, "group") and group is not None:
                # We have a group filter.
                wgroup = getSet(data[w]["group"])
                # Check it against out list.
                if not group.issubset(wgroup):
                    # Nope, boo.
                    continue
            elif not data.has_option(w, "group") and group is not None:
                logging.error("Weapon %s does not have a group!" % w)
                continue
            if data.has_option(w, "itemsubtype") and weapontype is not None:
                # A weapon type filter.
                wtype = getSet(data[w]["itemsubtype"])
                if not weapontype.issubset(wtype):
                    # Weapon type doesn't match.
                    continue
            elif not data.has_option(w, "itemsubtype"):
                # It doesn't match our filter with no group either.
                continue
            if data.has_option(w, "damagetype") and damagetype is not None:
                # Check if they're the same
                if damagetype != data[w]["damagetype"]:
                    continue
            elif not data.has_option(w, "damagetype") and damagetype is not None:
                # "No damage type" doesn't match our damagetype filter, so.
                continue
            if data.has_option(w, "materialtype") and materialtype is not None:
                # A material type filter. Make sure ours is in the list.
                mtype = getSet(data[w]["materialtype"])
                if not materialtype.issubset(mtype):
                    # Nope.
                    continue
            elif not data.has_option(w, "materialtype") and materialtype is not None:
                # As with other things, skip it because "None" doesn't match.
                continue
            if data.has_option(w, "properties") and properties is not None:
                # I think we know how this works by now.
                props = getSet(data[w]["properties"])
                if not properties.issubset(props):
                    continue
            elif not data.has_option(w, "properties") and properties is not None:
                continue
            # Check to make sure our item doesn't have a bonus associated with
            # it that might put us over.
            if data.has_option(w, "bonus"):
                # Do some math to make sure that if we're re-generating a
                # weapon we don't go over.
                budget = self.maxbonus - self.getBonus()
                budget += self.bonus
                if data[w]["bonus"] > budget:
                    continue
            # OK, we've made it this far.
            # The weapon matches our filter. Add it to the list.
            flist.append(w)
        #Cool, now we have a list of weapons. Or do we?
        if len(flist) == 0:
            logging.debug("Filters eliminated all weapons. Defaulting.")
        else:
            weplist = flist
        r = random.randint(0, len(weplist)-1)
        weapon = random.choice(weplist)
        return weapon
        
    def getWeaponInfo(self):
        self.group = getList(self.id, "group")
        if data.has_option(self.id, "weight"):
            self.weight = data[self.id].getfloat("weight")
        if data.has_option(self.id, "bonus"):
            self.bonus = data[self.id].getint("bonus")
        if data.has_option(self.id, "itemsubtype"):
            self.subtype = getList(self.id, "itemsubtype")
        if data.has_option(self.id, "damage"):
            self.damage = data[self.id]["damage"]
            self.damagetype = data[self.id]["damagetype"]
        self.properties = getList(self.id, "properties")
        if "versatile" in self.properties:
            self.damagevers = data[self.id]["damagevers"]
        if "ammunition" in self.properties or "thrown" in self.properties:
            # A weapon with a range.
            if data.has_option(self.id, "shortrange"):
                self.shortrange = data[self.id].getint("shortrange")
            else:
                self.shortrange = 5
            if data.has_option(self.id, "longrange"):
                self.longrange = data[self.id].getint("longrange")
            else:
                self.longrange = self.shortrange
        if data.has_option(self.id, "materialtype"):
            self.materialtype = getList(self.id, "materialtype")
        if data.has_option(self.id, "quantity"):
            qty = data[self.id].getint("quantity")
            # If quantity is 1 (or less) we don't care. Ignore it.
            if qty > 1:
                self.quantity = qty
        self.randomlists = self.getRandomLists()
        self.choice = self.chooseRandom()
        self.itemname = self.replaceRandom(data[self.id]["name"])

class Staff(Item):
    # Staffs are weird. They're both a weapon (quarterstaff) and a spellcasting
    # thingamajig like wands. A lot of the 5e staffs are either "Bunch of spells"
    # or "Does super tailored thing" so I'm going my own way with them.
    def __init__(self, rarity=None, id=None, forcerarity=True):
        Item.__init__(self, rarity=rarity)
        # So we *do* have staff items. But they still are going to be, at their
        # heart, quarterstaffs. So we will need to grab that info too.
        self.category = "staff"
        self.id = self.getStaff(id)
        self.getStaffInfo()
        self.getMaterial()
        bonus = self.addAllEffects() # Get us some effects!
        if bonus < self.maxbonus and forcerarity:
            tries = 0
            while bonus < self.maxbonus:
                bonus = self.redoEffects()
                tries += 1
                if tries >= self.maxtries:
                    break
        if bonus < self.maxbonus:
            self.rarity = self.getRarity()
        self.attunement = self.getAttunement()
        self.name = self.getName()
        self.info = self.getInfo()
        self.description = self.getDescription()
        
    def getStaff(self, id):
        # This grabs our staff. This determines the itemname and materials.
        itemlist = getCategoryList(self.category)
        wlist = []
        if id in itemlist:
            return id
        else:
            logging.debug("Staff %s not found in category %s" % (id, self.category))
        for i in itemlist:
            # Get the item's chance.
            if data.has_option(i, "chance"):
                wlist.append(data[i].getfloat("chance"))
            else:
                # Default to a chance of 1.
                wlist.append(1)
        item = random.choices(itemlist,wlist)[0]
        return item
    
    def getStaffInfo(self):
        # OK, so first. Let's grab our staff item properties.
        self.staffid = cfg["Options"]["staffweapon"]
        self.group = getList(self.staffid, "group")
        if data.has_option(self.staffid, "weight"):
            self.weight = data[self.staffid].getfloat("weight")
        if data.has_option(self.staffid, "bonus"):
            self.bonus = data[self.staffid].getint("bonus")
        if data.has_option(self.staffid, "itemsubtype"):
            self.subtype = getList(self.staffid, "itemsubtype")
        if data.has_option(self.staffid, "damage"):
            self.damage = data[self.staffid]["damage"]
            self.damagetype = data[self.staffid]["damagetype"]
        self.properties = getList(self.staffid, "properties")
        if "versatile" in self.properties:
            self.damagevers = data[self.staffid]["damagevers"]
        if "ammunition" in self.properties or "thrown" in self.properties:
            # A weapon with a range.
            if data.has_option(self.staffid, "shortrange"):
                self.shortrange = data[self.staffid].getint("shortrange")
            else:
                self.shortrange = 5
            if data.has_option(self.id, "longrange"):
                self.longrange = data[self.staffid].getint("longrange")
            else:
                self.longrange = self.shortrange
        # Get our material type from the "Staff" item first. If that doesn't
        # have one, then use the weapon.
        if data.has_option(self.id, "materialtype"):
            self.materialtype = getList(self.id, "materialtype")
        elif data.has_option(self.staffid, "materialtype"):
            self.materialtype = getList(self.staffid, "materialtype")
        self.randomlists = self.getRandomLists()
        self.choice = self.chooseRandom()
        self.itemname = self.replaceRandom(data[self.id]["name"])
        
    
class Ammunition(Item):
    def __init__(self, rarity=None, materialtype=None, ammunition=None,
                forcerarity=True):
        # Item bits.
        Item.__init__(self, rarity)
        self.category = "ammunition" # Tell everyone what we are.
        self.id = self.getAmmunition(ammunition, materialtype)
        self.getAmmunitionInfo()
        logging.debug("Selected %s" % self.itemname)
        self.getMaterial()
        bonus = self.addAllEffects() # Get us some effects!
        if bonus < self.maxbonus and forcerarity:
            tries = 0
            while bonus < self.maxbonus:
                bonus = self.redoEffects()
                tries += 1
                if tries >= self.maxtries:
                    break
        if bonus < self.maxbonus:
            self.rarity = self.getRarity()
        self.attunement = self.getAttunement()
        self.name = self.getName()
        self.info = self.getInfo()
        self.description = self.getDescription()
        
    def getAmmunition(self, ammunition, materialtype):
        # Selecting ourselves an ammunition type!
        ammolist = getCategoryList("ammunition")
        if ammunition is not None:
            # We have one picked out for us.
            if ammunition not in ammolist:
                # It's not in our list though.
                logging.error("Ammunition %s not found. Ignoring." % ammunition)
            else:
                logging.debug("Ammunition %s chosen." % ammunition)
                return ammunition
        # Ammunition is simple. Only one filter.
        if materialtype is not None:
            materialtype = getSet(materialtype)
        flist = [] # Our filtered list.
        for a in ammolist:
            if data.has_option(a, "materialtype") and materialtype is not None:
                mlist = getSet(getList(a, "materialtype"))
                if mlist.isdisjoint(materialtype):
                    # There's no overlap in our material lists.
                    continue
            flist.append(a)
        # Now we should have our list.
        if len(flist) == 0:
            # We need SOMETHING.
            logging.debug("Filters eliminated all ammunition. Defaulting.")
        else:
            weplist = flist
        ammo = random.choice(weplist)
        return ammo
    
    def getAmmunitionInfo(self):
        # Pulls the (very few) properties from the ammunition.
        self.quantity = data[self.id].getint("quantity")
        if data.has_option(self.id, "materialtype"):
            self.materialtype = getList(self.id, "materialtype") 
        if data.has_option(self.id, "bonus"):
            self.bonus = data[self.id].getint("bonus")     
        self.randomlists = self.getRandomLists()
        self.choice = self.chooseRandom()
        self.itemname = self.replaceRandom(data[self.id]["name"])

class Armor(Item):
    def __init__(self, rarity=None, group=None, materialtype=None, subtype=None,
        mindexterity=None, maxstrengthreq=None, stealthpenalty=None, armor=None,
        forcerarity=True):
        # Init the item bits.
        Item.__init__(self, rarity)
        self.category = "armor"
        self.id = self.getArmor(armor, group, subtype,  materialtype, 
                                mindexterity, maxstrengthreq, stealthpenalty)
        self.getArmorInfo()
        logging.debug("Selected %s" % self.itemname)
        self.getMaterial()
        bonus = self.addAllEffects() # Get us some effects!
        if bonus < self.maxbonus and forcerarity:
            tries = 0
            while bonus < self.maxbonus:
                bonus = self.redoEffects()
                tries += 1
                if tries >= self.maxtries:
                    break
        if bonus < self.maxbonus:
            self.rarity = self.getRarity()
        self.attunement = self.getAttunement()
        self.name = self.getName()
        self.info = self.getInfo()
        self.description = self.getDescription()
        
    def getArmor(self, armor, group, subtype, materialtype, mindexterity,
                maxstrengthreq, stealthpenalty):
        # As with the others, first we get our list.
        armorlist = getCategoryList("armor")
        # And check to see if the specified one is on the list.
        if armor is not None:
            if armor not in armorlist:
                logging.error("Armor %s is not found. Ignoring." % armor)
            else:
                logging.debug("Armor %s chosen." % armor)
                return armor
        # Convert things to sets so we're not repeatedly doing this later.
        if group is not None:
            group = getSet(group)
        if materialtype is not None:
            materialtype = getSet(materialtype)
        if subtype is not None:
            subtype = getSet(subtype)
        # And check our other filters.
        if mindexterity is not bool and mindexterity is not None:
            mindexterity = int(mindexterity)
        if maxstrengthreq is not None:
            maxstrengthreq = int(maxstrengthreq)
        if stealthpenalty is not None:
            stealthpenalty = bool(stealthpenalty)
        # Now that that's sorted, let's start, well, sorting.
        flist = []
        for a in armorlist:
            # Group filter.
            if group is not None:
                if not data.has_option(a, "group"):
                    # Cannot match a nonexistent subtype.
                    continue
                else:
                    require = getSet(getList(a, "group"))
                    if not group.issubset(require):
                        # We don't have a match here.
                        continue
            # Subtype filter.
            if subtype is not None:
                if not data.has_option(a, "itemsubtype"):
                    # Cannot match a nonexistent subtype.
                    continue
                else:
                    require = getSet(getList(a, "itemsubtype"))
                    if not subtype.issubset(require):
                        # We don't have a match here.
                        continue
            # Materialtype filter
            if materialtype is not None:
                if not data.has_option(a, "materialtype"):
                    # Cannot match a nonexistent subtype.
                    continue
                else:
                    require = getSet(getList(a, "materialtype"))
                    if not materialtype.issubset(require):
                        # We don't have a match here.
                        continue
            # Now we get our other filters.
            if stealthpenalty is not None:
                if not data.has_option(a, "stealthpenalty"):
                    # Defaults to false/no penalty
                    require = False
                else:
                    require = data[a].getboolean("stealthpenalty")
                if stealthpenalty != require:
                    # No match here.
                    continue
            if maxstrengthreq is not None:
                # We have a maximum strength requirement.
                if not data.has_option(a, "strengthreq"):
                    # Default to 0. This lets us easy compare.
                    require = 0
                else:
                    require = data[a].getint("strengthreq")
                if require > maxstrengthreq:
                    # Requires too much strength.
                    continue
            if mindexterity is not None:
                # We want the armor to provide a minimum of +X dexterity.
                if not data.has_option(a, "dexteritybonus"):
                    # Default is no dexterity bonus. So immediate fail.
                    continue
                require = data[a]["dexteritybonus"]
                if require != "true":
                    # If it IS true, we pass. It's unlimited.
                    # But if it's false, we auto-fail.
                    if require == "false":
                        continue
                    require = int(require) # We're in numbers now.
                    if require < mindexterity:
                        # The required amount is too low.
                        continue
            # It's passed our filters so far, so.
            flist.append(a)
        # OK, so now we have our list.
        if len(flist) == 0:
            logging.debug("Filters eliminated all armors. Defaulting.")
        else:
            armorlist = flist
        armor = random.choice(armorlist)
        return armor
    
    def getArmorInfo(self):
        self.group = getList(self.id, "group")
        if data.has_option(self.id, "weight"):
            self.weight = data[self.id].getfloat("weight")
        if data.has_option(self.id, "bonus"):
            self.bonus = data[self.id].getint("bonus")
        if data.has_option(self.id, "itemsubtype"):
            self.subtype = getList(self.id, "itemsubtype")
        if data.has_option(self.id, "materialtype"):
            self.materialtype = getList(self.id, "materialtype")
        self.ac = data[self.id].getint("armorclass")
        if data.has_option(self.id, "dexteritybonus"):
            self.maxdexterity = data[self.id]["dexteritybonus"]
            if self.maxdexterity in ["true", "false"]:
                self.maxdexterity = bool(self.maxdexterity)
                if not self.maxdexterity:
                    if self.properties is None:
                        self.properties = ["nodexterity"]
                    else:
                        self.properties.append("nodexterity")
            else:
                self.maxdexterity = int(self.maxdexterity)
                if self.properties is None:
                    self.properties = ["limitdexterity"]
                else:
                    self.properties.append("limitdexterity")
        else:
            self.maxdexterity = False
            if self.properties is None:
                self.properties = ["nodexterity"]
            else:
                self.properties.append("nodexterity")
            
        if data.has_option(self.id, "strengthreq"):
            self.minstrength = data[self.id].getint("strengthreq")
            if self.properties is None:
                self.properties = ["strengthreq"]
            else:
                self.properties.append("strengthreq")
        else:
            self.minstrength = 0
        if data.has_option(self.id, "stealthpenalty"):
            self.stealthpenalty = data[self.id].getboolean("stealthpenalty")
        else:
            self.stealthpenalty = False
        if self.stealthpenalty and self.properties is None:
            self.properties = ["stealthpenalty"]
        elif self.stealthpenalty:
            self.properties.append("stealthpenalty")
        self.randomlists = self.getRandomLists()
        self.choice = self.chooseRandom()
        self.itemname = self.replaceRandom(data[self.id]["name"])

class Shield(Item):
    def __init__(self, rarity=None, group=None, materialtype=None, subtype=None,
        shield=None, forcerarity=True):
        # Init the item bits.
        Item.__init__(self, rarity)
        self.category = "shield"
        self.id = self.getShield(shield, group, subtype,  materialtype)
        self.getShieldInfo()
        logging.debug("Selected %s" % self.itemname)
        self.getMaterial()
        bonus = self.addAllEffects() # Get us some effects!
        if bonus < self.maxbonus and forcerarity:
            tries = 0
            while bonus < self.maxbonus:
                bonus = self.redoEffects()
                tries += 1
                if tries >= self.maxtries:
                    break
        if bonus < self.maxbonus:
            self.rarity = self.getRarity()
        self.attunement = self.getAttunement()
        self.name = self.getName()
        self.info = self.getInfo()
        self.description = self.getDescription()
        
    def getShield(self, shield, group, subtype, materialtype):
        # As with the others, first we get our list.
        shieldlist = getCategoryList("shield")
        # And check to see if the specified one is on the list.
        if shield is not None:
            if shield not in shieldlist:
                logging.error("Shield %s is not found. Ignoring." % shield)
            else:
                logging.debug("Shield %s chosen." % shield)
                return shield
        # Convert things to sets so we're not repeatedly doing this later.
        if group is not None:
            group = getSet(group)
        if materialtype is not None:
            materialtype = getSet(materialtype)
        if subtype is not None:
            subtype = getSet(subtype)
        # Now that that's sorted, let's start, well, sorting.
        flist = []
        for a in shieldlist:
            # Group filter.
            if group is not None:
                if not data.has_option(a, "group"):
                    # Cannot match a nonexistent subtype.
                    continue
                else:
                    require = getSet(getList(a, "group"))
                    if not group.issubset(require):
                        # We don't have a match here.
                        continue
            # Subtype filter.
            if subtype is not None:
                if not data.has_option(a, "itemsubtype"):
                    # Cannot match a nonexistent subtype.
                    continue
                else:
                    require = getSet(getList(a, "itemsubtype"))
                    if not subtype.issubset(require):
                        # We don't have a match here.
                        continue
            # Materialtype filter
            if materialtype is not None:
                if not data.has_option(a, "materialtype"):
                    # Cannot match a nonexistent subtype.
                    continue
                else:
                    require = getSet(getList(a, "materialtype"))
                    if not materialtype.issubset(require):
                        # We don't have a match here.
                        continue
            # It's passed our filters so far, so.
            flist.append(a)
        # OK, so now we have our list.
        if len(flist) == 0:
            logging.debug("Filters eliminated all shields. Defaulting.")
        else:
            shieldlist = flist
        shield = random.choice(shieldlist)
        return shield
    
    def getShieldInfo(self):
        self.group = getList(self.id, "group")
        if data.has_option(self.id, "weight"):
            self.weight = data[self.id].getfloat("weight")
        if data.has_option(self.id, "bonus"):
            self.bonus = data[self.id].getint("bonus")
        if data.has_option(self.id, "itemsubtype"):
            self.subtype = getList(self.id, "itemsubtype")
        if data.has_option(self.id, "materialtype"):
            self.materialtype = getList(self.id, "materialtype")
        self.ac = data[self.id].getint("armorclass")
        self.randomlists = self.getRandomLists()
        self.choice = self.chooseRandom()
        self.itemname = self.replaceRandom(data[self.id]["name"])

class WondrousItem(Item):
    # A single class for all our wondrous item needs!
    # Belts, boots, bracers, cloaks, eyewear, hats, rings, trinkets, and gloves.
    # Rods and staffs are handleded elsewhere.
    def __init__(self, rarity=None, category=None, id=None, forcerarity=True):
        # So these are simple to get. we don't need to worry about filters!
        # Other than type, there's nothing to filter!
        Item.__init__(self, rarity)
        self.wondrous = True # We're a wondrous item!
        # First, let's get ourselves a category.
        clist = ["belt", "boots", "bracers", "cloak", "eyewear", "hat", "ring",
                "trinket", "gloves", "scroll", "wand", "rod"]
        if id is not None and category is None:
            # Figure out what category we're supposed to be in.
            for c in clist:
                ilist = getCategoryList(c)
                if id not in ilist:
                    continue
                else:
                    self.category = c
        elif category not in clist:
            self.category = random.choice(clist)
        else:
            self.category = category
        self.id = self.getWondrousItem(id)
        # Usually this is in a different function but that'd be excessive.
        self.randomlists = self.getRandomLists()
        self.choice = self.chooseRandom()
        self.itemname = self.replaceRandom(data[self.id]["name"])
        # Some things use material, but mostly for flavor.
        if data.has_option(self.id, "materialtype"):
            self.materialtype = getList(self.id, "materialtype")
        self.getMaterial()
        bonus = self.addAllEffects() # Get us some effects!
        if bonus < self.maxbonus and forcerarity:
            tries = 0
            while bonus < self.maxbonus:
                bonus = self.redoEffects()
                tries += 1
                if tries >= self.maxtries:
                    break
        if bonus < self.maxbonus:
            self.rarity = self.getRarity()
        self.attunement = self.getAttunement()
        self.name = self.getName()
        self.info = self.getInfo()
        self.description = self.getDescription()
    
    def getWondrousItem(self, id):
        # Oh, we need an item!
        # This should be simple.
        itemlist = getCategoryList(self.category)
        wlist = []
        if id in itemlist:
            return id
        else:
            logging.debug("Item %s not found in category %s" % (id, self.category))
        for i in itemlist:
            # Get the item's chance.
            if data.has_option(i, "chance"):
                wlist.append(data[i].getfloat("chance"))
            else:
                # Default to a chance of 1.
                wlist.append(1)
        item = random.choices(itemlist,wlist)[0]
        return item
        
class Belt(WondrousItem):
    # This just makes things easier.
    def __init__(self, rarity=None, id=None, forcerarity=True):
        WondrousItem.__init__(self, rarity=rarity, id=id, category="belt",
            forcerarity=forcerarity)
        if len(self.prefixes + self.suffixes) == 0:
            # We generated empty. Regenerate.
            self.__init__(rarity=rarity, id=id)

class Boots(WondrousItem):
    def __init__(self, rarity=None, id=None, forcerarity=True):
        WondrousItem.__init__(self, rarity=rarity, id=id, category="boots",
            forcerarity=forcerarity)
        if len(self.prefixes + self.suffixes) == 0:
            # We generated empty. Regenerate.
            self.__init__(rarity=rarity, id=id)

class Bracers(WondrousItem):
    def __init__(self, rarity=None, id=None, forcerarity=True):
        WondrousItem.__init__(self, rarity=rarity, id=id, category="bracers",
            forcerarity=forcerarity)
        if len(self.prefixes + self.suffixes) == 0:
            # We generated empty. Regenerate.
            self.__init__(rarity=rarity, id=id)
        
class Cloak(WondrousItem):
    def __init__(self, rarity=None, id=None, forcerarity=True):
        WondrousItem.__init__(self, rarity=rarity, id=id, category="cloak",
            forcerarity=forcerarity)
        if len(self.prefixes + self.suffixes) == 0:
            # We generated empty. Regenerate.
            self.__init__(rarity=rarity, id=id)
        
class Eyewear(WondrousItem):
    def __init__(self, rarity=None, id=None, forcerarity=True):
        WondrousItem.__init__(self, rarity=rarity, id=id, category="eyewear",
            forcerarity=forcerarity)
        if len(self.prefixes + self.suffixes) == 0:
            # We generated empty. Regenerate.
            self.__init__(rarity=rarity, id=id)
        
class Hat(WondrousItem):
    def __init__(self, rarity=None, id=None, forcerarity=True):
        WondrousItem.__init__(self, rarity=rarity, id=id, category="hat",
            forcerarity=forcerarity)
        if len(self.prefixes + self.suffixes) == 0:
            # We generated empty. Regenerate.
            self.__init__(rarity=rarity, id=id)
        
class Ring(WondrousItem):
    def __init__(self, rarity=None, id=None, forcerarity=True):
        WondrousItem.__init__(self, rarity=rarity, id=id, category="ring",
            forcerarity=forcerarity)
        if len(self.prefixes + self.suffixes) == 0:
            # We generated empty. Regenerate.
            self.__init__(rarity=rarity, id=id)
        
class Trinket(WondrousItem):
    def __init__(self, rarity=None, id=None, forcerarity=True):
        WondrousItem.__init__(self, rarity=rarity, id=id, category="trinket",
            forcerarity=forcerarity)
        if len(self.prefixes + self.suffixes) == 0:
            # We generated empty. Regenerate.
            self.__init__(rarity=rarity, id=id)
        
class Gloves(WondrousItem):
    def __init__(self, rarity=None, id=None, forcerarity=True):
        WondrousItem.__init__(self, rarity=rarity, id=id, category="gloves",
            forcerarity=forcerarity)
        if len(self.prefixes + self.suffixes) == 0:
            # We generated empty. Regenerate.
            self.__init__(rarity=rarity, id=id)

class Scroll(WondrousItem):
    def __init__(self, rarity=None, id=None, forcerarity=True):
        WondrousItem.__init__(self, rarity=rarity, id=id, category="scroll",
            forcerarity=forcerarity)
        if len(self.prefixes + self.suffixes) == 0:
            # We generated empty. Regenerate.
            self.__init__(rarity=rarity, id=id)
        
class Wand(WondrousItem):
    def __init__(self, rarity=None, id=None, forcerarity=True):
        WondrousItem.__init__(self, rarity=rarity, id=id, category="wand",
            forcerarity=forcerarity)
        if len(self.prefixes + self.suffixes) == 0:
            # We generated empty.
            self.__init__(rarity=rarity, id=id)

class Rod(WondrousItem):
    def __init__(self, rarity=None, id=None, forcerarity=True):
        WondrousItem.__init__(self, rarity=rarity, id=id, category="rod",
            forcerarity=forcerarity)
        if len(self.prefixes + self.suffixes) == 0:
            # We generated empty.
            self.__init__(rarity=rarity, id=id)
            
class Spellbook(Item):
    # Spellbooks! A collection of spells! For wizards!
    def __init__(self, rarity=None, level=None, id=None, forcerarity=None):
        # As with others, ID is for the ID of the base book.
        # But as Spellbooks don't care about effects, 
        Item.__init__(self, rarity=rarity)
        self.category = "spellbook"
        self.id = self.getSpellBook(id)
        if level is not None:
            self.level = level
            self.rarity = self.setRarity()
        else:
            self.level = self.getLevel()
        if data.has_option(self.id, "materialtype"):
            self.materialtype = getList(self.id, "materialtype")
        self.getMaterial()
        self.getSpells(self.level)
        self.itemname = self.replaceRandom(data[self.id]["name"])
        self.name = self.getName()
        self.info = "Spellbook, %s" % self.rarity
        self.description = self.getDescription()
        
    def setRarity(self):
        # Sets the rarity of ourselves depending on our level.
        if self.level > 16:
            return "legendary"
        elif self.level > 10:
            return "veryrare"
        elif self.level > 6:
            return "rare"
        elif self.level > 2:
            return "uncommon"
        else:
            return "common"
            
        
    def getSpellBook(self, id):
        # Basically a copy of the GetWondrousItem thing.
        itemlist = getCategoryList("spellbook")
        wlist = []
        if id in itemlist:
            return id
        else:
            logging.debug("Item %s not found in category %s" % (id, self.category))
        for i in itemlist:
            # Get the item's chance.
            if data.has_option(i, "chance"):
                wlist.append(data[i].getfloat("chance"))
            else:
                # Default to a chance of 1.
                wlist.append(1)
        item = random.choices(itemlist,wlist)[0]
        return item
        
    def getLevel(self):
        # Returns a number (1-20) depending on what level of rarity we want.
        # Common is level 1-2, Uncommon is 3-6, Rare is 7-10
        # Very RAre is 11-16, and Legendary is 17-20.
        if self.rarity == "common":
            level = random.randint(1,2)
        elif self.rarity == "uncommon":
            level = random.randint(3,6)
        elif self.rarity == "rare":
            level = random.randint(7,10)
        elif self.rarity == "veryrare":
            level = random.randint(11,16)
        elif self.rarity == "legendary":
            level = random.randint(17,20)
        else:
            level = 1 # Default to lowest level.
        return level
    
    def addSpell(self,level):
        # Gets a wizard spell of the appropriate level and adds it to the book.
        spell = Spell(level=level, chclass="wizard")
        # Make sure we have no duplicates.
        overflow = 0 # Just to make sure we don't loop infinitely.
        while spell.id in self.spellids:
            spell = Spell(level=level, chclass="wizard")
            overflow += 1
            if overflow > 100:
                # We've checked too many times. Probably not any left.
                spell = Spell(level=100)
        # OK, we have our spell now.
        if spell.id is None:
            # We have a failure.
            return False
        self.spells.append(spell)
        self.spellcount[level] += 1
        self.spellids.append(spell.id)
        return True
    
    def getSpells(self, level):
        # Adds spells to the spellbook, up to the given level.
        # First, reset the spellbook, just in case.
        self.spells = []
        self.spellids = []
        self.spellcount = [0] * 10
        # Now pick us some spells!
        if level >=1:
            # Add our cantrips.
            for r in range(0,3):
                # We don't worry about running out of these.
                # And if there isn't... oh well, not much we can do about it.
                self.addSpell(0)
            # And our first level spells.
            for r in range(0,6):
                # Same thing here. Always assume there's enough 1st level spells.
                self.addSpell(1)
        if level >= 2:
            # Add our new spells. Two new spells, and 0-2 scribed scrolls.
            for r in range(0,random.randint(2,4)):
                self.addSpell(1)
        if level >= 3:
            # We get level 2 spells now!
            # Add at least one.
            self.addSpell(2)
            # Now, for our other new spell and 0-2 scribes scrolls.
            for r in range(0, random.randint(1,3)):
                l = random.randint(1,2) # Random spell level.
                self.addSpell(l)
        if level >= 4:
            # Another cantrip.
            self.addSpell(0)
            # 2 new spells and 0-2 scrolls. You get the picture by now.
            for r in range(0, random.randint(2,4)):
                l = min(2,random.randint(1,3)) # Slightly bias towards 2nd-level.
                self.addSpell(l)
        if level >= 5:
            # Level 3 spell.
            self.addSpell(3)
            for r in range(0, random.randint(1,3)):
                l = random.randint(2,3)
                self.addSpell(l)
        if level >= 6:
            for r in range(0, random.randint(2,4)):
                l = min(3, random.randint(2,4))
                self.addSpell(l)
        if level >= 7:
            # Level 4 spell.
            self.addSpell(4)
            for r in range(0, random.randint(1,3)):
                l = random.randint(3,4)
                self.addSpell(l)
        if level >= 8:
            for r in range(0, random.randint(2,4)):
                l = min(4, random.randint(3,5))
                self.addSpell(l)
        if level >= 9:
            # Level 5 spell.
            self.addSpell(4)
            for r in range(0, random.randint(1,3)):
                l = random.randint(3,5)
                self.addSpell(l)
        if level >= 10:
            # Our last cantrip.
            self.addSpell(0)
            for r in range(0, random.randint(2,4)):
                l = min(5, random.randint(3,6))
                self.addSpell(l)
        if level >= 11:
            # Level 6 spell.
            self.addSpell(6)
            for r in range(0, random.randint(1,3)):
                l = random.randint(4,6)
                self.addSpell(l)
        if level >= 12:
            for r in range(0, random.randint(2,4)):
                l = min(6, random.randint(4,7))
                self.addSpell(l)
        if level >= 13:
            # Level 7 spell.
            self.addSpell(7)
            for r in range(0, random.randint(1,3)):
                l = random.randint(5,7)
                self.addSpell(l)
        if level >= 14:
            for r in range(0, random.randint(2,4)):
                l = min(7, random.randint(5,8))
                self.addSpell(l)
        if level >= 15:
            # Level 8 spell.
            self.addSpell(8)
            for r in range(0, random.randint(1,3)):
                l = random.randint(6,8)
                self.addSpell(l)
        if level >= 16:
            for r in range(0, random.randint(2,4)):
                l = min(8, random.randint(6,8))
                self.addSpell(l)
        if level >= 17:
            # Level 9 spell.
            self.addSpell(9)
            for r in range(0, random.randint(1,3)):
                l = random.randint(6,9)
                self.addSpell(l)
        if level >= 18:
            for r in range(0, random.randint(2,4)):
                l = random.randint(6,9)
                self.addSpell(l)
        if level >= 19:
            for r in range(0, random.randint(2,4)):
                l = random.randint(6,9)
                self.addSpell(l)
        if level >= 20:
            for r in range(0, random.randint(2,4)):
                l = random.randint(6,9)
                self.addSpell(l)
        return sum(self.spellcount)
    
    def getName(self):
        # Spellbooks don't have prefixes or suffixes, so it doesn't follow
        # the normal methodology.
        lvlstr = "Level %d" % self.level
        qtystr = "(%d)" % sum(self.spellcount)
        if "@material" in self.itemname:
            name = " ".join([lvlstr, self.itemname, qtystr])
        else:
            name = " ".join([lvlstr, self.material.name, self.itemname, qtystr])
        while "  " in name:
            name = name.replace("  "," ").strip()
        name = self.replaceVars(name)
        return name
    
    def getDescription(self):
        # Instead of prefix and suffix stuff, just show our list of spells.
        splist = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[]}
        desc = ""
        for s in self.spells:
            splist[s.level].append(s.name)
        for r in range(0,10):
            # For each spell level:
            splist[r] = ", ".join(splist[r])
        # Now add to the description.
        if splist[0] != "":
            desc += "*Cantrips:*\n" + splist[0]
        for r in range(1,10):
            if splist[r] != "":
                desc += "\n\n*Level %d Spells:*\n" % r + splist[r]
        return desc

class ForceScroll(Item):
    # A category to force-generate a scroll of a particular level.
    def __init__(self, level):
        # First, set our rarity.
        if level < 0:
            level = 0
        elif level > 9:
            level = 9
        if level <= 1:
            rarity = "common"
        elif level <= 3:
            rarity = "uncommon"
        elif level <= 5:
            rarity = "rare"
        elif level <= 8:
            rarity = "veryrare"
        elif level == 9:
            rarity = "legendary"
        self.level = str(level)
        Item.__init__(self, rarity)
        self.wondrous = True # We're a wondrous item!
        self.id = "scrollitem" # We're forcing things here.
        self.category = "scroll"
        self.itemname = "Scroll"
        self.getMaterial()
        self.suffixes.append(self.putSuffix("scrolleffect%s" % self.level))
        self.name = self.getName()
        self.info = self.getInfo()
        self.description = self.getDescription()

    def putSuffix(self, id):
        # Puts the designated suffix effect on the scroll.
        neweffect = Effect(category=self.category, affix="suffix", 
        subtype=None, itemid=self.id, damagetype=None,
        materialtype=None, effectids=None, materialid=None, group=None,
        properties=None, maxbonus=None, minbonus=None, effectid = id)
        self.parseModifiers(neweffect)
        logging.debug("Selected %s" % neweffect.id)
        return neweffect
