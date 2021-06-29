"""
This demo show basic interactions with Premiere Pro using the Pymiere library.
It will display some info about the currently opened project in Premiere Pro and an action in the timeline.
Before running this script make sure that you have a Premiere project opened with at least a sequence.
"""
import pymiere
# new sequences are created from sqpreset files  
# basic presets come installed with Premiere and can be accessed using
from pymiere.wrappers import get_system_sequence_presets  

for sequence in pymiere.objects.app.project.sequences:
    pymiere.objects.app.project.deleteSequence(sequence)  

