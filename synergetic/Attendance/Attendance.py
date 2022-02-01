from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import select
import datetime as dt
from synergetic.School import CURRENT_YEAR, CURRENT_SEMESTER

engine_test = create_engine("mssql+pyodbc://@SynTest")

# Only deal with these tables
metadata = MetaData()
metadata.reflect(engine_test, only=['AttendanceMaster',
                                    'tAttendances',
                                    'AbsenceEvents',
                                    'luAbsenceType',
                                    'luAbsenceReason',
                                    'luAbsenceEventType'])

Base = automap_base(metadata=metadata)
Base.prepare()

AttendanceMaster = Base.classes.AttendanceMaster
tAttendances = Base.classes.tAttendances
AbsenceEvents = Base.classes.AbsenceEvents
luAbsenceType = Base.classes.luAbsenceType
luAbsenceReason = Base.classes.luAbsenceReason
luAbsenceEventType = Base.classes.luAbsenceEventType

# Used to stop output command as SQL alchemy doesn't seem to allow "OUTPUT INTO"
# https://techcommunity.microsoft.com/t5/sql-server-blog/update-with-output-clause-8211-triggers-8211-and-sqlmoreresults/ba-p/383457
# https://stackoverflow.com/questions/47513622/dealing-with-triggers-in-sqlalchemy-when-inserting-into-table
AttendanceMaster.__table__.implicit_returning = False
tAttendances.__table__.implicit_returning = False

# AbsenceEvents.__table__.implicit_returning = False


# noinspection PyPep8Naming
def create_attendance_master(CreatedDate=dt.datetime.now(), CreatedByID=None, ModifiedDate=None, ModifiedByID=None,
                             FileType='A', FileYear=None, FileSemester=None, ClassCampus='S', ClassCode='Test',
                             StaffID=99999, AttendanceDate=dt.datetime.combine(dt.date.today(), dt.time(0, 0, 0)),
                             AttendancePeriod=10, AttendanceDateTimeFrom=dt.datetime.now(), AttendanceDateTimeTo=None,
                             AttendanceDayNumber=None, TimetableGroup=None, ClassCancelledFlag=0,
                             AttendanceOfficerModeFlag=0, SystemProcessNumber=0, SeqLinkedTo=None,
                             MarkRollAsMultiPeriodFlag=None):
    """
    /Essentially the class the roll is being taken for. Can sometimes get multiple entries per class, perhaps when the
    roll has been exited and gone back into/

    Create an AttendanceMaster object with default values. Passing no parameters will create a 'test' record.
    The value of StaffID will populate CreatedByID and ModifiedByID if you don't pass those

    //AttendanceMasterSeq: Primary Key. No need to specify
    :param CreatedDate: Time the roll was taken
    :param CreatedByID: ID of the staff member taking the roll  (different to StaffID when a relief is taken)
    :param ModifiedDate: Appears to be the same as CreatedDate for most cases
    :param ModifiedByID: Appears to be the same as CreatedByID for most cases
    :param FileType: FileType for the class
    :param FileYear: FileYear for the class
    :param FileSemester: FileSemester for the class
    :param ClassCampus: ClassCampus for the class
    :param ClassCode: ClassCode for the class
    :param StaffID: Staff Member of the class  (different to StaffID when a CreatedByID is taken)
    :param AttendanceDate: Date of class
    :param AttendancePeriod: Period of class
    :param AttendanceDateTimeFrom: Start datetime of class
    :param AttendanceDateTimeTo: End datetime of class
    :param AttendanceDayNumber: Day in timetable cycle
    :param TimetableGroup: Always 'T' for academic classes
    :param ClassCancelledFlag: Whether the class is cancelled, never happened for academic classes
    :param AttendanceOfficerModeFlag: Unknown, always 0
    :param SystemProcessNumber: Unknown, always 0
    :param SeqLinkedTo: Other record that related to. Maybe used when multiperiod?? but not always
    :param MarkRollAsMultiPeriodFlag: Roll as multi-period
    :return:
    """


    if CreatedByID is None:
        CreatedByID = StaffID
    if ModifiedDate is None:
        ModifiedDate = CreatedDate
    if ModifiedByID is None:
        ModifiedByID = CreatedByID
    if FileYear is None:
        FileYear = CURRENT_YEAR
    if FileSemester is None:
        FileSemester = CURRENT_SEMESTER
    if AttendanceDateTimeTo is None:
        AttendanceDateTimeTo = AttendanceDateTimeFrom + dt.timedelta(minutes=50)
    if TimetableGroup is None:
        TimetableGroup = 'T' if FileType == 'A' else FileType
    if MarkRollAsMultiPeriodFlag is None:
        MarkRollAsMultiPeriodFlag = 1 if SeqLinkedTo is not None else 0
    args = {key: value for key, value in locals().items() if value is not None}
    return AttendanceMaster(**args)


def create_t_attendances(AttendanceMasterSeq=None, ID=88888, PossibleAbsenceCode='', PossibleDescription='', AttendedFlag=0,
                         ModifiedDate=None, ModifiedByID=99999,
                         PossibleReasonCode='', UserFlag1=0, UserFlag2=0, UserFlag3=0, UserFlag4=0, UserFlag5=0,
                         LateArrivalFlag=0, LatearrivalTime=None, EarlyDepartureFlag=0, EarlyDepartureTime=None,
                         AbsenceEventsSeq=0, NonAttendCreatedAbsenceEventsFlag=None):
    """
    /Each Student attendance/

    Creates a tAttendances instance with default arguments.
    Important args: ID, AttendedFlag, ModifiedByID, ModifiedDate

    //AttendanceSeq: Primary Key. No need to specify
    :param AttendanceMasterSeq: Foreign key, the roll record it's being entered for
    :param ID: Student ID
    :param PossibleAbsenceCode: From luAbsenceType
    :param PossibleDescription: Custom absence comment
    :param AttendedFlag: Attended? 1 or 0
    :param ModifiedDate: datetime record was modified
    :param ModifiedByID: Who modified
    :param PossibleReasonCode: Not used, probably links to luAbsenceReason
    :param UserFlag1: Can't determine the use
    :param UserFlag2
    :param UserFlag3
    :param UserFlag4
    :param UserFlag5
    :param LateArrivalFlag: Whether the student arrived late
    :param LatearrivalTime: Time (sometimes datetime) of Late arrival, NULL when not a late arrival
    :param EarlyDepartureFlag: Whether the student left early
    :param EarlyDepartureTime: Time (sometimes datetime) of early departure, NULL when not a early departure
    :param AbsenceEventsSeq: Link to the absence events table
    :param NonAttendCreatedAbsenceEventsFlag: Absence event created by not marked as absent

    :return:
    """
    if PossibleAbsenceCode == '' and AttendedFlag == 0:
        PossibleAbsenceCode = 'ABS'
    if LateArrivalFlag == 1 and LatearrivalTime is None:
        LatearrivalTime = dt.datetime.now()
    if EarlyDepartureFlag == 1 and EarlyDepartureTime is None:
        EarlyDepartureTime = dt.datetime.now()
    if NonAttendCreatedAbsenceEventsFlag is None:
        NonAttendCreatedAbsenceEventsFlag = 1 if AbsenceEventsSeq > 0 and AttendedFlag == 1 else 0
    # Get all the local arguments, but filtered out the ones that haven't been set
    args = {key: value for key, value in locals().items() if value is not None}
    return tAttendances(**args)


def create_absence_events(SupersededByAbsenceEventsSeq=None, AbsenceEventTypeCode=None, ID=77777,
                          EventDateTime=dt.datetime.combine(dt.date.today(), dt.time(0, 0, 0)),
                          EventDate=None, EventTime=None, CreatedByID=-99999,
                          CreatedDate=None, ModifiedByID=None, ModifiedDate=None,
                          AbsenceTypeCode='', AbsenceReasonCode='', SchoolInOutStatus='', EnteredInAdvanceFlag=0,
                          SystemGeneratedFlag=0, SystemProcessNumber=0, NoteReceivedFlag=0, ContactMadeFlag=0,
                          ApprovedFlag=0, ReportedByID=None, ReportedByName='', EventComment='',
                          LeavingWithID=None, AbsencePeriodCode=None, ContactReceivedFlag=0, NoteMadeFlag=0,
                          TerminalCode='', LinkedID=None):
    """
    /Each Absence event/

    Creates an absence events instance with default arguments.
    Important args: ID, CreatedByID, AbsencePeriodCode
    //AbsenceEventsSeq: Primary Key. No need to specify
    //MasterAbsenceEventsSeq: Mostly the same as AbsenceEventsSeq, but is different when both 'in' and 'out' is entered
    :param SupersededByAbsenceEventsSeq: Superseded by another AbsenceEvent?
    :param AbsenceEventTypeCode: Type, linked to luAbsenceEventType
    :param ID: Student ID
    :param EventDateTime: datetime
    :param EventDate: date
    :param EventTime: time
    :param CreatedByID: ID of person marking event
    :param CreatedDate: date
    :param ModifiedByID: ID of person modifying event
    :param ModifiedDate: ID of person modifying event
    :param AbsenceTypeCode: Absence Type, linked to luAbsenceType
    :param AbsenceReasonCode: Absence Reason, linked to luAbsenceReason
    :param SchoolInOutStatus: Either 'In', 'Out', or ''
    :param EnteredInAdvanceFlag: Entered in Advanced
    :param SystemGeneratedFlag: Generated by the system
    :param SystemProcessNumber: Unknown
    :param NoteReceivedFlag: Whether a note was received
    :param ContactMadeFlag: Contact Made
    :param ApprovedFlag
    :param ReportedByID
    :param ReportedByName
    :param EventComment
    :param LeavingWithID
    :param AbsencePeriodCode
    :param ContactReceivedFlag
    //MasterEndAbsenceEventsSeq
    :param NoteMadeFlag
    :param TerminalCode
    :param LinkedID

    :return:
    """

    # MasterAbsenceEventsSeq should default to AbsenceEventsSeq except when SchoolInOutStatus is both 'In' and 'Out'
    if EventDate is None:
        EventDate = EventDateTime
    if CreatedDate is None:
        CreatedDate = EventDateTime
    if ModifiedByID is None:
        ModifiedByID = CreatedByID
    if ModifiedDate is None:
        ModifiedDate = EventDateTime
    if AbsenceTypeCode is None:
        AbsenceTypeCode = "ABS"

    args = {key: value for key, value in locals().items() if value is not None}
    return AttendanceMaster(**args)
