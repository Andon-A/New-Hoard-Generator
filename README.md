# New-Hoard-Generator
 A treasure hoard generator for D&D 5e
### What does it do?
It generates hoards! But you knew that. It functions in a similar vein to the DMG Hoard generator, with generators tailored for the CR levels, but it makes some tweaks. Largely, these are due to it being a program and not dice, which grants some additional variability:
* Money: It dispenses with coinage other than GP. It's the currency players turn things into anyway, so it simplifies things there a bit.
* Treasure: The DMG's treasure is all unified. X gems of Y value. This many art pieces, etc. Instead of this, it generates a total value of treasure and then picks from its list of treasure until the value is filled. The treasure list, like most things, is configurable (More on that later), and it also gives you the total value of the coinage and treasure if you'd rather just ignore it all.
* Item Selection: As with the treasure, the DMG's item selection is fairly unified. Regardless of what table you roll on, and no matter how many items you get, they'll all be roughly the same rarity. The item selector works similar to the treasure selector above - It generates a "value" and then picks items based on weights set in a configuration file for that specific generator - By default, a CR 0-4 hoard isn't going to get any legendary items regardless of how much "value" it may have, while a CR 17-20 hoard won't generate uncommon or common items unless those are the only ones that fit. Value for these items is largely arbitrary - A common item is "worth" 1, uncommon 2, etc. A small hoard with a value of 6 could generate 2 rare items, 6 common items, and so on.
* Item Selection: The hoard generator can pick from both static, or pre-made, items - or it can generate things from an item generator inspired by the way 3rd edition D&D magic items worked. The math is highly complex with multiple filters and other factors, so I haven't bothered to do it, but it can probably do a few hundred thousand unique items, from weapons to cloaks to trinkets and rings and, well. You get the picture. It can be configured to be biased towards one source or the other, too!
* Saving to PDF: The hoard generator can export to a pdf, because what's a hoard worth when it's gone after you close the program?
### What's this about configuration?
The generator is fairly configurable! Many portions of it can be changed via the .cfg files:
* The hoard generator can be configured for more generators at whatever CRs you want, including raising the maximum CR. Each generator can have the amount of gold, treasures, and items it generates modified, along with the rarities of the items they produce.
* The static item selector can have additional items added. Currently, it has all of the SRD magic items (Except the Deck of Many Things because formatting that with the way this works would have been... a nightmare.), but items from other sources, such as homebrew, can be added easily.
* The item generator can have materials, effects, base items, and the like added as well. Homebrew weapons? Yep, it'll deal with them just fine. Fancy armor effects? Those too!
### But what about the future?
There's several things I'm planning on adding as time goes on. I'll give a rough rundown of them here. This is a non-inclusive list, of course!
* Potion generator. While potions are less flashy than equipment, there's still room for some fun things with them.
* Curses for items.
* Better documentation. I've put some general overviews of how some things work in text files in the docs folder but, well. It really could use some better-looking and better-explained, uh. Explanations.
* Hoard editing in the UI. Things like removing items, fiddling with gold amounts, adding items, and the like.
* Item editing in the UI. Remove particular effects, add other effects, etc.
* Configuration editing in the UI
* A better method for saving other than "It kinda works"
* Art! But I'm very picky about what art I use, mostly because there's a lot of stolen art out there. Picking through that will take time.
### How can I contribute?
Well, for one, this is the first python code I've written in *some time* so there's definitely some improvements to make to the code. And if you have a feature in mind, feel free to fork this thing, add your feature, and put it on a pull request. I do want to keep it functional across all OS-es, so I've specifically avoided windows-specific things. Ideally it remains fairly lightweight, but ease of use and ease of maintenance is a higher priority.
