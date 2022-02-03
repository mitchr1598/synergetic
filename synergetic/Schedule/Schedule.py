from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import select
from synergetic.School import CURRENT_YEAR, CURRENT_SEMESTER
from synergetic.School import SubjectClasses
from synergetic.synergetic_session import Synergetic
import datetime as dt
import synergetic.errors as errors

engine_test = create_engine("mssql+pyodbc://@SynTest")

# Only deal with these tables
metadata = MetaData()
metadata.reflect(engine_test, only=['StaffSchedule',
                                    'StaffScheduleStudentClasses'])

Base = automap_base(metadata=metadata)


class StaffSchedule(Base):
    __tablename__ = 'SubjectClasses'

    @classmethod
    def from_subject_class_seq_date_from(cls, subject_class_seq, date_time_from):
        query = select(SubjectClasses).filter_by(SubjectClassesSeq=subject_class_seq, DateFrom=date_time_from)
        with Synergetic.test() as session:
            subject_class = session.execute(query).scalars().all()
        if len(subject_class) != 1:
            raise errors.LookUpError(f"Database lookup return {len(subject_class)} results, when 1 was expected"
                                     f"\n{locals()=}")
        return subject_class[0]


Base.prepare()

StaffScheduleStudentClasses = Base.classes.StaffScheduleStudentClasses


def create_staff_schedule(StaffID=0,
                          ScheduleDateTimeFrom=None, ScheduleDateTimeTo=None, ScheduleDateFrom=None,
                          ScheduleTimeFrom=None, ScheduleDateTo=None, ScheduleTimeTo=None, Comment='', Room='',
                          TeamCode='', ParentStaffScheduleSeq=None, AttendanceCreatedByDate=None,
                          AttendanceCreatedByID=0, AttendanceModifiedByDate=None, AttendanceModifiedByID=0,
                          SubjectClassesSeq=None, TimesheetsSeq=None, ClassType='', ModifiedDatetime=None,
                          LocationCode='', StaffScheduleTypeCode='', Results='', SummaryNotes='',
                          Opposition='', ConfirmedDateTime=None, ConfirmedByUser='', SystemProcessNumber=None):
    """
    Creates a StaffSchedule instance. This is essentially an instance of a lesson attended by the staff.

    Example usage: create_staff_schedule(StaffID=51087,
                          ScheduleDateTimeFrom=dt.datetime(2042, 3, 14, 15, 30, 0),
                          ScheduleDateTimeTo=dt.datetime(2042, 3, 14, 16, 0, 0),
                          ParentStaffScheduleSeq=123456,
                          AttendanceCreatedByDate=None,
                          AttendanceCreatedByID=0,
                          AttendanceModifiedByDate=None,
                          AttendanceModifiedByID=0,
                          SubjectClassesSeq=None,
                          LocationCode='Gym',
                          StaffScheduleTypeCode='TRAIN')

    :param StaffID: *IMPORTANT* ID of the staff member creating the lesson for
    :param ScheduleDateTimeFrom: DateTime of the start of the lesson
    :param ScheduleDateTimeTo: DateTime of the end of the lesson
    :param ScheduleDateFrom: Date of the start of the lesson
    :param ScheduleTimeFrom: Time of the start of the lesson
    :param ScheduleDateTo: Date of the end of the lesson
    :param ScheduleTimeTo: Time of the end of the lesson
    :param Comment: A comment on the lesson
    :param Room: Room the lesson takes place
    :param TeamCode: Not sure, always blank for academic
    :param ParentStaffScheduleSeq: *IMPORTANT* When a class repeats there's multiple entries for the same class. This is
    the seq of the first lesson of that class. Observed in Instrumental lessons.
    :param AttendanceCreatedByDate: When the related AttendanceMaster was created (can be None)
    :param AttendanceCreatedByID: Who created the related AttendanceMaster (can be 0)
    :param AttendanceModifiedByDate: When the related AttendanceMaster was modified (can be None)
    :param AttendanceModifiedByID: Who modified the related AttendanceMaster (can be 0)
    :param SubjectClassesSeq: *IMPORTANT* Sequence of the SubjectClass
    :param TimesheetsSeq: Not sure
    :param ClassType: Not sure, always blank
    :param ModifiedDatetime: Time this row was modified
    :param LocationCode: Code of the location (from luLocation)
    :param StaffScheduleTypeCode: Code of the schedule type (training, rehersal etc.) (from luStaffScheduleType)
    :param Results: Results of the schedule (probably used for matches)
    :param SummaryNotes:
    :param Opposition:
    :param ConfirmedDateTime:  Always null
    :param ConfirmedByUser: Always blank
    :param SystemProcessNumber: Not sure, always null
    :return:
    """
    if SubjectClassesSeq is None:
        raise errors.MissingValueError("SubjectClassSeq is required to create a StaffSchedule but is missing.")
    if ScheduleDateTimeFrom is None:
        ScheduleDateTimeFrom = dt.datetime.now()
    if ScheduleDateTimeTo is None:
        ScheduleDateTimeTo = ScheduleDateTimeFrom + dt.timedelta(minutes=60)
    if ScheduleDateFrom is None:
        ScheduleDateFrom = ScheduleDateTimeFrom.date()
    if ScheduleTimeFrom is None:
        ScheduleTimeFrom = ScheduleDateTimeFrom.time()
    if ScheduleDateTo is None:
        ScheduleDateTo = ScheduleDateTimeTo.date()
    if ScheduleTimeTo is None:
        ScheduleTimeTo = ScheduleDateTimeTo.time()
    if ModifiedDatetime is None:
        ModifiedDatetime = dt.datetime.now()

    args = {key: value for key, value in locals().items() if value is not None}
    return StaffSchedule(**args)


def create_staff_schedule_student_classes(StaffScheduleSeq=None, FileType='A',
                                          FileYear=None, FileSemester=None, ClassCampus='S',
                                          ClassCode=None, ID=0,
                                          AttendedFlag=None, SubjectClassesSeq=None, ConfirmedDateTime=None,
                                          ConfirmedByUser='', PossibleAbsenceCode=None, PossibleReasonCode=None,
                                          PossibleDescription=None):
    """
    Creates a StaffSchedule instance. This is where rolls are marked when using the schedules section of a class.

    Example usage:
    create_staff_schedule_student_classes(StaffScheduleSeq=123456, FileType='SS',
                                          FileYear=2022, FileSemester=1, ClassCampus='S',
                                          ClassCode=13FUN01,
                                          ID=51047,
                                          AttendedFlag=0,
                                          SubjectClassesSeq=654321,
                                          PossibleAbsenceCode=EXCUR,
                                          PossibleReasonCode=SPO,
                                          PossibleDescription='Sport Excursion')

    :param StaffScheduleSeq:  The Staff Schedule this is linked to
    :param FileType: Of the class in question
    :param FileYear: Of the class in question
    :param FileSemester: Of the class in question
    :param ClassCampus: Of the class in question
    :param ClassCode: Of the class in question
    :param ID: Of the student in question
    :param AttendedFlag: Whether they attended
    :param SubjectClassesSeq: Of the class in question
    :param ConfirmedDateTime: Always null, must be some confirmation thing in Synergetic somewhere
    :param ConfirmedByUser: Always null, must be some confirmation thing in Synergetic somewhere
    :param PossibleAbsenceCode: From luAbsenceType
    :param PossibleReasonCode: From luAbsenceReason
    :param PossibleDescription: Custom description of the absence
    :return:
    """
    if StaffScheduleSeq is None:
        raise errors.MissingValueError("StaffScheduleSeq is required to create a StaffScheduleStudentClasses instance"
                                       "but is missing.")
    if ClassCode is None:
        raise errors.MissingValueError("ClassCode is required to create a StaffScheduleStudentClasses instance but is "
                                       "missing.")
    if SubjectClassesSeq is None:
        sc = SubjectClasses.from_class_code_query(ClassCode, filetype=FileType, fileyear=FileYear,
                                                  filesemester=FileSemester, classcampus=FileSemester)
        SubjectClassesSeq = sc.SubjectClassesSeq
    if AttendedFlag is None:
        AttendedFlag = 1

    args = {key: value for key, value in locals().items() if value is not None}
    return StaffScheduleStudentClasses(**args)

