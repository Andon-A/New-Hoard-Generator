# configs.SPELL_DATA.py! A magical land, where the comments spell it all out for you.
# No I'm not sorry for that.
# In the current (2021.3.11) version of the NHG, static scrolls can be
# replaced by a forced scroll. Which is a weird, hacky implementation of
# a "random" item. With this, we can allow the itemgen and other things
# to access the list of configs.SPELL_DATA, so we can make a... better version.

import logging
import configs
import random

# Now, we want lists of spellcasting classes and spell schools.
CLASSES = []
SPELL_SCHOOLS = []
# Fill in those schools.

spell_data = configs.SPELL_DATA

# Update our class lists and spell schools.
for spell in spell_data.config:
    school = spell_data.get(spell, "school")
    if school not in SPELL_SCHOOLS and school is not None:
        SPELL_SCHOOLS.append(school)
    classes = spell_data.get(spell, "class")
    if classes is not None:
        classes = classes.split(";")
        for cl in classes:
            if cl not in CLASSES:
                CLASSES.append(cl)


# Now for our Spell class!
class Spell:
    def __init__(self,schools=None, level=None, classlist=None, itemtype=None):
            # Grabs a spell that fits the above filters.
            self.id = self.getSpell(schools, level, classlist, itemtype)
            if self.id is not None:
                self.name = spell_data.get(self.id, "name")
                self.level = spell_data.getInt(self.id, "level")
                self.school = spell_data.get(self.id, "school")
                self.classlist = spell_data.getList(self.id, "class")
                self.itemtypes = spell_data.getList(self.id, "itemtype")
            else:
                self.name = ""
                self.level = None
                self.school = None
                self.itemtypes = None
                self.classlist = []
    
    def getSpell(self, schools, level, classlist, item):
        # This is the actual filter. Easy enough.
        # Clean up our filters.
        if schools is not None and type(schools) not in [str, list, tuple]:
            # Invalid. Ignore it.
            logging.error("Ignoring invalid spell school filter: %s" % str(schools))
            schools = None
        if type(schools) is str:
            schools = [schools]
        # Our level filter.
        min_level = 0
        max_level = 9
        if type(level) is int:
            min_level = level
            max_level = level
        elif type(level) in [list, tuple]:
            min_level = max(min(level), 0) # No negative-level configs.SPELL_DATA.
            max_level = min(max(level), 9) # No 10+ level configs.SPELL_DATA.
        # Class List filter.
        if type(classlist) is str:
            classlist = classlist.split(";")
        if classlist is not None and type(classlist) not in [list, tuple]:
            logging.error("Ignoring invalid class list filter: %s" % str(classlist))
            classlist = None
        elif classlist is not None:
            classlist = set(classlist)
        # And item list filter.
        if item is not None and type(item) is not str:
            # I can't imagine a valid reason to use multiple item types as a filter.
            logging.error("Ignoring invalid item type filter: %s" % str(item))
            item = None
        # Make our list for configs.SPELL_DATA that fit the filter to go in.
        spell_list = []
        spell_weights = []
        # Now, cycle through our configs.SPELL_DATA.
        for spell in spell_data.config:
            # Check the scool
            if schools is not None:
                # Each spell belongs to precisely one school.
                # But we might have a few schools we can match.
                data = spell_data.get(spell, "school")
                if data not in schools:
                    # Our school isn't present. 
                    continue
            # Check the level.
            if level is not None:
                # Level must be at least the min level and at most the max level
                data = spell_data.getInt(spell, "level")
                if data is None:
                    # Spell has no level, so is invalid.
                    continue
                elif min_level > data or max_level < data:
                    # We're out of our level range.
                    continue
            # Check the class list.
            if classlist is not None:
                data = spell_data.getList(spell, "class")
                if data is None:
                    continue
                data = set(data)
                # We need an overlap, but any overlap will do.
                if data.isdisjoint(classlist):
                    # No overlap here though.
                    continue
            # And the item type. Ours only needs to be in the list.
            if item is not None:
                data = spell_data.getList(spell, "item_type")
                if data is None:
                    continue
                if item not in data:
                    # But it's not. :(
                    continue
            # If we've reached here, then, well. We have a valid spell!
            # Add the spell and its chance weight to the appropriate lists.
            spell_list.append(spell)
            chance = spell_data.getInt(spell, "chance")
            if chance is None:
                spell_weights.append(1)
            else:
                spell_weights.append(chance)
        # Now it's time to choose our spell.
        if len(spell_list) == 0:
            logging.debug("Filters returned no configs.SPELL_DATA.")
            return None
        spell = random.choices(spell_list, spell_weights)[0]
        return spell
            