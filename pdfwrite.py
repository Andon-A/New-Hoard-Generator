# PDF 
# Takes information given and makes it a PDF.
# It's designed to put the hord title in the top center
# Followed by some generator info
# Followed by the seed.
# Below that we split into two columns, and add the contents. To keep things
# going where they should go, it gets a little... convoluted.
# FPDF is not exactly designed for this, but it works... although I'd use
# something else. Suggestions welcome.
#
# Since we know what font size and such we're using, we'll be able to configure
# how things work.

import configs

import configparser
from fpdf import FPDF, HTMLMixin
from math import ceil, floor

# Load our (updated and shiny and new) configs:
general = configs.CFG(configs.GENERAL)
# Set up our fonts.
FONT_FOLDER = general.get("Folders", "pdffonts")
FONT_NAME = general.get("PDF", "font_name")
reg_font = "./%s/%s" % (FONT_FOLDER, general.get("PDF", "font_regular"))
bold_font = "./%s/%s" % (FONT_FOLDER, general.get("PDF", "font_bold"))
italic_font = "./%s/%s" % (FONT_FOLDER, general.get("PDF", "font_italic"))
bolditalic_font = "./%s/%s" % (FONT_FOLDER, general.get("PDF", "font_bolditalic"))
# Minimum lines for an item. At least 3 (Name, info, description).
MIN_LINES = general.getInt("PDF", "min_lines")
if MIN_LINES is None:
    MIN_LINES = 3
elif MIN_LINES < 3:
    MIN_LINES = 3

class PDF(FPDF, HTMLMixin):
    # A class that does a few other things
    def __init__(self, title, seed="", cr=None):
        # We know what we want it to do.
        # So set it up to do it.
        # Portrait orientation, inch units, letter format.
        FPDF.__init__(self, orientation="P", unit="in", format="Letter")
        # And now some standard setup stuff.
        # First, set our margins. Left, Center, and Right.
        # Bottom margin is typically used by auto page break.
        # We don't want that, but the margin is used later.
        self.set_margins(0.75, 0.75, 0.75)
        self.set_auto_page_break(False, 0.75)
        # Now add our font(s)
        # I have Liberation Serif in the config but that can be changed
        # First, the regular. Then bold, italic, and bolditalic.
        self.add_font(family=FONT_NAME, style="", fname=reg_font, uni=True)
        self.add_font(family=FONT_NAME, style="B", fname=bold_font, uni=True)
        self.add_font(family=FONT_NAME, style="I", fname=italic_font, uni=True)
        self.add_font(family=FONT_NAME, style="BI", fname=bolditalic_font, uni=True)
        # Now some other housekeeping. The title of the work (As saved)
        # And the creator (This program)
        self.title = title
        self.set_title(self.title)
        self.set_creator("New Hoard Generator v%s" % configs.VERSION)
        if type(cr) is int or type(cr) is str:
            cr = str(cr)
            self.subtitle = "CR %s Hoard. Made with New Hoard Generator v%s" % (cr, configs.VERSION)
        else:
            self.subtitle = "Made with New Hoard Generator v%s" % configs.VERSION
        self.seed = seed
        self.get_title_sizes() # Adjusts title font size to fit.
        self.textsize = general.getFloat("PDF", "text_size")
        self.indent = general.getFloat("PDF", "indent")
        # Store our margins since we'll be.... abusing them later.
        self.l_margin_actual = self.l_margin
        self.r_margin_actual = self.r_margin
        # Horizontal centerpoint. Also for margin abuse later.
        # First, the divider. How far apart we want them to be.
        self.column_divider = 0.5
        # Now the column 1 right-hand margin
        self.col_r_margin = (self.w / 2) - (self.column_divider / 2)
        # And the column 2 left-hand margin
        self.col_l_margin = (self.w / 2) + (self.column_divider / 2)
        # And our column width. So we don't have to calculate it later.
        self.col_width = self.col_r_margin - self.l_margin
        # Now start the first page and column.
        # First, set our column variable. The first run needs this.
        self.column = None
        # Now. Add our first page.
        self.add_page()
        # And set up the column.
        self.next_column()
        # We SHOULD be good to go now.
        
    
    def get_line_height(self):
        # Returns the line height, rounded up to the next .05 inch, for the
        # current text size.
        # self.font_size gives the appropriate measurement in inches.
        lh = (5 * ceil((self.font_size * 100)/5)) / 100
        return lh
        
    def get_title_sizes(self):
        # Takes our title and subtitle sizes and reduces them to fit one line.
        t1size = general.getFloat("PDF", "title_size")
        t2size = general.getFloat("PDF", "subtitle_size")
        step = general.getFloat("PDF", "size_step")
        # First, the title.
        self.set_font(FONT_NAME, "B", t1size)
        xwidth = self.get_string_width(self.title)
        maxwidth = 8.5 - (self.l_margin + self.r_margin)
        while xwidth > maxwidth:
            t1size -= step
            self.set_font_size(t1size)
            xwidth = self.get_string_width(self.title)
        self.titlesize = t1size # Set to our adjusted size.
        # And now for the subtitle.
        self.set_font(FONT_NAME, "", t2size)
        xwidth = self.get_string_width(self.subtitle)
        while xwidth > maxwidth:
            t2size -= step
            self.set_font_size(t2size)
            xwidth = self.get_string_width(self.subtitle)
        self.subtitlesize = t2size
        return

    def header(self):
        # This writes the title onto each page.
        # If it's the first page, also writes the "made by" line and seed.
        self.set_font(FONT_NAME, "B", self.titlesize)
        self.lh = self.get_line_height()
        # Make a cell with the title.
        # Get our width, depending on the margins.
        cw = 8.5 - (self.l_margin + self.r_margin)
        self.cell(w=cw, h=self.lh, txt=self.title, align="C", ln=2)
        if self.page < 2:
            # Only put the subtitle and seed on the first page.
            # Subtitle
            self.set_font(FONT_NAME, "", self.subtitlesize)
            self.lh = self.get_line_height()
            self.cell(w=cw, h=self.lh, txt=self.subtitle, align="C", ln=2)
            # And seed.
            self.set_font(FONT_NAME, "", self.textsize)
            self.lh = self.get_line_height()
            if self.seed != "":
                self.cell(w=cw, h=self.lh, txt="Seed: %s" % self.seed, align="C", ln=2)
        # Set a marker for the top of this page.
        # And then set up our column.
        self.top_y = self.get_y() + 0.25
    
    def next_column(self):
        # Sets the page up for the current column.
        # This horridly abuses the margins. We've stored them elsewhere.
        # First, though, make it so we work right.
        # Calling next column should just increase the columns, right?
        # But maybe we need to add a page.
        if self.column == 0:
            self.column = 1
            # Go to the second column of the page.
            self.set_right_margin(self.r_margin_actual)
            self.set_left_margin(self.col_l_margin)
            # Move our cursor to the right point.
            self.set_x(self.l_margin)
            self.set_y(self.top_y)
        elif self.column == None:
            # First column of the first page.
            self.column = 0
            # Set up our column.
            self.set_right_margin(self.col_r_margin)
            self.set_x(self.l_margin)
            self.set_y(self.top_y)
        else:
            # Well, we've reached the end of the second margin.
            # Time to add a page. That has the "Take care of first column"
            # bits in it.)
            self.column = 0
            # First, re-set our margins.
            self.set_left_margin(self.l_margin_actual)
            self.set_right_margin(self.r_margin_actual)
            # Add our page.
            self.add_page()
            # And set up our column.
            self.set_right_margin(self.col_r_margin)
            self.set_x(self.l_margin)
            self.set_y(self.top_y)
    
    def getLines(self, text):
        # Gets the number of lines the string will take up.
        lines = ceil(self.get_string_width(text) / self.col_width)
        return lines
    
    def getLinesRemaining(self):
        # Gets the number of lines remaining at the current text size.
        # Always rounds down.
        ypos = self.get_y()
        bottom = self.h - self.b_margin
        dist = floor((bottom - ypos) / self.lh)
        return dist
        
    def addItem(self, iname=None, iinfo=None, idesc=None, indent=True):
        # First, set our font and  line height.
        self.set_font(FONT_NAME, "B", self.textsize)
        self.lh = self.get_line_height()
        # Clean up our description. If there's any new lines, separate them.
        if idesc is not None:
            if type(idesc) is str:
                idesc = [idesc]
            desc = []
            for d in idesc:
                desc += d.split("\n")
            # And remove any empty ones.
            idesc = []
            for d in desc:
                if d != "":
                    idesc.append(d)
        # Now get our total line count.
        LC = 1 # There's always some room, so add 1 for good measure.
        if iname is not None:
            LC += self.getLines(iname)
        if iinfo is not None:
            LC += self.getLines(iinfo)
        if idesc is not None:
            for de in idesc:
                LC += self.getLines(de)
        if iname is None and iinfo is None and idesc is None:
            # Well we have nothing to do here, so. Bye.
            return
        # Get the lines remaining. First get our height.
        # And then divide it by our line size.
        if self.getLinesRemaining() < MIN_LINES:
            # Not enough lines left.
            self.next_column()
            self.lh = self.get_line_height()
        # We at least have enough space to do our name and our info.
        if iname is not None:
            self.write(self.lh, iname)
            LC -= 1
            self.ln(self.lh) # And go to a new line.
        # Info is italic, so set the font. Leave the line height.
        if iinfo is not None:
            self.set_font(FONT_NAME, "I", self.textsize)
            self.write(self.lh, iinfo)
            self.ln(self.lh)
        # And back to our normal text. But here we use the writeLines function.
        if idesc is not None:
            for r in range(0, len(idesc)):
                line = idesc[r]
                if LC <= 5 and self.getLinesRemaining() <= 3:
                    # We'd put only two lines on the next column. Shorten this one
                    # to move more over there.
                    self.next_column()
                    self.lh = self.get_line_height()
                elif self.getLinesRemaining() <= 0:
                    # No more space!
                    self.next_column()
                    self.lh = self.get_line_height()
                # OK, so. Now we can write our lines.
                LC -= self.getLines(line)
                if r > 0 and indent:
                    # Second and further lines get the indent.
                    self.write_lines(line, self.indent)
                else:
                    self.write_lines(line)
                self.ln(self.lh)
        self.ln(0.25) # A bit of a gap between this and the next one.
        return
    
    def getItalics(self, word):
        # Returns if the word starts, finishes, both, or none.
        start = False
        end = False
        if len(word) == 1:
            # Nope, we ignore 1-letter words.
            return start, end, word
        else:
            # Word is 3 or more characters.
            if word[0] == "*":
                start = True
                word = word[1:]
            if word[-1] == "*":
                end = True
                word = word[:-1]
            return start, end, word
    
    def write_lines(self, text, indent=0):
        # Writes a string of text as lines.
        # First, splits the string into words.
        text = text.split(" ")
        # We presume the location is good. Except maybe indent.
        self.set_x(self.get_x() + indent)
        # Set our font and line height.
        self.set_font(FONT_NAME, "", self.textsize)
        self.lh = self.get_line_height()
        # We want to know if the text is *italic*
        italics = False
        startitalic = False
        enditalic = False
        for r in range(0, len(text)):
            word = text[r]
            #print(word)
            #print(italics)
            # Make sure we have a word.
            if len(word) == 0:
                continue
            elif len(word) == 1 and word == "*":
                # A single * inverts our italic-ness
                italics = not italics
                continue # No need to print this.
            elif len(word) >= 2:
                # Longer words. Check if we start or end italics.
                startitalic, enditalic, word = self.getItalics(word)
            # OK, so now we know our final word.
            # Check to see if it'll fit
            wlen = self.get_string_width(word)
            xpos = self.get_x()
            margin = self.l_margin + self.col_width
            if (xpos + wlen) > margin:
                # Hmm, we're too big.
                if self.getLinesRemaining() <= 1:
                    # And we're at the bottom of the column.
                    self.next_column()
                    # If we go to a new page, well. This helps keep things tidy
                    self.set_font(FONT_NAME, "", self.textsize)
                    self.lh = self.get_line_height()
                else:
                    # Still room. Another line!
                    self.ln(self.lh)
            # OK, so now we know our word, we have space, and we know our
            # italics. Let's go!
            if not italics and startitalic:
                italics = True
                startitalic = False # We've started our italics.
            elif italics and startitalic:
                startitalic = False # We're already italic.
            # Turn on our italics.
            if italics:
                self.set_font(FONT_NAME, "I", self.textsize)
            else:
                self.set_font(FONT_NAME, "", self.textsize)
            # Write our word
            if r == len(text)-1:
                # Last word, skip the trailing space.
                self.write(self.lh, word)
            else:
                self.write(self.lh, word + " ")
            # Check to see if we turn off italics.
            if enditalic:
                italics = False
                enditalic = False
        return
                
                    
        
        
        
        
        
        
        
        
        
        
        
        
        
        