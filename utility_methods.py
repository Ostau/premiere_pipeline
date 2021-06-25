
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
        elif (clip.end.seconds < start):
            clip.remove(False, False)
        elif (clip.start.seconds >= end):
            passed = True
            clip.remove(False, False)