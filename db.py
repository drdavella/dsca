from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import logging, os

Base = declarative_base()
Session = sessionmaker()


class DataSet(Base):
    __tablename__ = 'dataset'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    date = Column(Date)

    datapoints = relationship("DataPoint", back_populates="dataset")

    def __init__(self,name,date=None):
        self.name = name
        self.date = date

    def add_datapoint(self,time,temperature,heat_flow):
        self.datapoints.append(DataPoint(time,temperature,heat_flow))


    def num_datapoints(self):
        '''
        Returns the number of data points in this data set.

        @return Number of data points in this data set.
        '''
        return len(dataset)


    def __repr__(self):
        s = "<DataSet(name={})>".format(self.name)
        return s


class DataPoint(Base):
    __tablename__ = 'datapoint'

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey('dataset.id'))
    # what is the precision of this?
    time = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    heat_flow = Column(Float, nullable=False)

    dataset = relationship("DataSet", back_populates="datapoints")

    def __init__(self,time,temperature,heat_flow):
        self.time = time
        self.temperature = temperature
        self.heat_flow = heat_flow


    def __repr__(self):
        s = "<DataPoint(time={},temperature={},heat_flow={})>" \
                .format(self.time,self.temperature,self.heat_flow)
        return s


class Database():

    @classmethod
    def create_database(cls,filename):
        '''
        Creates file and writes database schema at the specified path.

        @param filename Full path to database to be created
        '''
        if not os.path.exists(os.path.dirname(filename)):
            logging.error("database directory does not exist")
        engine = create_engine('sqlite:///'+filename)
        logging.debug("creating the database schema")
        Base.metadata.create_all(engine)


    def __init__(self,filename):
        '''
        Creates database object from file at given path.

        @param filename Full path representing the database file
        '''
        logging.info("opening database connection")
        self.engine = create_engine('sqlite:///'+filename)
        Session.configure(bind=self.engine)
        self.session = Session()
        self.datasets = list()


    def add_dataset(self,filename):
        '''
        Adds a data set to the database.

        @param filename Full path of CSV that contains data set
        '''
        if not os.path.exists(filename):
            logging.error("given CSV representing data set does not exist")
            return False
        ds_name, _ = os.path.splitext(os.path.basename(filename))
        ds = DataSet(ds_name)
        logging.debug("parsing CSV file")
        with open(filename,'r') as f:
            for line in f:
                if line == '\n': continue
                time, temp, heat = line.split(',')
                if time == "" or temp == "" or heat == "":
                    continue
                ds.add_datapoint(time,temp,heat)
        num_points = ds.num_datapoints()
        if num_points == 0:
            logging.error("empty dataset")
            return False
        self.datasets.append(ds)
        logging.debug("updating database with {} datapoints".format(num_points))
        self.session.add(ds)
        self.session.commit()
        return True
