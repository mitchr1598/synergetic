from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import select
from sqlalchemy.orm import relationship
from synergetic.synergetic_session import Synergetic
from synergetic.School import CURRENT_YEAR, CURRENT_SEMESTER
import synergetic.errors as errors
import synergetic.synergetic_session as syn


# Only deal with these tables
syn.metadata.reflect(syn.engine, only=['SubjectClasses'])

Base = automap_base(metadata=syn.metadata)


class SubjectClasses(Base):
    __tablename__ = 'SubjectClasses'

    @classmethod
    def from_seq(cls, seq):
        query = select(SubjectClasses).filter_by(SubjectClassesSeq=seq)
        with Synergetic.test() as session:
            subject_class = session.execute(query).scalars().all()
        if len(subject_class) != 1:
            raise errors.LookUpError(f"Database lookup return {len(subject_class)} results, when 1 was expected"
                                     f"\n{seq=}")
        return subject_class[0]

    @classmethod
    def from_class_code(cls, classcode, filetype='A', fileyear=CURRENT_YEAR, filesemester=CURRENT_SEMESTER, classcampus='S'):
        query = select(SubjectClasses).filter_by(ClassCode=classcode, FileType=filetype, FileYear=fileyear,
                                                 FileSemester=filesemester, ClassCampus=classcampus)
        with Synergetic.test() as session:
            subject_class = session.execute(query).scalars().all()
        if len(subject_class) != 1:
            raise errors.LookUpError(f"Database lookup return {len(subject_class)} results, when 1 was expected"
                                     f"\n{locals()=}")
        return subject_class[0]


Base.prepare()
