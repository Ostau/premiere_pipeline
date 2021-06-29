
import pymiere
from pymiere.wrappers import time_from_seconds

project = pymiere.objects.app.project

# HELPER FUNCTIONS

"""
Clear clips from a video track in a sequence.

seq             reference to sequence
track_num       number of the track to clear clips from
"""
def clear_video_track(seq, track_num):
    for clip in seq.videoTracks[track_num].clips:
        clip.remove(False, False)
    
"""
Clear clips from a audio track in a sequence.

seq             reference to sequence
track_num       number of the track to clear clips from
"""
def clear_audio_track(seq, track_num):
    for clip in seq.audioTracks[track_num].clips:
        clip.remove(False, False)    


"""
Duplicate a sequence.

seq_name        name of the original sequence
new_seq_name    the desired name for the new sequence

returns         reference to the new sequence
"""
def dup_seq(seq_name, new_seq_name):
    # clone the original sequence
    get_seq_ref(seq_name).clone() 
    # find the copy
    new_seq = get_seq_ref(seq_name+" Copy")
    # rename it to the right name
    new_seq.name = new_seq_name

    return new_seq


"""
Get sequence reference from name.

seq_name        name of the sequence
returns         sequence reference
"""
def get_seq_ref(seq_name):
    return [s for s in project.sequences if s.name == seq_name][0]

"""
Compress track by removing all empty spaces between clips and pushing everything to front.

track           track object
return          end of compressed segment
"""
def compress_track(track, start):
    move_pointer = start
    for footage_clip in track.clips:
        duration = footage_clip.duration.seconds
        footage_clip.start = time_from_seconds(move_pointer)
        footage_clip.end = time_from_seconds(move_pointer + duration)
        move_pointer = footage_clip.end.seconds
    return move_pointer


"""
Clears all clips in the track outside of start to end

track           track object
start           start in seconds
end             end in seconds
"""
def clear_track_outside_of(track, start, end):
    passed = False

    for clip in track.clips:
        if (passed):
            # if we've passed the end of the annotation
            clip.remove(False, False)
        elif (clip.end.seconds <= start):
            clip.remove(False, False)
        elif (clip.start.seconds >= end):
            passed = True
            clip.remove(False, False)


"""
Finds the project item in the media browser that matches the name given.

name            name of the project item sought
skip            list of names to skip
return          reference to item if found, None otherwise
"""
def find_project_item(name, skip):
    # BFS over project item structure
    visited = []
    queue = []

    root = project.rootItem
    queue.append(root)
    visited.append(root.name)

    while queue:
        s = queue.pop(0)

        if (s in skip):
            visited.append(s)
            continue

        if (s.name == name):
                return s

        if(s.children):
            for child in s.children:
                if not child.name in visited:
                    queue.append(child)
                    visited.append(child.name)

    return None


"""
Extract armature and notes from an annotation clip.

annotation_clip     clip that contains the annotation mogrt
return              a list with armature as the first element and notes as the second
"""
def unwrap_annot(annotation_clip):
    annotation = [comp for comp in annotation_clip.components if comp.displayName == "Graphic Parameters"][0]

    # extract the armature/notes values
    armature = annotation.properties[0].getValue()['textEditValue']
    notes = annotation.properties[1].getValue()['textEditValue']

    return [armature, notes]

"""
Extract armature and notes from an annotation clip.

annotation_clip     clip that contains the annotation mogrt
return              a list with armature as the first element and notes as the second
"""
def unwrap_annot_shallow(annotation_clip):
    annotation = [comp for comp in annotation_clip.components if comp.displayName == "Graphic Parameters"][0]

    # extract the armature/notes values
    armature = annotation.properties[0].getValue()
    notes = annotation.properties[1].getValue()

    return [armature, notes]

"""
Returns the last clip of the track

track               track to be searched
return              reference to the last clip     
"""
def get_last_clip(track):
    return track.clips[len(track.clips) - 1]

"""
Poplate the armature and notes of a new annotation cllip

annotation clip     clip containing the annotation component
armature            armature statemenet
notes               notes
"""
def populate_annot(annotation_clip, armature, notes):
    annotation = [comp for comp in annotation_clip.components if comp.displayName == "Graphic Parameters"][0]

    # set the armature/notes values
    annotation.properties[0].setValue(armature, False)
    annotation.properties[1].setValue(notes, False)

"""
Scale a clip.

clip            clip to be scaled
scale           scale value
"""
def clip_set_scale(clip, scale):
    motion = [comp for comp in clip.components if comp.displayName == "Motion"][0]

    # set the armature/notes values
    motion.properties[1].setValue(scale, False)

"""
Move a clip.

clip            clip to be moved
w               width
h               height
"""
def clip_set_position(clip, w, h):
    motion = [comp for comp in clip.components if comp.displayName == "Motion"][0]

    # set the armature/notes values
    motion.properties[0].setValue([w,h], False)