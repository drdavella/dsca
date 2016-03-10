from tkinter import *
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
        self.root = Tk()
        if title: self.root.wm_title(title)

        self.pw = PanedWindow()
        self.pw.pack(fill=BOTH,expand=1)
        self.pw.add(self.__make_list_frame())
        self.pw.add(self.__make_graph_frame())

        height = self.root.winfo_screenheight()
        width = self.root.winfo_screenwidth()
        self.root.geometry("{}x{}".format(width,height))
        self.root.mainloop()


    def __make_list_frame(self):
        '''
        '''
        frame = Frame(self.root)
        frame.pack()
        label = Label(frame,text="List Frame")
        label.pack(anchor=CENTER)
        button = Button(frame,text="Exit",command=frame.quit)
        button.pack(side=LEFT)
        return frame


    def __make_graph_frame(self):
        frame = Frame(self.root)
        frame.pack()
        label = Label(frame,text="Graph Frame")
        label.pack(anchor=CENTER)
        button = Button(frame,text="WHATEVER")
        button.pack(side=RIGHT)
        return frame

