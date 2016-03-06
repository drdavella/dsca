import tkinter as tk
import logging


class Gui():
    def __init__(self,database,title=""):
        '''
        Initializes tk GUI to be used by the application.

        @param database Database object to be used by the application
        @param title    Optional window title
        '''
        self.db = database
        logging.info("creating GUI")
        self.root = tk.Tk()
        if title: self.root.wm_title(title)
        self.root.mainloop()
