import pygtk
pygtk.require('2.0')
import gtk
import sqlite3

class Drink:
    def __init__(self, con, old_drink=None, name=None):
        self.new_drink = False
        if old_drink:
            self.name = old_drink.name
            self.proof = old_drink.proof
            self.shot = old_drink.shot
            self.volume = old_drink.volume
            self.cost = old_drink.cost
        else:
            self.name = ''
            self.proof = 0
            self.shot = 0.0
            self.volume = 0.0
            self.cost = 0.0
        if name:
            self.name = name
            self.load_fields(con)
        else:
            dialog = gtk.Dialog('Drink Chooser')
            # Top label
            label = gtk.Label()
            label.set_text('What is Yo\' Drank of Choice?')
            dialog.vbox.pack_start(label, False, False, 10)
            label.show()
            # Entries Table
            table = gtk.Table(5, 2)
            # Drink name entry
            label = gtk.Label('Drink Name')
            table.attach(label, 0, 1, 0, 1)
            label.show()
            self.name_entry = gtk.Entry()
            completion = gtk.EntryCompletion()
            liststore = gtk.ListStore(str)
            cur = con.cursor()
            cur.execute('SELECT name FROM drinks')
            for row in cur:
                liststore.append(row)
            cur.close()
            completion.set_model(liststore)
            completion.set_text_column(0)
            self.name_entry.set_completion(completion)
            self.name_entry.connect('changed', self.set_name, con)
            table.attach(self.name_entry, 1, 2, 0, 1)
            self.name_entry.show()
            # Proof entry
            label = gtk.Label('Proof')
            table.attach(label, 0, 1, 1, 2)
            label.show()
            self.proof_entry = gtk.Entry()
            self.proof_entry.connect('changed', self.set_proof)
            table.attach(self.proof_entry, 1, 2, 1, 2)
            self.proof_entry.show()
            # Shot entry
            label = gtk.Label('Volume per Drink (oz)')
            table.attach(label, 0, 1, 2, 3)
            label.show()
            self.shot_entry = gtk.Entry()
            self.shot_entry.connect('changed', self.set_shot)
            table.attach(self.shot_entry, 1, 2, 2, 3)
            self.shot_entry.show()
            # Volume entry
            label = gtk.Label('Volume of Bottle (L)')
            table.attach(label, 0, 1, 3, 4)
            label.show()
            self.volume_entry = gtk.Entry()
            self.volume_entry.connect('changed', self.set_volume)
            table.attach(self.volume_entry, 1, 2, 3, 4)
            self.volume_entry.show()
            # Cost entry
            label = gtk.Label('Cost of Bottle')
            table.attach(label, 0, 1, 4, 5)
            label.show()
            self.cost_entry = gtk.Entry()
            self.cost_entry.connect('changed', self.set_cost)
            table.attach(self.cost_entry, 1, 2, 4, 5)
            self.cost_entry.show()
            dialog.vbox.pack_start(table, False, False)
            table.show()
            if old_drink:
                self.fill_fields()
            dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
            dialog.set_response_sensitive(gtk.RESPONSE_OK, True)
            dialog.set_default_response(gtk.RESPONSE_OK)
            dialog.run()
            dialog.destroy()
            self.save(con)

    def fill_fields(self):
        self.name_entry.set_text(self.name)
        self.proof_entry.set_text(str(self.proof))
        self.shot_entry.set_text(str(self.shot))
        self.volume_entry.set_text(str(self.volume))
        self.cost_entry.set_text(str(self.cost))
    
    def set_name(self, widget, con):
        self.new_drink = True
        self.name = widget.get_text()
        self.load_fields(con)
        self.fill_fields()

    def load_fields(self, con):
        cur = con.cursor()
        cur.execute('SELECT * FROM drinks WHERE name=?',
            (self.name,))
        values = cur.fetchall()
        if values:
            values = values[0]
            self.name = values[0]
            self.proof = values[1]
            self.shot = values[2]
            self.volume = values[3]
            self.cost = values[4]
            self.new_drink = False
        cur.close()

    def set_proof(self, widget, data=None):
        try:
            proof = float(widget.get_text())
        except ValueError:
            return None
        if proof < 0:
            return None
        self.proof = proof

    def set_shot(self, widget, data=None):
        try:
            shot = float(widget.get_text())
        except ValueError:
            return None
        if shot < 0:
            return None
        self.shot = shot

    def set_volume(self, widget, data=None):
        try:
            volume = float(widget.get_text())
        except ValueError:
            return None
        if volume < 0:
            return None
        self.volume = volume

    def set_cost(self, widget, data=None):
        try:
            cost = float(widget.get_text())
        except ValueError:
            return None
        if cost < 0:
            return None
        self.cost = cost

    def shot_cost(self):
        if not self.volume:
            return 0
        return self.shot * self.cost / (self.volume * 33.81)

    def shot_alcohol(self):
        return self.shot * self.proof / 200

    def save(self, con):
        if self.shot == 0.0:
            self.shot = self.volume * 33.81
        if self.volume == 0.0:
            self.volume = self.shot / 33.81
        cur = con.cursor()
        if self.new_drink:
            cur.execute('INSERT INTO drinks VALUES (?, ?, ?, ?, ?)',
                (self.name, self.proof, self.shot, self.volume, self.cost))
        else:
            cur.execute('UPDATE drinks SET proof=?, shot=?, volume=?, cost=? WHERE name=?',
                (self.proof, self.shot, self.volume, self.cost, self.name))
        cur.close()
            
