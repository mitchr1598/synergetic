from sqlalchemy.ext.automap import automap_base
from synergetic_session import Synergetic
from Attendance.Attendance import create_attendance_master, AttendanceMaster
from sqlalchemy import create_engine, MetaData
import datetime
import pyodbc


engine_test = create_engine("mssql+pyodbc://@SynTest")

# Only deal with these tables
metadata = MetaData()
metadata.reflect(engine_test, only=['uCovidVaccine', 'uStaffContract'])

Base = automap_base(metadata=metadata)
Base.prepare()

uCovidVaccine = Base.classes.uCovidVaccine
uStaffContracts = Base.classes.uStaffContract


def main():
    atten_master = create_attendance_master()
    with Synergetic.test() as session:
        session.add(atten_master)
        session.rollback()
        #session.commit()


if __name__ == '__main__':
    main()


