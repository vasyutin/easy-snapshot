import enum, os, sys, time, glob, argparse
from pathlib import Path

# -----------------------------------------------------------------------------
class WorkingMode(enum.Enum):
   error = 0
   save = 1
   restore = 2

# -----------------------------------------------------------------------------
g_Arguments = None

# -----------------------------------------------------------------------------
def GetWorkingMode():
   return WorkingMode.save

# -----------------------------------------------------------------------------
def GetFolderState(Folder_):
   FileList = list(Path(Folder_).rglob('*'))
   print(FileList)
   return {}

# -----------------------------------------------------------------------------
def SaveFolderState(State_, File_):
   return True

# -----------------------------------------------------------------------------
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ArgParser = argparse.ArgumentParser(description='Easy Snapshoter. Saves and restores the state of folders for an incremental backup.')
ArgParser.add_argument('-s', '--save', metavar='<State file>', type=str, \
   help='Save the state of a given folder (-f or --folder) to a file with the given name ', dest='savedStateName')
ArgParser.add_argument('-r', '--restore', type=str, help='Restore the state of a given folder (-f or --folder)', dest='restoredStateName')
ArgParser.add_argument('-f', '--folder', type=str, help='ToDo', dest='folder')
ArgParser.add_argument('-w', '--compare-with', type=str, help='ToDo', dest='compareWith')
ArgParser.add_argument('-l', '--list-of-changes', type=str, help='ToDo', dest='listOfChanges')
ArgParser.add_argument('-a', '--archiver', type=str, help='ToDo', dest='archiver')
ArgParser.add_argument('-c', '--current-state', type=str, help='ToDo', dest='currentState')
ArgParser.add_argument('-g', '--changed-files', type=str, help='ToDo', dest='changedFilesDir')

g_Arguments = ArgParser.parse_args()
Mode = GetWorkingMode()
if Mode is WorkingMode.error:
   exit(1)

if Mode is WorkingMode.save:
   State = GetFolderState(g_Arguments.folder)
   SaveFolderState(State, g_Arguments.savedStateName)
