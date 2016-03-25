from tkinter import *
from tkinter.ttk import *
import logging

label_font = ('Times',20,'bold')


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

        self.height = int(self.root.winfo_screenheight() / 1.5)
        self.width = int(self.root.winfo_screenwidth() / 1.5)
        self.datasets = list()
        self.plots = list()
        self.__make_list_frame()
        self.__make_graph_frame()
        self.__make_command_frame()

        self.root.geometry("{}x{}".format(self.width,self.height))
        self.root.mainloop()



    def __make_list_frame(self):
        '''
        '''
        h = self.height - 50
        w = self.width // 2
        # initialize the frame
        frame = Frame(self.root,border=5,relief='sunken',height=h,width=w)
        frame.grid_propagate(False)
        frame.grid(row=0, column=0,sticky=(N,E))
        # list of all data sets
        label = Label(frame,text="All Data Sets",font=label_font)
        label.grid(row=0,column=0,columnspan=2)

        self.datasets = StringVar(value=[str(x) for x in range(50)])
        data = Listbox(frame,listvariable=self.datasets)
        data.selection_set(0)
        data.grid(row=1,column=0,columnspan=2)
        sb_data = Scrollbar(frame,orient=VERTICAL,command=data.yview)
        data.configure(yscrollcommand=sb_data.set)
        # list of sets to be plotted
        label = Label(frame,text="Plotted Data Sets",font=label_font)
        label.grid(row=0,column=2,columnspan=2)
        plot = Listbox(frame,listvariable=StringVar(value=self.plots))
        plot.grid(row=1,column=2,columnspan=2)
        sb_plot = Scrollbar(frame,orient=VERTICAL,command=plot.yview)
        plot.configure(yscrollcommand=sb_data.set)
        # buttons
        add_dataset = Button(frame,text="New Dataset",command=self.__add_dataset)
        add_dataset.grid(row=2,column=0)
        plot = Button(frame,text="Plot",command=self.__add_plot)
        plot.grid(row=2,column=1)
        return frame


    def __make_graph_frame(self):
        ''''''
        h = self.height - 50
        w = self.width // 2
        frame = Frame(self.root,border=5,relief='sunken',height=h,width=w)
        frame.grid_propagate(False)
        frame.grid(row=0,column=1)
        #label = Label(frame,text="Graph Frame",font=label_font)
        #label.pack(anchor=CENTER)
        #button = Button(frame,text="WHATEVER")
        #button.pack(side=RIGHT)
        #return frame


    def __make_command_frame(self):
        ''''''
        frame = Frame(self.root)
        frame.grid(row=1,column=0,columnspan=2)
        button = Button(frame,text="Exit",command=self.root.quit)
        button.pack(anchor=CENTER)


    def __add_dataset(self):
        ''''''
        self.datasets.set([str(x) for x in range(50,100)])
        print("woot!")

    def __add_plot(self):
        self.plots.append(str(105))
