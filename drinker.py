import pygtk
pygtk.require('2.0')
import gtk
import time

from math import ceil

from drink import Drink

class Drinker:
    def __init__(self, drink, delete_method, set_drink_method, con):
        self.name = ''
        self.alcohol = 0.0
        self.tab = 0.0
        self.drink = drink
        self.weight = 1.0
        self.male = False
        self.started = 0.0
        # create box for drinker components
        self.vbox = gtk.VBox()
        # create table for entries
        table = gtk.Table(2, 2)
        # create name field
        label = gtk.Label('Name')
        table.attach(label, 0, 1, 0, 1, 0, 0, 10)
        label.show()
        self.name_entry = gtk.Entry()
        self.name_entry.connect('changed', self.set_name)
        table.attach(self.name_entry, 1, 2, 0, 1)
        self.name_entry.show()
        # create weight field
        label = gtk.Label('Weight')
        table.attach(label, 0, 1, 1, 2, 0, 0, 10)
        label.show()
        self.weight_entry = gtk.Entry()
        self.weight_entry.set_visibility(False)
        self.weight_entry.connect('changed', self.set_weight)
        table.attach(self.weight_entry, 1, 2, 1, 2)
        self.weight_entry.show()
        # add table
        self.vbox.pack_start(table, False, False)
        table.show()
        # create gender selector
        hbox = gtk.HBox()
        self.female_button = gtk.RadioButton(None, 'Female')
        hbox.pack_start(self.female_button, False, False)
        self.female_button.show()
        self.male_button = gtk.RadioButton(self.female_button, 'Male')
        self.male_button.connect('toggled', self.set_gender, self.weight_entry)
        hbox.pack_start(self.male_button, False, False, 20)
        self.male_button.show()
        self.vbox.pack_start(hbox, False, False)
        hbox.show()
        # create drink button
        button = gtk.Button('Get Yo\' Drank On')
        button.connect('clicked', self.take_shot)
        self.vbox.pack_start(button)
        button.show()
        # create change drink button
        button = gtk.Button('Change Yo\' Drank')
        button.connect('clicked', self.change_drink, set_drink_method, con)
        self.vbox.pack_start(button, False, False)
        button.show()
        # create info label
        self.label = gtk.Label()
        self.label.set_justify(gtk.JUSTIFY_CENTER)
        self.vbox.pack_start(self.label)
        self.label.show()
        # create vomit button
        button = gtk.Button('I Was Just Bullshittin\'')
        button.connect('clicked', self.undo_shot)
        self.vbox.pack_start(button, False, False)
        button.show()
        # create remove button
        button = gtk.Button('Knocked Out')
        button.connect('clicked', delete_method, self)
        self.vbox.pack_start(button, False, False)
        button.show()
        self.vbox.show()
        self.update_label()

    def fill_fields(self):
        self.name_entry.set_text(self.name)
        self.weight_entry.set_text(str(self.weight))
        self.male_button.set_active(self.male)

    def set_name(self, widget, data=None):
        self.name = widget.get_text()
        self.update_label()

    def set_weight(self, widget, data=None):
        try:
            weight = int(widget.get_text())
        except ValueError:
            return None
        if weight <= 0:
            return None
        self.weight = weight
        self.update_label()

    def set_gender(self, widget, data=None):
        self.male = widget.get_active()
        if data:
            data.set_visibility(self.male)
        self.update_label()

    def change_drink(self, widget, set_drink, con):
        self.drink = Drink(con, self.drink)
        set_drink(self.drink)
        self.update_label()

    def take_shot(self, widget, data=None):
        if self.bac() == 0.0:
            self.started = time.time()
            self.alcohol = 0
        self.alcohol += self.drink.shot_alcohol()
        self.tab += self.drink.shot_cost()
        self.update_label()

    def undo_shot(self, widget, data=None):
        self.alcohol -= self.drink.shot_alcohol()
        self.tab -= self.drink.shot_cost()
        if self.alcohol < 0:
            self.alcohol = 0
        if self.tab < 0:
            self.tab = 0
        if self.bac() == 0.0:
            self.started = time.time()
            self.alcohol = 0
        self.update_label()

    def bac(self):
        bac = (self.alcohol * (7.52 if self.male else 9.92) / self.weight -
            0.016 * (time.time() - self.started) / 3600)
        if bac < 0.0:
            return 0.0
        return bac

    def update_label(self):
        self.label.set_text('%s\nStandard Drinks: %d\nBAC: %.4f' %
            (self.drink.name, ceil(self.alcohol * 2), self.bac()))

