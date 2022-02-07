from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, MetaData

engine_prod = create_engine("mssql+pyodbc://@Synergetic")
engine_test = create_engine("mssql+pyodbc://@SynTest")


class Synergetic(Session):
    def __init__(self, engine):
        super().__init__(engine)

    @classmethod
    def production(cls):
        return Synergetic(engine_prod)

    @classmethod
    def test(cls):
        return Synergetic(engine_test)


# Global metadata object. Add tables to it by using the .reflect(only=[...]) method
metadata = MetaData()

engine = engine_test

