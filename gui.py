import tkinter as tk
import logging


class Gui():
    def __init__(self,title=""):
        '''
        Initializes tk GUI to be used by the application.

        @param title Optional window title
        '''
        logging.info("creating GUI")
        self.root = tk.Tk()
        if title: self.root.wm_title(title)
        self.root.mainloop()
