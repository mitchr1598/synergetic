from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import select
from synergetic.synergetic_session import Synergetic
from synergetic.School import CURRENT_YEAR, CURRENT_SEMESTER


engine_test = create_engine("mssql+pyodbc://@SynTest")

# Only deal with these tables
metadata = MetaData()
metadata.reflect(engine_test, only=['SubjectClasses'])

Base = automap_base(metadata=metadata)


class SubjectClasses(Base):
    __tablename__ = 'SubjectClasses'

    @classmethod
    def from_seq(cls, seq):
        query = select(SubjectClasses).filter_by(SubjectClassesSeq=seq)
        with Synergetic.test() as session:
            subject_class = session.execute(query).scalars().all()
        if len(subject_class) != 1:
            raise LookUpError(f"Database lookup return {len(subject_class)} results, when 1 was expected"
                              f"\n{seq=}")
        return subject_class[0]

    @classmethod
    def from_class_code(cls, classcode, filetype='A', fileyear=CURRENT_YEAR, filesemester=CURRENT_SEMESTER, classcampus='S'):
        query = select(SubjectClasses).filter_by(classcode=classcode,
                                                 filetype=filetype,
                                                 fileyear=fileyear,
                                                 filesemester=filesemester,
                                                 classcampus=classcampus)
        with Synergetic.test() as session:
            subject_class = session.execute(query).scalars().all()
        if len(subject_class) != 1:
            raise LookUpError(f"Database lookup return {len(subject_class)} results, when 1 was expected"
                              f"\n{locals()=}")
        return subject_class[0]


class LookUpError(Exception):  # Needs to go into a separate errors file
    pass


Base.prepare()
