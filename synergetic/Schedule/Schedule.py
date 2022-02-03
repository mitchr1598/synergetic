from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, MetaData
from synergetic.School import CURRENT_YEAR, CURRENT_SEMESTER
from synergetic.School import SubjectClasses
import datetime as dt

engine_test = create_engine("mssql+pyodbc://@SynTest")

# Only deal with these tables
metadata = MetaData()
metadata.reflect(engine_test, only=['StaffSchedule',
                                    'StaffScheduleStudentClasses'])

Base = automap_base(metadata=metadata)
Base.prepare()

StaffSchedule = Base.classes.StaffSchedule
StaffScheduleStudentClasses = Base.classes.StaffScheduleStudentClasses

# Used to stop output command as SQL alchemy doesn't seem to allow "OUTPUT INTO"
# https://techcommunity.microsoft.com/t5/sql-server-blog/update-with-output-clause-8211-triggers-8211-and-sqlmoreresults/ba-p/383457
# https://stackoverflow.com/questions/47513622/dealing-with-triggers-in-sqlalchemy-when-inserting-into-table
for class_ in [StaffSchedule, StaffScheduleStudentClasses]:
    class_.__table__.implicit_returning = False


class MissingValueError(Exception):
    pass


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
        raise MissingValueError("SubjectClassSeq is required to create a StaffSchedule but is missing.")
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
        raise MissingValueError("StaffScheduleSeq is required to create a StaffScheduleStudentClasses instance but is "
                                "missing.")
    if ClassCode is None:
        raise MissingValueError("ClassCode is required to create a StaffScheduleStudentClasses instance but is "
                                "missing.")
    if SubjectClassesSeq is None:
        sc = SubjectClasses.from_class_code_query(ClassCode, filetype=FileType, fileyear=FileYear,
                                                  filesemester=FileSemester, classcampus=FileSemester)
        raise MissingValueError("SubjectClassesSeq is required to create a StaffScheduleStudentClasses instance but is "
                                "missing.")
    if AttendedFlag is None:
        AttendedFlag = 1

    args = {key: value for key, value in locals().items() if value is not None}
    return StaffScheduleStudentClasses(**args)

