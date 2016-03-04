import tkinter as tk
import logging


class Gui():
    def __init__(self):
        '''
        Initializes tk GUI to be used by the application.
        '''
        self.root = tk.Tk()
        logging.info("creating GUI")
        self.root.mainloop()
