# A new item generator.
# The original one is a little... hacky in places. And also a little bloated.
# For example: Wondrous items. There was a separate class for each. That...
# All did the same thing? Not particularly necessary.
#
# Goals for upgrades for this are also to allow for editing and re-generating
# parts of items. That is, replace the material. Replace an effect. Replace
# the base item itself.
#
# Oh, and do better with the logging.

import random
import logging
import configs
import spells
from importlib import reload

# Load our configs.
general = configs.CFG(configs.GENERAL)
item_data = configs.CFG(configs.ITEM_DATA)
cfg = configs.CFG(configs.ITEM_GEN_CFG)

# Our item types. We'll use them a bit later.
ITEM_TYPES = ("ammunition", "armor", "belt", "boots", "bracers", "eyewear",
        "hat", "ring", "rod", "shield", "staff", "trinket", "wand", "weapon",
        "cloak", "gloves", "scroll")
# These items are considered "Wondrous Items".
# Wondrous Items are treated differently in a few ways. Notably, they can ignore
# some limits.
WONDROUS_ITEMS = ("belt", "boots", "bracers", "eyewear", "hat", "ring", "rod",
        "trinket", "cloak", "gloves")
# Items that can be enhanced.
ENH_ITEMS = ("ammunition", "armor", "shield", "weapon", "staff", "wand")
# And item weights. If we aren't given an item type, use these to determine.
ITEM_WEIGHTS = []
for item in ITEM_TYPES:
    ITEM_WEIGHTS.append(cfg.getInt("ItemWeights", item))

# A list of rarities we use.
RARITY_LIST = ["common", "uncommon", "rare", "veryrare", "legendary"]

def reloadConfigs():
    # Reloads the configs module and then resets the configs.
    reload(configs)
    general = configs.CFG(configs.GENERAL)
    item_data = configs.CFG(configs.ITEM_DATA)
    cfg = configs.CFG(configs.ITEM_GEN_CFG)
    return

# Our own functions
def getSet(item):
    # Returns an item as a set.
    # These are super useful for comparison for filters.
    if type(item) == str:
        # Strings might be a semicolon list. If not, well. A one-item set works.
        item == item.split(";")
    if type(item) not in [list, tuple, set]:
        # Our workable types here.
        return set(item)
    else:
        logging.error("Cannot convert to set! Set will return empty.")
        # Return an empty set, so we continue working.
        return {}

def checkAttunement(id1, id2):
    # Determines if the attunements of the two effects, items, etc
    if type(id1) is not str or type(id2) is not str:
        logging.error("One or both ids were not strings. Attunement cannot be checked.")
        return False
    if id1 not in item_data.config:
        logging.error("%s is not in the item generator's item_data." % id1)
        return False
    if id2 not in item_data.config:
        logging.error("%s is not in the item generator's item_data." % id2)
        return False
    # OK, now we've done the easy filter. Time to get some information.
    attune1 = item_data.get(id1, "attunement")
    attune2 = item_data.get(id2, "attunement")
    if attune1 is None or attune2 is None:
        # No attunement is always compatible.
        return True
    attune1 = attune1.lower()
    attune2 = attune2.lower()
    restrict1 = item_data.get(id1, "attunement_requirements")
    restrict2 = item_data.get(id2, "attunement_requirements")
    if attune1 == "false" or attune2 == "false":
        # No requirements on one of them.
        return True
    if item_data.getBool(id1, "attunement_join") == False or \
        item_data.getBool(id2, "attunement_join") == False:
        # One of these says "NO!" to joining any attunement.
        return False
    if attune1 == "desc" and restrict1 is None:
        # We were supposed to have a requirement description, but it's not there.
        attune1 = "true"
    if attune2 == "desc" and restrict2 is None:
        # Same as above.
        attune2 = "true"
    # If we have restrictions, they're in place now.
    # Time to check them.
    if attune1 == "desc" and attune1 == attune2:
        # Both have descriptions.
        if restrict1 == restrict2:
            # Identical is compatible.
            return True
        else:
            # They differ and are not.
            return False
    elif (attune1 == "desc" and attune2 == "true" and restrict2 is None) \
        or (attune2 == "desc" and attune1 == "true" and restrict1 is None):
        # If one is a description and the other simply needs attunement, it works.
        return True
    elif attune1 == "true" and attune2 == "true":
        # Both are simple attunements.
        return True
    else:
        # Hmm. No dice here.
        return False

# Changes the dice size. Not sure if I'll need this outside the item class, but
# there's really no reason for it to be in there so. Here it is.
def changeDiceSize(workstr, increase=True):
    # If we're passed a non-dice thing, ignore it.
    if type(workstr) is not str:
        return workstr
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

# A class for our modifiers.
# These are our materials and effects.
class Modifier:
    def __init__(self, category, itemtype=None, itemtypeconflict=None, itemsubtype=None,
        damagetype=None, materialtype=None, itemgroup=None, properties=None,
        bonus=None, affix=None, effects=None, itemid=None, rarity=None, force_none=False):
        # Set up our empty variables.
        self.emptyValues()
        self.category = category
        # Well, that's a lot of stuff!
        # Grab ourselves an ID.
        if not force_none:
            self.id = self.getID(category, itemtype, itemsubtype, damagetype,
                materialtype, itemgroup, properties, bonus, affix, effects, itemid,
                rarity=rarity, itemtypeconflict=itemtypeconflict)
            self.setValues(itemid)
    
    def emptyValues(self):
        # Sets up all variables as their empty, default state.
        self.id = None
        self.name = None
        self.prefix = None
        self.suffix = None
        self.bonus = 0
        self.modifiers = []
        self.properties = []
        self.random_lists = {}
        self.choice = None
        self.spells = {}
        self.attunement = None
        self.material_type = None
        self.affix = None
   
    def setValues(self, itemid):
        if self.id is None:
            return
        # Fills out the information for the modifier.
        self.category = item_data.get(self.id, "category")
        self.bonus = item_data.getInt(self.id, "bonus")
        self.modifiers = self.getModifiers(itemid)
        self.properties = item_data.getList(self.id, "properties")
        self.random_lists = self.getRandomLists()
        self.choices = self.chooseRandom()
        self.attunement = self.getAttunement()
        if self.category == "material":
            # Effects don't have a material type since they're not, well. A material.
            self.material_type = item_data.getList(self.id, "material_type")
        self.name = self.getString("name")
        self.prefix = self.getString("prefix")
        self.suffix = self.getString("suffix")
    
    def rerollRandom(self, itemid):
        # Re-rolls the spells and random choice.
        self.spells = {}
        self.getModifiers(itemid) # Don't need to reassign the modifiers
        self.choices = self.chooseRandom()
        self.name = self.getString("name")
        self.prefix = self.getString("prefix")
        self.suffix = self.getString("suffix")
    
    def getModifiers(self, itemid):
        # Returns the pre-programmed effects, if they're available.
        modifiers = []
        spells = {}
        mods = item_data.get(self.id, "modifiers")
        if mods is not None:
            # We have some modifiers. Now parse them.
            mods = mods.split(";")
            for mod in mods:
                # We're not validating, just parsing.
                if mod.find("(") == -1:
                    # No arguments. Just put it into the list.
                    # We want it as a list for ease of use later.
                    modifiers.append([mod.strip()])
                else:
                    p1 = mod.find("(")
                    p2 = mod.find(")")
                    modlist = []
                    modlist.append(mod[:p1]) # The command.
                    modlist += mod[p1+1:p2].split(",") # Split the arguments
                    if modlist[0].lower().startswith("randspell"):
                        # We have a random spell. This we parse here, and
                        # not add it to the list.
                        self.getSpell(itemid, modlist)
                    else:
                        modifiers.append(modlist)
        return modifiers
    
    def getRandomLists(self):
        # Retrieves the random lists.
        rlists = {}
        for option in item_data.config[self.id]:
            # Check each of our options.
            if option.startswith("random_list_") and len(option) > 10:
                # A random list! With an identifier!
                random = item_data.getList(self.id, option)
                rlists["%s" % option[12:]] = random
        return rlists
    
    def chooseRandom(self):
        # Each item has a number of joinlists. These are which random lists
        # share a choice. By default, they all have the same one. The first
        # item in a list, if it starts with "@@", designates the group.
        # Figure out which groups we have.
        joingroups = {"default":[]}
        for r in self.random_lists:
            first = self.random_lists[r][0]
            if first.startswith("@@"):
                if first not in joingroups:
                    joingroups[first] = [r]
                else:
                    joingroups[first] += [r]
            else:
                joingroups["default"] += [r]
        if len(joingroups["default"]) == 0:
            # Our default group is empty. Remove it.
            joingroups.pop("default", None)
        choices = {}
        # Now record our choices for each group.
        for group in joingroups:
            length = -1
            choice = -1
            for rlist in joingroups[group]:
                if len(self.random_lists[rlist]) < length or length == -1:
                    length = len(self.random_lists[rlist])
            if group == "default":
                choice = random.randint(0, length-1)
            else:
                # Ignore the first item as it's the group ID.
                choice = random.randint(1, length-1)
            # Now assign this group's items to choices.
            for rlist in joingroups[group]:
                choices[rlist] = choice
        return choices

    def getSpell(self, itemid, info):
        # Adds the designated spell to the modifier's spell list.
        id = info[0][9:] # The identifier of the spell.
        category = None
        if itemid is not None:
            category = item_data.get(itemid, "category")
        levels = []
        notlevels = []
        for i in info[1:]:
            try:
                # Is this an int?
                i = int(i)
                levels.append(i)
            except:
                # It is *not* an int.
                # It may be a colon-separated list (legacy)
                # Or maybe just a string. Either way, this works.
                notlevels += i.split(":")
        # Figure out if we have a level identifier
        level = None
        if len(levels) == 1:
            level = levels[0]
        else:
            level = (min(levels), max(levels))
        # Now for our school.
        schools = []
        classlist = []
        for item in notlevels:
            if item in spells.CLASSES:
                classlist.append(item)
            elif item in spells.SPELL_SCHOOLS:
                schools.append(item)
        if len(schools) == 0:
            schools = None
        if len(classlist) == 0:
            classlist = None
        spell = spells.Spell(schools=schools, level=levels, classlist=classlist,
            itemtype=category)
        self.spells[id] = spell
        return
    
    def getString(self, strID):
        # Grabs the specified string, and replaces any variables in it.
        workstr = item_data.get(self.id, strID)
        workstr = self.replaceVars(workstr)
        return workstr
    
    def getDescription(self, category):
        if self.id is None:
            return "" # No description for nothing.
        desc = item_data.get(self.id, "%s_description" % category)
        if desc is None:
            return ""
        for item_type in ITEM_TYPES:
            if "@%s_description" % item_type in desc:
                newdesc = item_data.get(self.id, "%s_description" % item_type)
                if newdesc is not None:
                    desc = desc.replace("@%s_description" % item_type, newdesc)
        desc = self.replaceVars(desc)
        return desc
        
    def replaceVars(self, workstr):
        # Replaces the randomly generated spells and lists.
        if workstr is None or workstr == "":
            return ""
        # First, replace our random choices.
        for rand in self.choices:
            choice = self.choices[rand]
            find = "@R%s" % rand
            replace = self.random_lists[rand][choice]
            workstr = workstr.replace(find, replace)
        for spell in self.spells:
            find = "@spell%s" % spell
            replace = self.spells[spell].name
            workstr = workstr.replace(find, replace)
        return workstr
                
    
    def getAttunement(self):
        # Returns the attunement requirements of a given modifier.
        # Doesn't worry about attunement joining restrictions. Those are only
        # for filtering, and aren't used from here on out.
        attune = item_data.get(self.id, "attunement")
        if attune == "true" or attune == "desc":
            # We have some type of attunement.
            # See if we have any requirements.
            attunereq = item_data.get(self.id, "attunement_requirements")
            if attunereq is None:
                # No requirements, just general attunement
                return True
            elif attunereq is not None and attune == "desc":
                # We have a description. Return the whole thing.
                return attunereq
            else:
                # We have a list of requirements.
                return  attunereq.split(";")
            
    
    def getID(self, category, itemtype, itemsubtype, damagetype, materialtype,
        itemgroup, properties, bonus, affix, effects, itemid, rarity, itemtypeconflict):
        # Grabs an appropriate item ID, given our filters.
        # First, time to filter those filters.
        if type(category) is not str:
            logging.critical("Modifier must have a category of effect or material")
            raise typeError("Modifier must have a category of effect or material.")
        elif category not in ["effect","material"]:
            logging.critical("Modifier must have a category of effect or material.")
            raise ValueError("Modifier must have a category of effect or material.")
        # Item type. Should be a single item type as a string. If not, ignore it.
        if type(itemtype) is not str and itemtype is not None:
            logging.error("Itemtype must be a single string. Ignoring")
            itemtype = None
        # Subtype should be a list or tuple or set.
        if type(itemsubtype) not in [list, tuple, set] and itemsubtype is not None:
            logging.error("Item subtype must be a list. Ignoring.")
            itemsubtype = None
        if itemsubtype is not None:
            itemsubtype = set(itemsubtype)
        # Damagetype is a string.
        if type(damagetype) is not str and damagetype is not None:
            logging.error("Damage type must be a string. Ignoring.")
            damagetype = None
        # Material Type is a list or tuple
        if type(materialtype) not in [list, tuple] and materialtype is not None:
            logging.error("Material type must be a list. Ignoring.")
            materialtype = None
        if materialtype is not None:
            materialtype = set(materialtype)
        # Item group, also a list/tuple
        if type(itemgroup) not in [list, tuple] and itemgroup is not None:
            logging.error("Item group must be a list. Ignoring.")
            itemgroup = None
        if itemgroup is not None:
            itemgroup = set(itemgroup)
        # Properties, also a list/tuple.
        if type(properties) not in [list, tuple] and properties is not None:
            logging.error("Properties must be a list. Ignoring.")
            properties = None
        # Bonus should be either an int (Set number), or a list/tuple (Min/max).
        # Handling the list is done in the getModifier function
        if type(bonus) not in [int, list, tuple] and bonus is not None:
            logging.error("Bonus must be an int or two-item list. Ignoring.")
            bonus = None
        # affix should be a string.
        if type(affix) is not str and affix is not None:
            logging.error("Affix must be a string. Ignoring.")
            affix = None
        # But, affixes should only apply to effects, not materials.
        elif affix is not None and category == "material":
            logging.error("Affixes do not apply to materials. Ignoring.")
            affix = None
        # Only prefix and suffix allowed.
        elif affix not in ["prefix","suffix"] and affix is not None:
            logging.error("Affix must be prefix or suffix only. Ignoring.")
            affix = None
        # Effects must be in a list or tuple.
        if type(effects) not in [list, tuple] and effects is not None:
            logging.error("Effects must be in a list. Ignoring.")
            effects = None
        if type(itemid) is not str and itemid is not None:
            logging.error("Item ID must be a string. Ignoring.")
            itemid = None
        if type(itemtypeconflict) is str:
            itemtypeconflict = [itemtypeconflict]
        if type(itemtypeconflict) not in [list, tuple] and itemtypeconflict is not None:
            logging.error("Invalid itemtypeconflict filter. Ignoring.")
            itemtypeconflict = None
        min_bonus = 0
        max_bonus = 0
        if type(bonus) == int:
            min_bonus = bonus
            max_bonus = bonus
        elif bonus is not None:
            # We don't put floors or caps on these
            # Never know when someone will make a negative-bonus effect
            min_bonus = min(bonus)
            max_bonus = max(bonus)
        # Grab ourselves a list of appropriate effects.
        mod_list = item_data.getOptionList("category", category)
        # And some other lists for adding things that fit.
        filtered_list = []
        weight_list = []
        for mod in mod_list:
            # Now, to go through each of the filters.
            # First up, item type.
            if itemtype is not None or itemtypeconflict is not None:
                # Grab the data from the item.
                data = item_data.getList(mod, "item_type")
                if itemtype is not None:
                    if itemtype not in data and len(data) > 0:
                        # Our itemtype doesn't fit.
                        continue
                if itemtypeconflict is not None:
                    itemtypeconflict = set(itemtypeconflict)
                    data = set(data)
                    if not data.isdisjoint(itemtypeconflict):
                        # There's an overlap and that's bad.
                        continue
            if itemsubtype is not None:
                # Same deal here, except we have our own list.
                # The effect must be wholly contained in the filter.
                data = set(item_data.getList(mod, "item_subtype"))
                if not data.issubset(itemsubtype) and len(data) > 0:
                    # It's not.
                    continue
                # Now check for conflicts.
                data = set(item_data.getList(mod, "item_subtype_conflict"))
                if not data.isdisjoint(itemsubtype) and len(data) > 0:
                    # There's an overlap, which means conflict.
                    continue
            if damagetype is not None:
                # The effect can apply to any of its given damage types
                # We only have to make sure ours is in it.
                data = item_data.getList(mod, "damage_type")
                if damagetype not in data and len(data) > 0:
                    # It's not in it.
                    continue
                # And, similarly, we need to make sure ours is NOT in any conflict
                data = item_data.getList(mod, "damage_type_conflict")
                if damagetype in data and len(data) > 0:
                    # It is, boo.
                    continue
            if materialtype is not None:
                # OK, so. We have two things here.
                # First, we need to see if our material type is allowed.
                # This is simple overlap.
                data = set(item_data.getList(mod, "material_type"))
                if data.isdisjoint(materialtype) and len(data) > 0:
                    # No overlap.
                    continue
                # Now, we need to see if there's any overlap with our restrictions.
                data = set(item_data.getList(mod, "material_type_conflict"))
                if not data.isdisjoint(materialtype) and len(data) > 0:
                    # There's an overlap, so no joy here.
                    continue
            if itemgroup is not None:
                # Item group! If the modifier's groups are not fully contained
                # in the item's groups, then it fails.
                data = set(item_data.getList(mod, "group"))
                if not data.issubset(itemgroup) and len(data) > 0:
                    continue
                # As usual, check conflicts.
                data = set(item_data.getList(mod, "group_conflict"))
                if not data.isdisjoint(itemgroup) and len(data) > 0:
                    # There's an overlap. That's bad.
                    continue
            if properties is not None:
                # The given list must contain all of our requirements.
                data = set(item_data.getList(mod, "required_properties"))
                if not data.issubset(properties) and len(data) > 0:
                    continue
                # And conflicts.
                data = set(item_data.getList(mod, "property_conflict"))
                if not data.isdisjoint(itemgroup) and len(data) > 0:
                    continue
            if bonus is not None:
                # Make sure we're within bounds.
                data = item_data.getInt(mod, "bonus")
                if data is None:
                    # Invalid modifier.
                    continue
                if min_bonus > data or data > max_bonus:
                    # Outside of the range required.
                    continue
            if affix is not None:
                data = item_data.get(mod, affix)
                if data is None:
                    # No affix of this type.
                    continue
            if effects is not None:
                # These effects already exist. We must be compatible.
                data = item_data.getList(mod, "effect_id_conflict")
                data += item_data.getList(mod, "material_id_conflict")
                compatible = True
                for effect in effects:
                    if effect.id == mod:
                        # Never choose the same thing twice!
                        compatible = False
                        break
                    if effect.id in data:
                        # This effect conflicts with our conflicts.
                        # Don't bother checking the rest.
                        compatible = False
                        break
                    elist = item_data.getList(effect.id, "effect_id_conflict")
                    elist += item_data.getList(effect.id, "material_id_conflict")
                    if mod in elist:
                        # Our modifier is prohibited by this effect.
                        compatible = False
                        break
                    if not checkAttunement(mod, effect.id):
                        # Our attunement is incompatible.
                        compatible = False
                        break
                if compatible == False:
                    # We've ran into some comptaibility issues.
                    continue
            if itemid is not None:
                # Make sure this item isn't prohibited.
                data = item_data.getList(mod, "item_id_conflict")
                if itemid in data:
                    continue
            if rarity is not None:
                data = item_data.getList(mod, "req_rarity")
                if rarity not in data and len(data) > 0:
                    # Rarity not allowed.
                    continue
            # Wow! We made it this far!
            filtered_list.append(mod)
            chance = item_data.getInt(mod, "chance")
            if chance is None:
                weight_list.append(1)
            else:
                weight_list.append(chance)
        # Time to choose.
        if len(filtered_list) < 1:
            # No items. Boo.
            logging.info("Filters removed all potential modifiers for item %s." % itemid)
            return None
        modifier = random.choices(filtered_list, weight_list)[0]
        return modifier
                        
# Now for our item class!
class Item:
    def __init__(self, rarity=None, category=None, group=None, subtype=None,
        damage_type=None, properties=None, material_type=None):
        self.emptyValues()
        self.category = self.getCategory(category)
        if self.category in WONDROUS_ITEMS:
            # We're dealing with a wondrous item.
            self.wondrous = True
        self.rarity = self.getRarity(rarity)
        self.id = self.getID(group, subtype, damage_type, properties,
            material_type, rarity=self.rarity)
        if self.id is not None:
            self.getValues()
        self.generateEffects()
        self.rarity = self.updateRarity()
        # Max effects might change depending on rarity changes, so update it.
        self.max_effects = cfg.getInt("General", "max_effects_%s" % self.rarity)
    
    def emptyValues(self):
        # Sets the basic values. Every item must have all of these.
        # General item things.
        self.source = "Generated Item"
        self.rarity = None
        self.category = None
        self.item_name = ""
        self.id = None
        self.charges = 0
        self.recharge = None
        self.recharge_mod = None
        self.destroy_on_empty = False
        self.wondrous = False
        self.material = None
        self.group = None
        self.subtype = None
        self.material_type = []
        self.random_lists = {}
        self.modifiers = []
        self.choices = {}
        self.spells = {}
        self.prefixes = []
        self.suffixes = []
        self.curse = None # Not implemented yet
        self.item_attunement = None
        self.item_bonus = 0
        self.item_description = None
        self.item_properties = []
        self.attunement = None
        self.enhancement = 0
        self.item_weight = 0
        self.quantity = None
        # Weapon things.
        self.damage = None
        self.damage_type = None
        self.versatile_damage = None
        self.short_range = None
        self.long_range = None
        # Armor things.
        self.ac = None
        self.min_str = None
        self.stealth_penalty = None
        self.max_prefix = None
        self.max_suffix = None
        self.can_have_enh = False
    
    def getValues(self):
        # Gets our values.
        # Several of these won't exist in many cases. But they'll return as None
        # Which is precisely what we want.
        self.group = item_data.getList(self.id, "group")
        self.subtype = item_data.getList(self.id, "item_subtype")
        self.material_type = item_data.getList(self.id, "material_type")
        self.random_lists = self.getRandomLists()
        self.choices = self.chooseRandom()
        self.modifiers = self.getItemModifiers()
        self.item_attunement = self.getItemAttunement()
        self.item_bonus = item_data.getInt(self.id, "bonus")
        if self.item_bonus is None:
            self.item_bonus = 0
        self.item_weight = item_data.getFloat(self.id, "weight")
        if self.item_weight is None:
            self.item_weight = 0
        self.item_properties = item_data.getList(self.id, "properties")
        self.quantity = item_data.getInt(self.id, "quantity")
        # Weapon
        self.damage = item_data.get(self.id, "damage")
        self.damage_type = item_data.get(self.id, "damage_type")
        self.versatile_damage = item_data.get(self.id, "versatile_damage")
        self.short_range = item_data.getInt(self.id, "short_range")
        self.long_range = item_data.getInt(self.id, "long_range")
        # Armor (& Shield)
        self.ac = item_data.getInt(self.id, "armor_class")
        self.min_str = item_data.getInt(self.id, "required_strength")
        if self.category not in WONDROUS_ITEMS:
            self.max_prefix = cfg.getInt("General", "max_prefix")
            self.max_suffix = cfg.getInt("General", "max_suffix")
        if self.category in ENH_ITEMS:
            self.can_have_enh = True
        # Name and Description. Always last, since sometimes they depend on things.
        self.item_name = self.getString("name")
        self.item_description = self.getString("Description")
    
    def getMaxEffects(self):
        return cfg.getInt("General", "max_effects_%s" % self.rarity)
    
    def isMagic(self):
        # Checks to see if the item is magic in any way.
        # First, ourselves. Presume non-magical.
        magic = item_data.getBool(self.id, "is_magic")
        if magic is None:
            magic = False
        if self.enhancement > 0:
            magic = True
        if self.material is not None:
            if self.material.id is not None:
                # Materials are also non-magical unless noted otherwise.
                data = item_data.getBool(self.material.id, "is_magic")
                if data:
                    magic = True
        for effect in self.prefixes + self.suffixes:
            data = item_data.getBool(effect.id, "is_magic")
            # Effects are presumed to be magical unless noted otherwise.
            if data is None or data is True:
                magic = True
        # At this point, magic can only be True or False.
        # Probably true, though.
        return magic

    def getCategory(self, category):
        # Checks if our category is valid. If not, it generates one.
        if category not in ITEM_TYPES:
            if category is not None:
                logging.debug("Category %s invalid. Choosing one." % str(category))
            category = random.choices(ITEM_TYPES, ITEM_WEIGHTS)[0]
        return category
    
    def getRarity(self, rarity):
        # Validates our rarity. If it's bad, it selects one for us.
        if rarity in RARITY_LIST:
            return rarity
        else:
            if rarity is not None:
                logging.debug("Rarity %s invalid. Choosing one." % str(rarity))
            return random.choice(RARITY_LIST)           
    
    def rerollRandom(self):
        # Re-chooses random spells and random list choices.
        self.spells = {}
        self.getItemModifiers() # This re-does the spells.
        self.choices = self.chooseRandom()
        self.item_name = self.getString("name")
        self.item_description = self.getString("Description")
    
    def getItemModifiers(self):
        # Returns the pre-programmed effects, if they're available.
        modifiers = []
        spells = {}
        mods = item_data.get(self.id, "modifiers")
        if mods is not None:
            # We have some modifiers. Now parse them.
            mods = mods.split(";")
            for mod in mods:
                # We're not validating, just parsing.
                if mod.find("(") == -1:
                    # No arguments. Just put it into the list.
                    # We want it as a list for ease of use later.
                    modifiers.append([mod.strip()])
                else:
                    p1 = mod.find("(")
                    p2 = mod.find(")")
                    modlist = []
                    modlist.append(mod[:p1]) # The command.
                    modlist += mod[p1+1:p2].split(",") # Split the arguments
                    if modlist[0].lower().startswith("randspell"):
                        # We have a random spell. This we parse here, and
                        # not add it to the list.
                        self.getSpell(modlist)
                    else:
                        modifiers.append(modlist)
        return modifiers
    
    def getRandomLists(self):
        # Retrieves the random lists.
        rlists = {}
        for option in item_data.config[self.id]:
            # Check each of our options.
            if option.startswith("random_list_") and len(option) > 10:
                # A random list! With an identifier!
                random = item_data.getList(self.id, option)
                rlists["%s" % option[12:]] = random
        return rlists
    
    def chooseRandom(self):
        # Each item has a number of joinlists. These are which random lists
        # share a choice. By default, they all have the same one. The first
        # item in a list, if it starts with "@@", designates the group.
        # Figure out which groups we have.
        joingroups = {"default":[]}
        for r in self.random_lists:
            first = self.random_lists[r][0]
            if first.startswith("@@"):
                if first not in joingroups:
                    joingroups[first] = [r]
                else:
                    joingroups[first] += [r]
            else:
                joingroups["default"] += [r]
        if len(joingroups["default"]) == 0:
            # Our default group is empty. Remove it.
            joingroups.pop("default", None)
        choices = {}
        # Now record our choices for each group.
        for group in joingroups:
            length = -1
            choice = -1
            for rlist in joingroups[group]:
                if len(self.random_lists[rlist]) < length or length == -1:
                    length = len(self.random_lists[rlist])
            if group == "default":
                choice = random.randint(0, length-1)
            else:
                # Ignore the first item as it's the group ID.
                choice = random.randint(1, length-1)
            # Now assign this group's items to choices.
            for rlist in joingroups[group]:
                choices[rlist] = choice
        return choices

    def getSpell(self,info):
        # Adds the designated spell to the modifier's spell list.
        id = info[0][9:] # The identifier of the spell.
        levels = []
        notlevels = []
        for i in info[1:]:
            try:
                # Is this an int?
                i = int(i)
                levels.append(i)
            except:
                # It is *not* an int.
                # It may be a colon-separated list (legacy)
                # Or maybe just a string. Either way, this works.
                notlevels += i.split(":")
        # Figure out if we have a level identifier
        level = None
        if len(levels) == 1:
            level = levels[0]
        else:
            level = (min(levels), max(levels))
        # Now for our school.
        schools = []
        classlist = []
        for item in notlevels:
            if item in spells.CLASSES:
                classlist.append(item)
            elif item in spells.SPELL_SCHOOLS:
                schools.append(item)
        if len(schools) == 0:
            schools = None
        if len(classlist) == 0:
            classlist = None
        spell = spells.Spell(schools=schools, level=levels, classlist=classlist,
            itemtype=self.category)
        self.spells[id] = spell
        return
    
    def getItemAttunement(self):
        # Returns the attunement requirements of a given modifier.
        # Doesn't worry about attunement joining restrictions. Those are only
        # for filtering, and aren't used from here on out.
        attune = item_data.get(self.id, "attunement")
        if attune == "true" or attune == "desc":
            # We have some type of attunement.
            # See if we have any requirements.
            attunereq = item_data.get(self.id, "attunement_requirements")
            if attunereq is None:
                # No requirements, just general attunement
                return True
            elif attunereq is not None and attune == "desc":
                # We have a description. Return the whole thing.
                return attunereq
            else:
                # We have a list of requirements.
                return  attunereq.split(";")
    
    def getString(self, strID):
        # Grabs the specified string, and replaces any variables in it.
        workstr = item_data.get(self.id, strID)
        workstr = self.replaceItemVars(workstr)
        return workstr
        
    def replaceItemVars(self, workstr):
        # Replaces the randomly generated spells and lists.
        if workstr is None or workstr == "":
            return ""
        # First, replace our random choices.
        for rand in self.choices:
            choice = self.choices[rand]
            find = "@R%s" % rand
            replace = self.random_lists[rand][choice]
            workstr = workstr.replace(find, replace)
        for spell in self.spells:
            find = "@spell%s" % spell
            replace = self.spells[spell].name
            workstr = workstr.replace(find, replace)
        return workstr
    
    def getBonus(self):
        # Returns the item's current bonus
        bonus = self.item_bonus
        if self.material is not None:
            bonus += self.material.bonus
        for effect in self.prefixes + self.suffixes:
            if effect is not None:
                bonus += effect.bonus
        bonus += self.enhancement
        return bonus
    
    def getMaxBonus(self, rarity):
        # Returns the maximum bonus for the current rarity.
        max_bonus = cfg.getInt("General", "max_bonus_%s" % rarity)
        return max_bonus
    
    def getEmptyMaterial(self):
        # Replaces the material with an empty version, AKA "No material"
        empty_mat = Modifier(category="material", force_none=True)
        return empty_mat
    
    def getMaterial(self):
        # This gets our material, or gets a new material
        # It does not assign it!
        budget = cfg.getInt("General", "max_bonus_%s" % self.rarity) - self.getBonus()
        if self.material is not None:
            # Take into account our current material.
            budget += self.material.bonus
        min_budget = cfg.getInt("Effects","budget_range_material")
        if min_budget is None:
            min_budget = -10
        else:
            if min_budget < 0:
                min_budget = 0
            min_budget = budget - min_budget
        # We want to make sure we don't conflict.
        all_effects = []
        all_effects += self.prefixes + self.suffixes
        all_properties = []
        all_properties += self.getProperties()
        if self.enhancement > 0:
            all_properties.append("enhancement")
        for effect in all_effects:
            all_properties += effect.properties
        new_mat = Modifier(category="material", itemtype=self.category,
            itemsubtype=self.subtype, damagetype=self.getDamageType(),
            materialtype=self.material_type, itemgroup=self.getGroups(),
            properties=all_properties, bonus=(min_budget, budget),
            effects=all_effects, itemid=self.id, rarity=self.rarity)
        while new_mat.id is None and min_budget > -10:
            # Work our way down
            minbudget -= 1
            new_mat = Modifier(category="material", itemtype=self.category,
                itemsubtype=self.subtype, damagetype=self.getDamageType(),
                materialtype=self.material_type, itemgroup=self.getGroups(),
                properties=all_properties, bonus=(min_budget, budget),
                effects=all_effects, itemid=self.id, rarity=self.rarity)
        if self.material is not None:
            # We're replacing a material. Try and make sure it's not the same one.
            tries = 10
            while new_mat.id == self.material.id and tries > 0:
                new_mat = Modifier(category="material", itemtype=self.category,
                    itemsubtype=self.subtype, damagetype=self.getDamageType(),
                    materialtype=self.material_type, itemgroup=self.getGroups(),
                    properties=all_properties, bonus=(min_budget, budget),
                    effects=all_effects, itemid=self.id, rarity=self.rarity)
                tries -= 1
        return new_mat
    
    def replaceAffix(self, affix):
        # Replaces the given affix.
        if affix == self.material:
            # We're replacing our material. Neat. Also easy.
            self.material = self.getMaterial()
            return True
        # OK, so our effects. Find out which one it is
        index = -1
        if affix.affix == "prefix":
            for r in range(0, len(self.prefixes)):
                if affix == self.prefixes[r]:
                    index = r
                    break
        elif affix.affix == "suffix":
            for r in range(0, len(self.suffixes)):
                if affix == self.suffixes[r]:
                    index = r
                    break
        if index == -1:
            # Affix not found.
            return False
        new_affix = self.getAffix(affix.affix, effect=affix)
        if affix.affix == "prefix":
            self.prefixes[index] = new_affix
        elif affix.affix == "suffix":
            self.suffixes[index] = new_affix
        return True
    
    def getAffix(self, affix, effect=None):
        # This works similar to our material grabber, but gets an effect
        # of the specified affix (prefix/suffix). If an effect is supplied, then
        # it uses that uses that budget.
        budget = cfg.getInt("General", "max_bonus_%s" % self.rarity) - self.getBonus()
        if effect is not None:
            budget += effect.bonus
        minbudget = cfg.getInt("Effects","budget_range")
        if self.category == "scroll":
            # We want scrolls to be really close to their maximum.
            minbudget = cfg.getInt("Effects", "scroll_budget_range")
        if minbudget is None:
            minbudget = -10
        else:
            if minbudget < 0:
                minbudget = 0
            minbudget = budget - minbudget
        # Make sure we're not conflicting with anything.
        all_effects = []
        for eff in self.prefixes + self.suffixes:
            if eff != effect:
                all_effects.append(eff)
        if self.material is not None:
            if self.material.id is not None:
                all_effects.append(self.material)
                material_type = self.material.material_type
            else:
                material_type = self.material_type
        else:
            material_type = self.material_type
        all_properties = []
        all_properties += self.getProperties() # Make sure we've added any!
        item_type_conflict = None
        if self.category == "staff":
            # To make staffs be more unique than, say, just a magical quarterstaff
            # We can sometimes request a "Non-weapon" effect.
            no_weapon_chance = cfg.getInt("General", "staff_effect_chance")
            randchoice = random.randint(1,100)
            if randchoice <= no_weapon_chance:
                item_type_conflict = "weapon"
        if self.enhancement > 0:
            all_properties.append("enhancement")
        # We can use our previously assembled list of effects conveniently now
        for effect in all_effects:
            all_properties += effect.properties
        new_effect = Modifier(category="effect", affix=affix, itemtype=self.category,
            itemsubtype=self.subtype, damagetype=self.getDamageType(),
            materialtype=material_type, itemgroup=self.getGroups(),
            properties=all_properties, bonus=(minbudget, budget),
            effects=all_effects, itemid=self.id, rarity=self.rarity,
            itemtypeconflict=item_type_conflict)
        while new_effect.id is None and minbudget > -10:
            minbudget -= 1
            new_effect = Modifier(category="effect", affix=affix, itemtype=self.category,
            itemsubtype=self.subtype, damagetype=self.getDamageType(),
            materialtype=material_type, itemgroup=self.getGroups(),
            properties=all_properties, bonus=(minbudget, budget),
            effects=all_effects, itemid=self.id, rarity=self.rarity,
            itemtypeconflict=item_type_conflict)
        if effect is not None:
            while new_effect.id == effect.id:
                # Don't give us the same one!
                new_effect = Modifier(category="effect", affix=affix, itemtype=self.category,
                itemsubtype=self.subtype, damagetype=self.getDamageType(),
                materialtype=material_type, itemgroup=self.getGroups(),
                properties=all_properties, bonus=(minbudget, budget),
                effects=all_effects, itemid=self.id, rarity=self.rarity,
                itemtypeconflict=item_type_conflict)
        new_effect.affix = affix
        return new_effect
    
    def getMaxEnhancement(self):
        weights = cfg.getList("Effects", "enh_weights")
        return len(weights)
    
    def getEnhancement(self, fill=False):
        # Either generates an enhancement bonus, or fills as much of the budget
        # as it can with bonus.
        # First, check to see if we're able to have bonuses.
        if not self.can_have_enh:
            # Wondrous items don't get enhancements.
            return 0
        # Figure out our enhancement limits.
        enh_weight = cfg.getList("Effects", "enh_weights")
        # Int-ify it
        enh_weight = [int(weight) for weight in enh_weight]
        max_enh = len(enh_weight)
        budget = cfg.getInt("General", "max_bonus_%s" % self.rarity) - self.getBonus()
        # Add our current enhancement bonus in if it exists.
        budget += self.enhancement
        if budget == 0 or max_enh == 0:
            # Nope, sorry, no enhancement for us today.
            return 0
        if fill:
            # We're filling things here, no need to worry about chances and such.
            if budget >= max_enh:
                return max_enh
            else:
                return budget
        # OK, at this point we need to figure out our bonus.
        # Trim off any excess ones we won't be using.
        enh_weight = enh_weight[:budget]
        enh_range = range(1, min(budget+1, max_enh+1))
        enhance = random.choices(enh_range, enh_weight)[0]
        return enhance
    
    def getBudget(self):
        # Returns our current available bonus budget
        max = cfg.getInt("General", "max_bonus_%s" % self.rarity)
        current = self.getBonus()
        return max - current
    
    def updateRarity(self):
        # Returns our actual rarity.
        # We determine this by maximums.
        common_max = cfg.getInt("General", "max_bonus_common")
        uncommon_max = cfg.getInt("General", "max_bonus_uncommon")
        rare_max = cfg.getInt("General", "max_bonus_rare")
        veryrare_max = cfg.getInt("General", "max_bonus_veryrare")
        # Don't worry about legendary. If it's above the veryrare amount, well.
        bonus = self.getBonus()
        if bonus <= common_max:
            return "common"
        elif bonus <= uncommon_max:
            return "uncommon"
        elif bonus <= rare_max:
            return "rare"
        elif bonus <= veryrare_max:
            return "veryrare"
        else:
            return "legendary"
    
    def generateEffects(self):
        # Determines which effects (Prefix, Suffix, Material, Enhancement) are
        # added to the item. It determines the total available budget and adds
        # effects until there is no more budget or until we have no more room.
        # This is intended to be able to be run if, say, things are removed or
        # the item's rarity is changed, etc. It does not replace anything by
        # itself.
        # Set ourselves up so we don't try to generate things needlessly.
        max_effects = cfg.getInt("General", "max_effects_%s" % self.rarity)
        enh_weight = cfg.getInt("General", "enh_chance")
        if self.enhancement > 0 or self.category in WONDROUS_ITEMS:
            enh_weight = 0
        mat_weight = cfg.getInt("General", "material_chance")
        if self.material is not None:
            if self.material.id is not None:
                # We already have a material.
                mat_weight = 0
        # Prefixes and suffixes.
        # We deal with if we have too many of these later.
        pre_weight = cfg.getInt("General", "prefix_chance")
        suf_weight = cfg.getInt("General", "suffix_chance")
        max_prefix = cfg.getInt("General", "max_prefix")
        if max_prefix is None:
            max_prefix = 1
        max_suffix = cfg.getInt("General", "max_suffix")
        if max_suffix is None:
            max_suffix = 1
        ignore_affix_limit = cfg.getBool("WondrousItems", "wi_ignore_affix_limit")
        if ignore_affix_limit is None:
            ignore_affix_limit = False
        # Check to see if we have to pay attention to these pesky limits.
        if self.category not in WONDROUS_ITEMS or not ignore_affix_limit:
            # We don't have to worry about extra effects.
            if len(self.prefixes) >= max_prefix:
                pre_weight = 0
            if len(self.suffixes) >= max_suffix:
                suf_weight = 0
        # And our total maximum.
        max_affix = cfg.getInt("General", "max_effects_%s" % self.rarity)
        if len(self.prefixes) + len(self.suffixes) >= max_affix:
            # Too many effects.
            pre_weight = 0
            suf_weight = 0
        # Simple "No Effect Chance". These items will be material + enhancement
        no_effect_chance = cfg.getInt("General", "no_effect_chance_%s" % self.rarity)
        wi_force_effect = cfg.getBool("WondrousItems", "wi_force_effect")
        staff_wand_force_effect = cfg.getBool("General", "staff_wand_force_effect")
        if (self.category in WONDROUS_ITEMS and not wi_force_effect) \
            or (self.category in ["staff", "wand"] and not staff_wand_force_effect) \
            or self.category in ENH_ITEMS:
            rand = random.randint(1,100)
            if rand <= no_effect_chance:
                # Sorry, friend, you don't get anything fancy today.
                pre_weight = 0
                suf_weight = 0
        # And for our 0 (or lower) cost items.
        max_no_bonus = cfg.getInt("General", "max_no_bonus")
        if max_no_bonus < 1:
            max_no_bonus = 1
        no_bonus_count = 0
        # OK. Now on to generating things.
        last_effect = None
        while (pre_weight + suf_weight + enh_weight + mat_weight) > 0:
            ids = ["enh", "mat", "pre", "suf"]
            weights = [enh_weight, mat_weight, pre_weight, suf_weight]
            choice = random.choices(ids, weights)[0]
            if choice == "enh":
                self.enhancement = self.getEnhancement()
                enh_weight = 0
                last_effect = "enh"
            elif choice == "mat":
                self.material = self.getMaterial()
                mat_weight = 0
                last_effect = "mat"
            elif choice == "pre":
                if last_effect == "pre":
                    last_effect = None
                else:
                    prefix = self.getAffix("prefix")
                    if prefix.id is None:
                        # One None, future Nones. Prevent that.
                        pre_weight = 0
                        last_effect = None
                    elif prefix.id in self.getEffectIDs():
                        # We already have this. Ignore it.
                        last_effect = None
                    elif prefix.bonus <= 0 and no_bonus_count >= max_no_bonus:
                        # We already have our maximum number of 0-bonus effects.
                        budget = self.getBudget()
                        if budget < 1:
                            pre_weight = 0
                        last_effect = None
                    else:
                        self.prefixes.append(prefix)
                        last_effect = "pre" # Don't generate a prefix again next time.
                        if (pre_weight + suf_weight + enh_weight + mat_weight) == pre_weight:
                            last_effect = None # Unless that's the ONLY thing we can do.
                        if prefix.bonus <= 0:
                            no_bonus_count += 1
                        if self.category not in WONDROUS_ITEMS or not ignore_affix_limit:
                            if len(self.prefixes) >= max_prefix:
                                pre_weight = 0
            elif choice == "suf":
                if last_effect == "suf":
                    last_effect = None
                else:
                    suffix = self.getAffix("suffix")
                    if suffix.id is None:
                        # If we get one "None", then any furthers will be none.
                        suf_weight = 0
                        last_effect = None
                    elif suffix.id in self.getEffectIDs():
                        # We already have this. Ignore it.
                        last_effect = None
                    elif suffix.bonus <= 0 and no_bonus_count >= max_no_bonus:
                        # Same as above.
                        budget = self.getBudget()
                        if budget < 1:
                            suf_weight = 0
                        last_effect = None
                    else:
                        self.suffixes.append(suffix)
                        last_effect = "suf"
                        # Same as above.
                        if (pre_weight + suf_weight + enh_weight + mat_weight) == suf_weight:
                            last_effect = None
                        if suffix.bonus <= 0:
                            no_bonus_count += 1
                        if self.category not in WONDROUS_ITEMS or not ignore_affix_limit:
                            if len(self.suffixes) >= max_suffix:
                                suf_weight = 0
            if len(self.prefixes) + len(self.suffixes) >= max_affix:
                pre_weight = 0
                suf_weight = 0
        # OK, so. Now we have one more step.
        if self.category not in WONDROUS_ITEMS:
            # We have something that can have an enhancement bonus.
            budget = self.getBudget()
            max_enh = len(cfg.getList("Effects", "enh_weights"))
            if self.enhancement < max_enh and budget > 0:
                # We have more room for enhancement. Fill it.
                self.enhancement = self.getEnhancement(fill=True)
        # That should be it.
        budget = self.getBudget()
        return budget
            
    def getEffectIDs(self):
        # Returns the IDs of all effects (prefixes and suffixes) on the item
        ids = []
        for effect in self.prefixes + self.suffixes:
            ids.append(effect.id)
        return ids
            
    def cleanEffects(self):
        # Removes all current effects and resets them to their default values.
        self.prefixes = []
        self.suffixes = []
        self.material = None
        self.enhancement = 0
        return
    
    def getAllModifiers(self):
        # Gathers all the modifiers - Of the item, of the effects,etc
        modifiers = []
        modifiers += self.modifiers
        if self.material is not None:
            modifiers += self.material.modifiers
        for effect in self.prefixes + self.suffixes:
            modifiers += effect.modifiers
        return modifiers
    
    def getDamage(self):
        # Returns the damage dice, and versatile damage dice.
        damage = self.damage
        vers = self.versatile_damage
        if self.damage is None:
            # We can't have versatile damage without regular damage.
            # That's just a two-handed weapon.
            return None, None
        # Add (Or subtract) our modifiers.
        for mod in self.getAllModifiers():
            if mod[0] == "changedmgdice" and len(mod) > 1:
                amt = int(mod[1])
                if amt < 0:
                    for r in range(0, amt):
                        damage = changeDiceSize(damage, increase=False)
                elif amt > 0:
                    for r in range(0, amt):
                        damage = changeDiceSize(damage, increase=True)
            if mod[0] == "changeversatile" and len(mod) > 1:
                amt = int(mod[1])
                if amt < 0:
                    for r in range(0, amt):
                        vers = changeDiceSize(vers, increase=False)
                elif amt > 0:
                    for r in range(0, amt):
                        vers = changeDiceSize(vers, increase=True)
        # OK, that should be it. Simple enough.
        return damage, vers
    
    def getProperties(self):
        # Typically only used for weapons, but hey. Never know what people do.
        properties = []
        properties += self.item_properties
        modifiers = self.getAllModifiers()
        # Add modifiers. We'll deal with duplicates later
        for mod in modifiers:
            # Add properties, no conditions.
            if mod[0] == "addproperty" and len(mod) > 1:
                if mod[1] not in ["versatile", "thrown", "ammunition"]:
                    # We explicitly do not fiddle with those, due to extra baggage
                    properties.append(mod[1])
            # Add modifiers *if*
            if mod[0] == "addpropertyif" and len(mod) > 3:
                # This has three parts. Modifier to add, Modifier to check,
                # And if the check is true or false.
                prop = mod[1]
                if prop not in ["versatile", "thrown", "ammunition"]:
                    check_prop = mod[2]
                    check = mod[3].lower()
                    if check == "false" or check == "0":
                        check = False
                    else:
                        check = True # Default to checking if we have it.
                    if check_prop in properties and check is True:
                        properties.append(prop)
                    if check_prop not in properties and check is False:
                        properties.append(prop)
        # OK, now let's deal with duplicates.
        properties = set(properties)
        # Now for removal.
        for mod in modifiers:
            # Remove properties, no conditions.
            if mod[0] == "removeproperty" and len(mod) > 1:
                if mod[1] not in ["versatile", "thrown", "ammunition"]:
                    # We explicitly do not fiddle with those, due to extra baggage
                    properties.remove(mod[1])
            # Remove modifiers *if*
            if mod[0] == "removepropertyif" and len(mod) > 3:
                # Functions like add property if, above, but removes.
                prop = mod[1]
                if prop not in ["versatile", "thrown", "ammunition"]:
                    check_prop = mod[2]
                    check = mod[3].lower()
                    if check == "false" or check == "0":
                        check = False
                    else:
                        check = True # Default to checking if we have it.
                    if check_prop in properties and check:
                        properties.remove(prop)
                    elif check_prop not in properties and not check:
                        properties.remove(prop)
        # Back into a list.
        properties = list(properties)
        # And return it.
        return properties
    
    def getWeight(self):
        # Returns the weight of the item.
        if self.item_weight is None:
            return None
        weight = self.item_weight
        modifiers = self.getAllModifiers()
        # We have two modifiers to worry about. Addweight and changeweight.
        # Do addweight first.
        for mod in modifiers:
            if mod[0] == "addweight" and len(mod) > 1:
                weight += int(mod[1])
        # And now multiply weight.
        for mod in modifiers:
            if mod[0] == "modifyweight" and len(mod) > 1:
                weight = weight * float(mod[1])
        # Make sure we're not breaking too many laws of physics.
        if weight < 0.01:
            weight = 0.01
        # And send it back.
        return weight
    
    def getAC(self):
        # Returns the armor's AC bonus.
        if self.ac is None:
            return None
        ac = self.ac
        for mod in self.getAllModifiers():
            if mod[0] == "changeac" and len(mod) > 1:
                ac += int(mod[1])
        # AC of 10 may as well not exist, so keep a minimum of 11.
        if ac < 11:
            ac = 11
        return ac
    
    def getMinStr(self):
        # Returns the minimum strength required to use the armor without penalty
        if self.min_str is None:
            return None
        min_str = self.min_str
        mods = self.getAllModifiers()
        # First, check if anything sets it.
        for mod in mods:
            if mod[0] == "setstrength" and len(mod) > 1:
                min_str = int(mod[1])
        # Now, for modifications.
        for mod in mods:
            if mod[0] == "adjstrength" and len(mod) > 1:
                min_str += int(mod[1])
        # Make sure we keep things sane. If it's this low, we can ignore it.
        if min_str < 1:
            min_str = None
        return min_str
    
    def getGroups(self):
        # Returns any groups (Simple, Melee, Heavy for amror, etc) the item has.
        # Doesn't check if it SHOULD have it, though.
        groups = set(self.group) # Make sure there's no duplicates.
        mods = self.getAllModifiers()
        # First, see if anything adds a group.
        for mod in mods:
            if mod[0] == "addgroup" and len(group) > 1:
                groups.add(mod[1])
        # And now, for removal.
        for mod in mods:
            if mod[0] == "removegroup" and len(group) > 1:
                if mod[1] in groups:
                    groups.remove(mod[1])
        # Now make sure we return a list.
        groups = list(groups)
        return groups
    
    def getStealthPenalty(self):
        # Returns if the armor gives a penalty to stealth.
        if self.category != "armor":
            return None
        penalty = self.stealth_penalty
        if penalty is None:
            penalty = False
        for mod in self.getAllModifiers():
            if mod[0] == "stealthpenalty" and len(mod) > 1:
                if mod[1].lower() == "true":
                    penalty = True
                elif mod[1].lower() == "false":
                    penalty = False
        return penalty
    
    def getDamageType(self):
        # Returns the damage type.
        # If multiple effects change it, it'll be the last one that does.
        # Which is likely the last suffix.
        if self.damage_type is None:
            return None
        dmgtype = self.damage_type
        # We only need to check the modifiers once for this one!
        for mod in self.getAllModifiers():
            if mod[0] == "changedmgtype" and len(mod) > 1:
                dmgtype = mod[1]
        return dmgtype
    
    def getRange(self):
        # Returns the short and long ranges of the weapon
        range = []
        range.append(self.short_range)
        range.append(self.long_range)
        modifiers = self.getAllModifiers()
        # First, add to our ranges.
        for mod in modifiers:
            if mod[0] == "addrange1" and len(mod) > 1:
                if range[0] is not None:
                    range[0] += int(mod[1])
            if mod[0] == "addrange2" and len(mod) > 1:
                if range[1] is not None:
                    range[1] += int(mod[1])
        # And now multiply.
        for mod in modifiers:
            if mod[0] == "multiplyrange1" and len(mod) > 1:
                if range[0] is not None:
                    range[0] = range[0] * float(mod[1])
            if mod[0] == "multiplyrange2" and len(mod) > 1:
                if range[1] is not None:
                    range[1] = range[1] * float(mod[1])
        # And that's all folks!
        return range
    
    def getQuantity(self):
        # Gets the item's quantity, adjusted by any modifiers.
        if self.quantity is None:
            return None # Cannot modify nothing!
        qty = self.quantity
        modifiers = self.getAllModifiers()
        # Deal with "Set quantity" first.
        for mod in modifiers:
            if mod[0] == "setquantity" and len(mod) > 1:
                if int(mod[1]) > qty:
                    qty = int(mod[1])
        # And now for "add quantity"
        for mod in modifiers:
            if mod[0] == "addquantity" and len(mod) > 1:
                qty += int(mod[1])
        # And finally, multiplication
        for mod in modifiers:
            if mod[0] == "modifyquantity" and len(mod) > 1:
                qty = qty * float(mod[1])
        # Tidy up.
        qty = round(qty)
        min_quantity = cfg.getInt("General", "min_quantity")
        if min_quantity is None:
            min_quantity = 1
        if min_quantity < 1:
            min_quantity = 1
        if qty < min_quantity:
            qty = min_quantity
        return qty
        
    def getCharges(self):
        # Returns total charges, daily recharge, and chance to destroy on last use
        charges = 0
        recharge = ["",None]
        destroy = False
        modifiers = self.getAllModifiers()
        # First, our base charges
        # Also check if any of them set the destroy on empty trigger
        for mod in modifiers:
            if mod[0] == "charges" and len(mod) > 1:
                if int(mod[1]) > charges:
                    charges = int(mod[1])
            if mod[0] == "destroyonempty":
                destroy = True
        # Now for our modification of charges.
        for mod in modifiers:
            if mod[0] == "modifycharges" and len(mod) > 1:
                if charges > 0:
                    charges += int(mod[1])
                    if charges < 1:
                        # Always need to have at least one charge.
                        charges = 1
        # Finally, let's do our recharge
        for mod in modifiers:
            if mod[0] == "recharge" and len(mod) > 1:
                if recharge[0] == "":
                    recharge[0] = mod[1]
                else:
                    recharge[0] = compareDice(recharge[0], mod[1])
                if len(mod) > 2:
                    if recharge[1] is None:
                        recharge[1] = int(mod[2])
                    elif int(mod[2]) > recharge[1]:
                        recharge[1] = int(mod[2])
        # Let's set our recharge into a nice string.
        rechargestr = recharge[0]
        if rechargestr is None:
            rechargestr = ""
        if recharge[1] is not None:
            if recharge[1] < 0:
                rechargestr += str(recharge[1])
            elif recharge[1] > 0:
                rechargestr += "+%d" % recharge[1]
        # And send everything back.
        if charges > 0:
            return charges, rechargestr, destroy
        else:
            return None
    
    def getAttunement(self):
        # Returns the string of if the item requires attunement or not.
        attune = False
        alist = []
        adesc = []
        if self.item_attunement is not None:
            if self.item_attunement is True:
                attune = True
            elif type(self.item_attunement) is str:
                attune = True
                adesc.append(self.item_attunement)
            elif type(self.item_attunement) is list:
                attune = True
                alist += self.item_attunement
        for effect in self.prefixes + self.suffixes + [self.material]:
            if effect.attunement is not None:
                if effect.attunement is True:
                    attune = True
                elif type(effect.attunement) is str:
                    attune = True
                    adesc.append(effect.attunement)
                elif type(effect.attunement) is list:
                    attune = True
                    alist += effect.attunement
        # Now we have our list.
        if not attune:
            # No attunement required.
            return ""
        if attune:
            if len(alist) == 0 and len(adesc) == 0:
                # Just general attunement
                return "(requires attunement)"
            elif len(adesc) > 0:
                # Description will simply override
                # It shouldn't happen in the first place, but it's good to be sure
                adesc = " or ".join(adesc)
                adesc = "(requires attunement %s)" % adesc
                return adesc
            elif len(alist) > 0 and len(adesc) == 0:
                if len(alist) == 1:
                    return "(requires attunement by a %s)" % alist[0]
                elif len(alist) == 2:
                    alist = " or ".join(alist)
                    return "(requires attunement by a %s)" % alist
                else:
                    astr = ", ".join(alist[:-1])
                    astr += ", or %s" % alist[-1]
                    return "(requires attunement by a %s)" % astr

    def getInfo(self):
        # Returns the item type, subtype, rarity, attunement, and magical status
        # And puts them into a single string (A stringle?).
        desc = ""
        magic = "non-magical"
        if self.isMagic():
            magic = "magical"
        if self.category in ("weapon", "armor", "ammunition"):
            desc += "%s (%s %s), " % (self.category, magic, self.item_name.lower())
        elif self.category in ("potion", "ring", "rod", "scroll", "staff", "wand"):
            desc += "%s %s, " % (magic, self.category)
        elif self.category == "shield":
            # The DMG treats shields as armor.
            desc += "armor (%s shield), " % magic
        else:
            desc += "wondrous item (%s %s), " % (magic, self.category)
        # Now for our rarity
        desc += "%s " % self.rarity.replace("veryrare", "very rare")
        # And attunement
        desc += self.getAttunement()
        desc = self.replaceVars(desc)
        desc = desc.capitalize()
        return desc
    
    def replaceVars(self, workstr, lowercase=False):
        # Replaces given variables in the provided string.
        if "@" not in workstr:
            # No variables found.
            return workstr
        workstr = workstr.replace("@enh", str(self.enhancement))
        if lowercase:
            workstr = workstr.replace("@item", self.item_name.lower())
            if self.material.id is not None:
                workstr = workstr.replace("@material", self.material.name.lower())
        else:
            workstr = workstr.replace("@item", self.item_name)
            if self.material.id is not None:
                workstr = workstr.replace("@material", self.material.name)
        workstr = workstr.replace("@category", self.category)
        workstr = workstr.replace("@weight", str(self.getWeight()))
        if self.getCharges() is not None:
            workstr = workstr.replace("@charges", str(self.getCharges()[0]))
            workstr = workstr.replace("@recharge", str(self.getCharges()[1]))
        if self.damage is not None:
            # Damage type *must* come before damage. Otherwise, well. You get
            # weird things.
            workstr = workstr.replace("@dmgtype", str(self.getDamageType()))
            workstr = workstr.replace("@dmg", str(self.getDamage()[0]))
        if self.versatile_damage is not None:
            workstr = workstr.replace("@vdmg", str(self.getDamage()[1]))
        if self.ac is not None:
            workstr = workstr.replace("@ac", str(self.getAC()))
            workstr = workstr.replace("@rawac", str(self.ac))
        if self.min_str is not None:
            workst = workstr.replace("@minstr", str(self.getMinStr()))
        # Some other housekeeping
        workstr = workstr.replace("\\n", "\n")
        while "\n\n" in workstr:
            workstr = workstr.replace("\n\n", "\n")
        while "  " in workstr:
            workstr = workstr.replace("  ", " ")
        workstr = workstr.strip()
        return workstr
    
    def getDescription(self):
        # Gets the description. Starts with the charges, then the item, then
        # the material, then the effects.
        desc = []
        charges = self.getCharges()
        if charges is not None:
            chargestr = ""
            if charges[0] == 1:
                chargestr = cfg.get("Effects", "one_charge_description")
            else:
                chargestr = cfg.get("Effects", "multi_charge_description")
            if charges[1] != "":
                chargestr += " %s" % cfg.get("Effects", "recharge_description")
            if charges[2] == True:
                chargestr += " %s" % cfg.get("Effects", "destroy_on_empty_description")
            desc.append(chargestr)
        if self.enhancement > 0:
            desc.append(cfg.get("Effects", "%s_enh_description" % self.category))
        desc.append(self.item_description)
        if self.material is not None:
            desc.append(self.material.getDescription(self.category))
        for affix in self.prefixes + self.suffixes:
            desc.append(affix.getDescription(self.category))
        desc = "\n".join(desc)
        desc = self.replaceVars(desc, lowercase=True)
        return desc
        
    
    def getName(self):
        # Gets the full name of the item. Includes quantity, prefixes, suffixes
        # enhancement, material, item... you get the picture.
        # Let's do this in order of appearance.
        # Quantity first.
        qtystr = ""
        if self.quantity is not None:
            qtystr = str(self.getQuantity())
        # Enhancement
        enhstr = ""
        if self.enhancement > 0:
            enhstr = "+%d" % self.enhancement
        # Prefixes.
        prelist = []
        for prefix in self.prefixes:
            prelist.append(prefix.prefix)
        prelist = " ".join(prelist)
        # Material and name.
        matname = ""
        if self.material is None:
            matname = self.item_name
        elif self.material.id is None:
            matname = self.item_name
        elif "@material" in self.item_name:
            matname = self.item_name.replace("@material", self.material.name)
        else:
            matname = " ".join([self.material.name, self.item_name])
        suflist = []
        for suffix in self.suffixes:
            suflist.append(suffix.suffix)
        suflist = " and ".join(suflist)
        name = " ".join([qtystr, enhstr, prelist, matname, suflist])
        # Clean up any weird double spaces
        while "  " in name:
            name = name.replace("  "," ")
        # Just in case there's any leading or trailing spaces.
        name = name.strip()
        # Replace any variables.
        name = self.replaceVars(name)
        return name
    
    def removeEffect(self, effect):
        # Removes the offending effect.
        if effect in self.prefixes:
            self.prefixes.remove(effect)
        elif effect in self.suffixes:
            self.suffixes.remove(effect)
        return
    
    def replaceItem(self):
        # Replaces the current item with another item of the same category.
        # Checks materials, effects, and curses to make sure none will beomce
        # invalid in the process.
        # Make sure we're not the only item on the list.
        group = []
        group_conflict = []
        subtype = []
        subtype_conflict = []
        damage_type = []
        damage_type_conflict = []
        properties = []
        property_conflict = []
        material_type = []
        for effect in self.prefixes + self.suffixes + [self.material]:
            if effect.id is not None:
                group += item_data.getList(effect.id, "group")
                group_conflict += item_data.getList(effect.id, "group_conflict")
                subtype += item_data.getList(effect.id, "subtype")
                subtype_conflict += item_data.getList(effect.id, "item_subtype_conflict")
                damage_type += item_data.getList(effect.id, "damage_type")
                damage_type_conflict += item_data.getList(effect.id, "damage_type_conflict")
                properties += item_data.getList(effect.id, "required_properties")
                property_conflict += item_data.getList(effect.id, "property_conflict")
                material_type += item_data.getList(effect.id, "material_type")
        if len(group) == 0:
            group = None
        if len(group_conflict) == 0:
            group_conflict = None
        if len(subtype) == 0:
            subtype = None
        if len(subtype_conflict) == 0:
            subtype_conflict = None
        if len(damage_type) == 0:
            damage_type = None
        if len(properties) == 0:
            properties = None
        else:
            # Make sure properties being met by our effects are not counted.
            properties = list(set(properties)) # Make sure we only have uniques.
            for effect in self.prefixes + self.suffixes + [self.material]:
                prop = item_data.getList(effect, "properties")
                for p in prop:
                    if p in properties:
                        properties.remove(p)
            if self.enhancement > 0:
                if "enhancement" in properties:
                    properties.remove("enhancement")
        if len(property_conflict) == 0:
            property_conflict = None
        if len(material_type) == 0:
            material_type = None
        new_id= self.getID(group=group, subtype=subtype, damage_type=damage_type,
            properties=properties, material_type=material_type,
            group_conflict=group_conflict, subtype_conflict=subtype_conflict,
            damage_type_conflict=damage_type_conflict, 
            property_conflict=property_conflict)
        tries = 10 # There might be only one item that fits.
        while new_id == self.id and tries > 0:
            new_id= self.getID(group=group, subtype=subtype, damage_type=damage_type,
                properties=properties, material_type=material_type,
                group_conflict=group_conflict, subtype_conflict=subtype_conflict,
                damage_type_conflict=damage_type_conflict, 
                property_conflict=property_conflict)
            tries -= 1
        self.id = new_id
        self.getValues()
        return new_id
        
    def getID(self, group=None, subtype=None, damage_type=None, max_bonus=None,
        properties=None, material_type=None, group_conflict=None,
        subtype_conflict=None, damage_type_conflict=None, property_conflict=None,
        material_type_conflict=None, rarity=None):
        # Grabs an ID fitting the type.
        # First, let's clean up our filters.
        # Group, subtype, damage_type, properties, and material_type need to end
        # up a sets, and can start as string, lists, or tuple.       
        if group is not None and type(group) not in [str, list, tuple]:
            logging.error("Invalid group filter %s. Ignoring." % str(group))
            group = None
        elif group is not None:
            if type(group) is str:
                group = [group]
            group = set(group)
        # Item subtype. Same as above.
        if subtype is not None and type(subtype) not in [str, list, tuple]:
            logging.error("Invalid subtype filter %s. Ignoring." % str(subtype))
            subtype = None
        elif subtype is not None:
            if type(subtype) is str:
                subtype = [subtype]
            subtype = set(subtype)
        # Damage Type.
        if damage_type is not None and type(damage_type) not in [str, list, tuple]:
            logging.error("Invalid damage_type filter %s. Ignoring." % str(damage_type))
            damage_type = None
        elif damage_type is not None:
            if self.category != "weapon":
                logging.error("Only weapons have damage types. Ignoring.")
                damage_type = None
            else:
                if type(damage_type) is str:
                    damage_type = [damage_type]
                damage_type = set(damage_type)
        if properties is not None and type(properties) not in [str, list, tuple]:
            logging.error("Invalid properties filter %s. Ignoring." % str(properties))
            properties = None
        elif properties is not None:
            if type(properties) is str:
                properties = [properties]
            properties = set(properties)
        if material_type is not None and type(material_type) not in [str, list, tuple]:
            logging.error("Invalid material_type filter %s. Ignoring." % str(material_type))
            material_type = None
        elif material_type is not None:
            if type(material_type) is str:
                material_type = [material_type]
            material_type = set(material_type)
        # Maximum bonus.
        if max_bonus is not None and type(max_bonus) is not int:
            logging.error("Invalid max_bonus filter: %s. Must be int. Ignoring." % max_bonus)
            max_bonus = None
        # Make sure we don't exceed our capacity.
        budget = cfg.getInt("General", "max_bonus_%s" % self.rarity)  - self.getBonus()
        # Add back in any existing item bonus
        budget += self.item_bonus
        if max_bonus is None:
            max_bonus = budget
        elif max_bonus > budget:
            max_bonus = budget
        # Conflicts. Each of these should only ever be provided by the replaceitem
        # function. So we can do less error checking.
        if group_conflict is not None:
            group_conflict = set(group_conflict)
        if subtype_conflict is not None:
            subtype_conflict = set(subtype_conflict)
        if damage_type_conflict is not None:
            damage_type_conflict = set(damage_type_conflict)
        if property_conflict is not None:
            property_conflict = set(property_conflict)
        # OK. So. Now we know our filters will work. Let's get down to filtering.
        item_list = item_data.getOptionList("category", self.category)
        filter_list = []
        weight_list = []
        for item in item_list:
            # Let's check our filters.
            if group is not None or group_conflict is not None:
                # Our group needs to be a subset of the item's group.
                # If we have a filter and the item has no group, we skip it.
                data = item_data.getList(item, "group")
                data = set(data)
                if group is not None:
                    if not group.issubset(data):
                        continue
                if group_conflict is not None:
                    # Conflict: None of these can be present in the item's group list.
                    if not group_conflict.isdisjoint(data):
                        continue
            if subtype is not None or subtype_conflict is not None:
                # Functions identical to the above, just for subset.
                data = item_data.getList(item, "item_subtype")
                data = set(data)
                if subtype is not None:
                    if not subtype.issubset(data):
                        continue
                if subtype_conflict is not None:
                    # Same as group conflict.
                    if not subtype_conflict.isdisjoint(data):
                        continue
            if damage_type is not None or damage_type_conflict is not None:
                # This is the reverse. The item's damage type has to fit one of ours.
                data = item_data.getList(item, "damage_type")
                data = set(data)
                if damage_type is not None:
                    if not data.issubset(damage_type):
                        continue
                if damage_type_conflict is not None:
                    # You know how this works. Just like the others.
                    if not damage_type_conflict.isdisjoint(data):
                        continue
            if properties is not None or property_conflict is not None:
                # Properties is back to the previous. Our item must match all.
                data = item_data.getList(item, "properties")
                data = set(data)
                if properties is not None:
                    if not properties.issubset(data):
                        continue
                if property_conflict is not None:
                    # Last one. Make sure there's no overlap.
                    if not property_conflict.isdisjoint(data):
                        continue
            if material_type is not None:
                # For material types, there simply needs to be an overlap.
                data = item_data.getList(item, "material_type")
                data = set(data)
                if material_type.isdisjoint(data):
                    continue
            if max_bonus is not None:
                # Our item's bonus mustn't exceed our budget.
                data = item_data.getInt(item, "bonus")
                if data is not None:
                    if data > budget:
                        continue
            if rarity is not None:
                data = item_data.getList(item, "req_rarity")
                if rarity not in data and len(data) > 0:
                    # Our rarity doesn't match.
                    continue
            # We've made it through our filters! Now, add our item.
            filter_list.append(item)
            chance = item_data.getInt(item, "chance")
            if chance is None:
                weight_list.append(1)
            else:
                weight_list.append(chance)
        # Now we have our list of valid items.
        if len(filter_list) < 1:
            logging.error("Filters eliminated all items.")
            return None
        else:
            return random.choices(filter_list, weight_list)[0]