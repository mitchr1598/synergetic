from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import select
import synergetic.synergetic_session as syn


# Only deal with these tables
syn.metadata.reflect(syn.engine, only=['FileSemesters'])

Base = automap_base(metadata=syn.metadata)
Base.prepare()

FileSemesters = Base.classes.FileSemesters

_res = [row for row in syn.engine.execute(
    select(
        FileSemesters.FileYear,
        FileSemesters.FileSemester
    ).where(
        FileSemesters.SystemCurrentFlag == 1
    )
)]

CURRENT_YEAR, CURRENT_SEMESTER = _res[0]


