from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import select


engine_test = create_engine("mssql+pyodbc://@SynTest")

# Only deal with these tables
metadata = MetaData()
metadata.reflect(engine_test, only=['FileSemesters'])

Base = automap_base(metadata=metadata)
Base.prepare()

FileSemesters = Base.classes.FileSemesters

_res = [row for row in engine_test.execute(
    select(
        FileSemesters.FileYear,
        FileSemesters.FileSemester
    ).where(
        FileSemesters.SystemCurrentFlag == 1
    )
)]

CURRENT_YEAR, CURRENT_SEMESTER = _res[0]


