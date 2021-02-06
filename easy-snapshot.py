import enum, os, sys, time, glob, argparse, re
from pathlib import Path

# -----------------------------------------------------------------------------
class WorkingMode(enum.Enum):
   error = 0
   save = 1
   restore = 2

# -----------------------------------------------------------------------------
g_Arguments = None

FILE_TAG = 'f'
FOLDER_TAG = 'd'

SAVED_STATE = 'savedState'
RESTORED_STATE = 'restoredState'
CURRENT_STATE = 'currentState'
CHANGED_FILES_DIR = 'changedFilesDir'
ARCHIVER = 'archiver'
LIST_OF_UPDATES = 'listOfUpdates'
COMPARE_WITH = 'compareWith'
FOLDER = 'folder'

# -----------------------------------------------------------------------------
def GetWorkingMode():
   def ReportSaveModeError(Option_):
      sys.stderr.write('Error! Invalid option (' + Option_ + ') for the save mode.')
      os._exit(1)

   def ReportRestoreModeError(Option_):
      sys.stderr.write('Error! Invalid option (' + Option_ + ') for the restore mode.')
      os._exit(1)

   def CheckForFolder():
      if getattr(g_Arguments, FOLDER) == None:
         sys.stderr.write("Error! Folder for snaphot (-f|--folder) was not specified.")
         os._exit(1)

   if getattr(g_Arguments, SAVED_STATE) != None:
      # check for illegal options
      if getattr(g_Arguments, RESTORED_STATE) != None:
         ReportSaveModeError('-r|--restore')
      if getattr(g_Arguments, CURRENT_STATE) != None:
         ReportSaveModeError('-c|--current-state')
      if getattr(g_Arguments, CHANGED_FILES_DIR) != None:
         ReportSaveModeError('-g|--changed-files')
      return WorkingMode.save

   if getattr(g_Arguments, RESTORED_STATE) != None:
      # check for illegal options
      if getattr(g_Arguments, SAVED_STATE) != None:
         ReportSaveModeError('-s|--save')
      if getattr(g_Arguments, COMPARE_WITH) != None:
         ReportSaveModeError('-w|--compare-with')
      if getattr(g_Arguments, LIST_OF_UPDATES) != None:
         ReportSaveModeError('-l|--list-of-updates')
      if getattr(g_Arguments, ARCHIVER) != None:
         ReportSaveModeError('-a|--archiver')
      return WorkingMode.restore
      
   sys.stderr.write("Error! The mode was not specified. Hoy have to specify either save (-s|--save) or restore (-r|--restore) mode.\n\n")
   return WorkingMode.error

   #   if hasattr(g_Arguments, 'restoredStateName'):
   #      sys.stderr.write()
   #g_Arguments.savedStateName = '02.esn'
   #g_Arguments.folder = 'C:\\Data'
   #g_Arguments.compareWith = '01.esn'
   #g_Arguments.listOfUpdates = 'updates.lst'
   #return WorkingMode.save

# -----------------------------------------------------------------------------
def GetFolderState(Folder_):
   FileList = list(Path(Folder_).rglob('*'))
   State = []
   for File in FileList:
      FileState = [FOLDER_TAG if os.path.isdir(File) else FILE_TAG, time.strftime('%Y-%m-%d_%H-%M-%S', time.gmtime(os.path.getmtime(File))), \
         str(os.path.getsize(File)), str(File)]
      State.append(FileState)
   State.sort(key=lambda x: x[3])
   return State

# -----------------------------------------------------------------------------
def SaveFolderState(State_, File_):
   try:
      with open(File_, 'w', encoding='utf-8') as File:
         File.write('# Created by easy-snapshot\n')
         for Item in State_:
            File.write(' '.join(Item) + '\n')
   except Exception as E_:
      sys.stderr.write("Error! Can't write snapshot '" + File_ + "': " + str(E_) + "\n")
      os._exit(1)
   return True

# -----------------------------------------------------------------------------
def ReadFolderState(StateFile_):
   Pattern = re.compile('(f|d)\s+(\d\d\d\d-\d\d-\d\d_\d\d-\d\d-\d\d)\s+(\d+)\s+(\S+)')
   State = []
   try:
      with open(StateFile_, 'r', encoding='utf-8') as File:
         while True:
            Line = File.readline().strip()
            if not Line: 
               break
            if len(Line) == 0 or Line.startswith('#'):
               continue
            Match = Pattern.match(Line)
            if Match == None:
               sys.stderr.write("Error! Invalid snapshot '" + StateFile_ + ".\n")
               os._exit(1)
            State.append([Match.group(1), Match.group(2), Match.group(3), Match.group(4)])

   except Exception as E_:
      print("Error! Can't read snapshot '" + StateFile_ + "': " + str(E_))
      os._exit(1)
   State.sort(key=lambda x: x[3])
   return State

# -----------------------------------------------------------------------------
def SaveListOfUpdates(CurrentState_, OtherState_, File_):
   Diff = []
   CurrentSize = len(CurrentState_)
   OtherSize = len(OtherState_)
   iCurrent = 0
   iOther = 0
   while iCurrent < CurrentSize and iOther < OtherSize:
      #
      while CurrentState_[iCurrent][0] == FOLDER_TAG:
         if iCurrent >= CurrentSize:
            break
         iCurrent += 1
      #
      while OtherState_[iOther][0] == FOLDER_TAG:
         if iOther >= CurrentSize:
            break
         iOther += 1
      #
      CurrentName = CurrentState_[iCurrent][3]
      OtherName = OtherState_[iOther][3]
      if CurrentName < OtherName:
         Diff.append(CurrentState_[iCurrent][3])
         iCurrent += 1
      elif CurrentName > OtherName:
         iOther += 1
      else:
         if CurrentState_[iCurrent][1] != OtherState_[iOther][1] or CurrentState_[iCurrent][2] != OtherState_[iOther][2]:
            Diff.append(CurrentName)
         iCurrent += 1
         iOther += 1
   #            
   try:
      with open(File_, 'w', encoding='utf-8') as File:
         for Item in Diff:
            File.write(Item + '\n')
   except Exception as E_:
      sys.stderr.write("Error! Can't write list of updates '" + File_ + "': " + str(E_) + "\n")
      os._exit(1)

# -----------------------------------------------------------------------------
#class Object(object):
#   pass

# -----------------------------------------------------------------------------
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ArgParser = argparse.ArgumentParser(description='Easy Snapshoter. Saves and restores the state of folders for an incremental backup.')
ArgParser.add_argument('-s', '--save', metavar = '<State file>', type = str, \
   help = 'Save the state of a given folder (-f or --folder) to a file with the given name ', dest = SAVED_STATE)
ArgParser.add_argument('-r', '--restore', type = str, help = 'Restore the state of a given folder (-f or --folder)', dest = RESTORED_STATE)
ArgParser.add_argument('-f', '--folder', type = str, help = 'ToDo', dest = FOLDER)
ArgParser.add_argument('-w', '--compare-with', type = str, help = 'ToDo', dest = COMPARE_WITH)
ArgParser.add_argument('-l', '--list-of-updates', type = str, help = 'ToDo', dest = LIST_OF_UPDATES)
ArgParser.add_argument('-a', '--archiver', type=str, help='ToDo', dest = ARCHIVER)
ArgParser.add_argument('-c', '--current-state', type = str, help = 'ToDo', dest = CURRENT_STATE)
ArgParser.add_argument('-g', '--changed-files', type = str, help = 'ToDo', dest = CHANGED_FILES_DIR)

g_Arguments = ArgParser.parse_args()

#g_Arguments = Object()
Mode = GetWorkingMode()

if Mode is WorkingMode.error:
   ArgParser.print_help()
   os._exit(1)

SAVED_STATE = 'savedState'
RESTORED_STATE = 'restoredState'
CURRENT_STATE = 'currentState'
CHANGED_FILES_DIR = 'changedFilesDir'
ARCHIVER = 'archiver'
LIST_OF_UPDATES = 'listOfUpdates'
COMPARE_WITH = 'compareWith'
FOLDER = 'folder'



if Mode is WorkingMode.save:
   State = GetFolderState(getattr(g_Arguments, FOLDER))
   SaveFolderState(State, getattr(g_Arguments, SAVED_STATE))
   if getattr(g_Arguments, COMPARE_WITH) != None or getattr(g_Arguments, LIST_OF_UPDATES) != None:
      if getattr(g_Arguments, COMPARE_WITH) == None:
         

   if getattr(g_Arguments, 'compareWith') != None and hasattr(g_Arguments, 'listOfUpdates'):
      OtherState = ReadFolderState(g_Arguments.compareWith)
      SaveListOfUpdates(State, OtherState, g_Arguments.listOfUpdates)
else:
   pass