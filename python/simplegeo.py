# simplegeo.py
# Part of the Ptolemy project. A simple GUI tool to help manually
# geocoding the locations in the format we need. It writes out a 
# JSON formatted file compatible with the Google Geocoding API format
# for our purposes. The filename is based on the Ptolemy ID we've
# adopted from Stuckelberg and Grasshoff. The coordinates are to be
# comma separated lat, lng that Google Maps displays when you right
# click on a map location and click "What's here?", enabling easy
# copy and paste.

import json

from Tkinter import *


class Application(Frame):

    def __init__(self):
        self.ptol_id_label = None
        self.ptol_id_entry = None
        self.coords_label = None
        self.coords_entry = None
        self.write_button = None

    def create_widgets(self):
        self.ptol_id_label = Label(self, text="Ptol ID")
        self.ptol_id_label.grid(row=0, column=0, sticky=W)
        self.ptol_id_entry = Entry(self, bd=1)
        self.ptol_id_entry.grid(row=0, column=1)

        self.coords_label = Label(self, text="Coords")
        self.coords_label.grid(row=1, column=0, sticky=W)
        self.coords_entry = Entry(self, bd=1)
        self.coords_entry.grid(row=1, column=1)

        self.write_button = Button(self)
        self.write_button["text"] = "Write"
        self.write_button["command"] =  self.write_file
        self.write_button.grid(row=2, column=1)

    @property
    def ptol_id(self):
        return self.ptol_id_entry.get().strip()
        
    @property
    def latitude(self):
        return float(self.coords_entry.get().split(',')[0])
        
    @property
    def longitude(self):
        return float(self.coords_entry.get().split(',')[1])
    
    @property
    def filename(self):
        return '../Data/geocode/%s.json' % self.ptol_id

    @property
    def results(self):
        return {
            "results" : [
                {
                    "geometry" : {
                        "location" : {
                            "lat" : self.latitude,
                            "lng" : self.longitude
                        }
                    }
                }
            ],
            "status" : "OK"
        }

    def write_file(self):
        with open(self.filename, 'wb') as outfile:
            json.dump(self.results, outfile, sort_keys=True,
                      indent=4, separators=(',', ': '))
            print 'wrote file: %s' % self.filename

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.create_widgets()
        self.pack()

root = Tk()
app = Application(master=root)
app.mainloop()
