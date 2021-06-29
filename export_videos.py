from utility_methods import *
import time
import sys
import threading

"""

SCRIPT DESCRIPTION:
Export a sequence as a video. Takes one argument, which is the name of the sequence.

BY: Volodymyr Loyko

"""
BASE_PATH = r"/Users/vloyko"
PROJECT_PATH = r"/Desktop/outer_boundaries"
EXPORT_PRESET_PATH = BASE_PATH + PROJECT_PATH + r"/assets/epr/export.epr"
EXPORT_PATH = BASE_PATH + PROJECT_PATH + r"/exports/"
SEQ_NAME = sys.argv[1]

print("Locating sequence...")
arm_seq = [s for s in project.sequences if s.name.endswith(SEQ_NAME)][0]

print()
print("Exporting " + arm_seq.name + "")

result = None

def export():
    global result
    result = arm_seq.exportAsMediaDirect(EXPORT_PATH + arm_seq.name + ".mp4", EXPORT_PRESET_PATH, 2)

thread = threading.Thread(target = export)
thread.start()

thread.join()
print(result)