import pygtk
pygtk.require('2.0')
import gtk, glib
import time
import sqlite3

from drinker import Drinker
from drink import Drink

class BabySitter:

    def __init__(self):
        con = sqlite3.connect('baby.db')
        # initialize window
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect('delete_event', self.delete_event)
        window.connect('destroy', self.destroy_event, con)
        window.set_title('The Babysitter')
        window.set_border_width(10)
        # intialize main box
        self.vbox = gtk.VBox()
        # create top box
        top_box = gtk.HBox()
        # create add drinker button
        button = gtk.Button('Add Drinker')
        button.connect('clicked', self.add_drinker_button, con)
        top_box.pack_start(button)
        button.show()
        # create add hour button
        button = gtk.Button('Add Hour')
        button.connect('clicked', self.add_hour)
        top_box.pack_start(button)
        button.show()
        self.vbox.pack_start(top_box, False, False)
        top_box.show()
        # create box for drinker control boxes
        self.drinker_table = gtk.Table()
        self.vbox.pack_start(self.drinker_table)
        # load drinkers and drink
        self.drinkers = []
        self.load_drinkers(con)
        self.load_drink(con)
        # show drinkers
        self.drinker_table.show()
        # add main table to window
        window.add(self.vbox)
        # show components
        self.vbox.show()
        window.show()
        glib.timeout_add_seconds(9, self.update_drinkers)

    def load_drinkers(self, con):
        cur = con.cursor()
        cur.execute('SELECT * FROM drinkers')
        for row in cur:
            drinker = Drinker(Drink(con, None, row[6]), self.remove_drinker, self.set_drink, con)
            drinker.name = row[0]
            drinker.weight = row[1]
            drinker.male = row[2]
            drinker.alcohol = row[3]
            drinker.started = row[4]
            drinker.tab = row[5]
            drinker.fill_fields()
            self.add_drinker(drinker)
        cur.close()

    def load_drink(self, con):
        cur = con.cursor()
        cur.execute('SELECT name FROM drink')
        self.drink = Drink(con, None, cur.fetchone()[0])
        cur.close()

    def save_drinkers(self, con):
        cur = con.cursor()
        cur.execute('DELETE FROM drinkers')
        for d in self.drinkers:
            if d.name:
                cur.execute('INSERT INTO drinkers VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (d.name, d.weight, d.male, d.alcohol, d.started, d.tab, d.drink.name))
        cur.close()

    def save_drink(self, con):
        cur = con.cursor()
        cur.execute('UPDATE drink SET name=?', (self.drink.name,))
        cur.close()

    def add_drinker_button(self, widget, con):
        drinker = Drinker(self.drink, self.remove_drinker, self.set_drink, con)
        self.add_drinker(drinker)

    def add_drinker(self, drinker):
        n = len(self.drinkers)
        self.drinker_table.attach(drinker.vbox, n % 6, n % 6 + 1,
            n / 6, n / 6 + 1)
        self.drinkers.append(drinker)

    def remove_drinker(self, widget, drinker):
        temp_drinkers = []
        for d in self.drinkers:
            self.drinker_table.remove(d.vbox)
            temp_drinkers.append(d)
        self.drinkers = []
        for d in temp_drinkers:
            if d != drinker:
                self.add_drinker(d)

    def set_drink(self, drink):
        self.drink = drink

    def add_hour(self, widget, data=None):
        for d in self.drinkers:
            d.started -= 3600
            d.update_label()

    def update_drinkers(self, data=None):
        for d in self.drinkers:
            d.update_label()
        return True

    def delete_event(self, widget, data=None):
        dialog = gtk.Dialog()
        label = gtk.Label('Really Quit?\n(Ask a sober person for help)')
        dialog.vbox.pack_start(label)
        label.show()
        dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        dialog.set_response_sensitive(gtk.RESPONSE_OK, True)
        dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        dialog.set_response_sensitive(gtk.RESPONSE_CANCEL, True)
        quit = dialog.run() == gtk.RESPONSE_OK
        dialog.destroy()
        return not quit

    def destroy_event(self, widget, con):
        self.save_drinkers(con)
        self.save_drink(con)
        con.commit()
        con.close()
        gtk.main_quit()

    def main(self):
        gtk.main()

babysitter = BabySitter()
babysitter.main()
