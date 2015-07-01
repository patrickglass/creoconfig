#!/usr/bin/python3
# http://www.python-course.eu/tkinter_entry_widgets.php
# from Tkinter import (
#     Frame,
#     Label,
#     Entry,
#     Button
# )
import Tkinter


fields = 'Last Name', 'First Name', 'Job', 'Country'


def fetch(entries):
    for entry in entries:
        field = entry[0]
        text  = entry[1].get()
        print('%s: "%s"' % (field, text))


def makeform(root, fields):
    entries = []
    for field in fields:
        row = Tkinter.Frame(root)
        lab = Tkinter.Label(row, width=15, text=field, anchor='w')
        ent = Tkinter.Entry(row)
        row.pack(side=Tkinter.TOP, fill=Tkinter.X, padx=5, pady=5)
        lab.pack(side=Tkinter.LEFT)
        ent.pack(side=Tkinter.RIGHT, expand=Tkinter.YES, fill=Tkinter.X)
        entries.append((field, ent))
    return entries


if __name__ == '__main__':
    root = Tkinter.Tk()
    ents = makeform(root, fields)
    root.bind('<Return>', (lambda event, e=ents: fetch(e)))
    b1 = Tkinter.Button(
        root, text='Show',
        command=(lambda e=ents: fetch(e)))
    b1.pack(side=Tkinter.LEFT, padx=5, pady=5)
    b2 = Tkinter.Button(root, text='Quit', command=root.quit)
    b2.pack(side=Tkinter.LEFT, padx=5, pady=5)
    root.mainloop()
