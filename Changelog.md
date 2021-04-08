## 2021.3.11: Initial Release
* Initial release. Things exist now!
## 2021.3.21: Item Editing
Item Edit Update! Here's the general overview: The UI now supports editing items. This involved a complete re-write of the item generation code to allow for things to be swapped when and wherever, and a complete re-write of the UI to better support this. There's a few other ancillary things that have changed too.
### General Changes
* Configuration files have changed. Most options have been replaced with easier to read versions that also more closely identify what they do. IE itemtypes became item_types.
* There's a single configuration file loader now, shared across all modules. This means that if I want to, say, access the version number, I just have to call the config file.
* Oh yeah, version number is in the config file now, because of the above.
* Spellbooks have been moved to their own separate generator
* Spells have been moved to their own separate generator
### Item Generator Changes
* A complete re-write, so there's a lot of changes.
* Base items can grant spells, have modifiers, and require attunement in the same manner as effects. Please note that base items (ie, "weapons") will likely need to be added to the spell configurations to actually generate spells.
* Base items can have a bonus cost
* Base items and effects can require specific rarities.
* Staffs as a base item no longer require a base item to be set. They can have differing damage, properties, etc. They're basically just like any other weapon, except they can have staff effects applied to them.
* There's a configuration that lets staffs have a modified chance to generate a staff-only effect. This should give less "Magic Quarterstaff" and more "Staff" feel to staffs.
* Wondrous Items can now (optionally) ignore the prefix/suffix limits, which means there should be fewer items generating with the wrong rarities.
* Each effect can grant spells. It's a much better system now, which allows for swapping out effects easily.
* Base items and effects can all have chance weights.
* The methods used for selecting spells and random lists now means that they're technically unlimited.
* If the first item in a random list starts with @@, it sorts it into a group that can be selected separately. You can have multiple, different random choice lists on a single effect now!
* All effects and base items can have random lists.
* Materials are just a different category of effect, so they can do anything an effect can.
* Materials are no longer always selected first. Instead, it's a random order.
* Pre-programed effects (modifiers) are only parsed when they need to be parsed, and don't modify the base item directly. This means that effects can't add or remove the thrown, ammunition, or versatile properties.
* Dexterity Bonus for armors and ability to modify it have been removed. The game treats it as linked to the armor type in the rules (Such as the Medium Armor Master feat in the PHB), so it's better to do the same. Nothing stopping descriptions from stating things, though!
* The way properties are checked has been improved, so each effect can check the other effects for them as well.
* There's now an option for a maximum number of effects an item can have, if those effects are bonus 0 or less.
* There's now an option to set the minimum quantity of items that have quantities (Mostly ammunition)
* There's now an option for wondrous items to ignore the chance to generate without effects, as that chance was intended to boost things like a simple +3 weapon. Not a plain Silk Hat.
* Materials and Effects have separate configurable bonus requirement ranges. That is, if the item can generate up to 4 bonus worth of effects, it can be set to search for 3 or 4 bonus effects first. If none are found, it'll widen the search until something is found. 
* Scrolls have their own bonus requirement range that's set narrower, as we want scrolls to have a high spell level for their spells. It's not set to only look at the highest one, since self-casting is a modifier.
* If an armor requires strength, this is noted in the properties (Although not the requirement, that's elsewhere). This should make having effects that require this tag a little easier.
* If an armor applies stealth disadvantage, this is also marked in the properties instead of the previous method of having a separate attribute. As with strength, this should make effects simpler.
* Effects, items, materials, etc can have the is_magic tag set. For items and materials, it defaults to FALSE, and for effects it defaults to TRUE. This means you can have fancy non-magic items, too!
* Scrolls now always generate the suffix first, as that's where the spells are.
* Scrolls have had their weight increased. They have about a 12% chance of generating now, up from 7%
### Static Item Selector Changes
* "Force Random Scroll" has been put into the static_items.cfg file as gen_scroll_spells
* The static item selector not handles selecting spells for its spell scrolls.
### Hoard Generator Changes
* Saving is now handled by the UI.
* Names in the name generator can now have a maximum CR.
* Spellbooks have their own weight. They've been configured to occur about 0.5% of the time.
* CR 0-4 and 5-10 have had their chances for static items increased.
### UI Changes
* The UI now supports saving like a sane person - That is, using a dialog.
* The UI now supports editing of items! You can change, add, and remove prefixes and suffixes, edit the enhancement, re-roll the base item, and replace the random choices for all of the above. These edits are temporary and aren't saved to the Hoard until you hit that fancy save button. Once saved, you cannot revert the changes (Although you can still re-generate the hoard with the seed).
* There is currently no method to add or remove items from a hoard. This will be done in a future update.
* Font family and font sizes can now be edited via the config files, in the UI section.
* If the set font family isn't found (It's now Liberation Serif by default), it'll default to Arial.
* The Hoard Name, Seed, and CR are now "Read-Only" instead of "Disabled" so you can highlight and copy them even when you can't edit them.
## 2021.3.28: Curses!
This cursed update adds, well, curses. Curses are another type of effect and generate on an item in a similar manner to materials - Items can only have one, etc. See below for details!
* Curses added! Items can only have one curse, and it largely follows the conventions for other effects. They're now listed in the UI as well.
* Curses do not have names, prefixes, or suffixes. An item's name only adds "Cursed" to the beginning.
* Curses can be edited like other effects.
* Added the generate_curses option (True/False) to item_generator.cfg. This does what you might expect it to do - Enables or disables curses.
* Added the hidden_from_identify (True/False) option, only for curses. If this is TRUE (Default), it adds the hidden_from_identify_single_description or hidden_from_identify_plural_description to the curse's description.
* Added the destroy_on_removal (True/False) option. If this is TRUE (Default false), it adds the destroy_on_removal_single_description or destroy_on_removal_plural_description, depending on base item or quantity.
* Added (rarity)_curse_chance option to item_generator.cfg. This is the chance (0-100) that an item of the given rarity will generate with a curse.
* Updated effect description to allow single_item_description and plural_item_description. Updated most effects to use this. Ammunition effects have been moved to their own file to help with this.
* Scroll effects have been moved to their own file.
* The effect checks first to see if there's a set description (IE, armor_description). Otherwise, it uses single_description or plural_description as appropriate.
* The getDescription() for modifiers allows for forcing of a specific description, including ones not listed. This is used for ammunition and material descriptions.
* The single_description and plural_description entries do not support the @(other category)_description replacements.
* Added requires_attunement to effects. If the item does not already have an attunement requirement, these effects will not generate.
* Changed some more configurations to be more readable.
* Removed requireaffix option for items. It wasn't being used in code, and only one effect (On scrolls) was attempting to use it. With tweaks to scroll code, this shouldn't be needed, and can be accomplished in other ways if it is.
## 2021.X.X: System Folders
This update is a simple one, as far as the outside goes. It changes the folders from local folders to a system folder.
* If local_mode in general.cfg is set to TRUE, the program will attempt to run in local mode. Useful for, say, a thumb drive.
* Added an option in general.cfg to set the logging level, as per the python3 logging module
* local_mode and logging_level only work if they're in the local (./default_config) general.cfg file.
* Re-wrote configs.py to use system/local folders as needed. This also means that instead of each section making a CFG class of a given config, these classes are made in configs.py and are used from there.
* The program will now remember the last folder you saved in.
* static_items.cfg has been changed to static_item_cfg.cfg, to make more clear this isn't the file with the static items in it.