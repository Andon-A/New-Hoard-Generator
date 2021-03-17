# Spellbook.py
# Split from the item generator.

import logging
import configs
import random
import spells

RARITIES = ["common", "uncommon", "rare", "veryrare", "legendary"]

class Spellbook():
    # Spellbooks! A collection of spells! For wizards!
    def __init__(self, rarity=None, level=None):
        # Spellbooks! They're books, that are full of spells.
        # Really, they're not that complicated.
        if rarity is None or rarity not in RARITIES:
            self.rarity = random.choice(RARITIES)
        if level is not None:
            # Level overrides rarity.
            self.level = level
            self.rarity = self.setRarity()
        else:
            self.level = self.getLevel()
        self.getSpells(self.level)
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
        spell = spells.Spell(level=level, classlist="wizard")
        # Make sure we have no duplicates.
        overflow = 0 # Just to make sure we don't loop infinitely.
        while spell.id in self.spellids:
            spell = spells.Spell(level=level, classlist="wizard")
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
    
    def getInfo(self):
        infostr = "Spellbook, %s" % self.rarity
        return infostr
    
    def getName(self):
        # Spellbooks don't have prefixes or suffixes, so it doesn't follow
        # the normal methodology.
        lvlstr = "Level %d" % self.level
        qtystr = "(%d)" % sum(self.spellcount)
        name = " ".join([lvlstr, "Spellbook", qtystr])
        while "  " in name:
            name = name.replace("  "," ").strip()
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