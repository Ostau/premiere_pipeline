
from pymiere.wrappers import time_from_seconds
from utility_methods import *

"""

SCRIPT DESCRIPTION:
Take annotatoted short sequences and add visual elements along with rearranging the videos.

BY: Volodymyr Loyko

"""

BUMPER_NAME = "bumper.mp4"
BUMPER_LENGTH = 5 #seconds
BUMPER_SCALE = 179
VIDEO_SCALE = 134
VIDEO_W = 540.0/1080.0
VIDEO_H = 722.0/1920.0
CAPTION_NAME = "yaas_caption"
SEQ_TAG = "_9_16"
NUM_ARMATURES = 3

print("Locating elements...")
arm_seq_list = [s for s in project.sequences if s.name.endswith(SEQ_TAG)]
print("Collected sequences...")

bumper = find_project_item(BUMPER_NAME, ["armatures"])
print("Found bumper...")
caption = find_project_item(CAPTION_NAME, ["armatures"])
print("Found caption...")

# iterate over each armature sequence
counter = 1
for arm_seq in arm_seq_list:
    print()
    print("Adding graphic elements to " + arm_seq.name + ":")
    # identify target tracks in the sequence
    caption_track = arm_seq.videoTracks[3]
    footage_track = arm_seq.videoTracks[1]
    annot_track = arm_seq.videoTracks[2]

    print("- adding captions")
    # process each annotation in the sequence
    for annotation_clip in annot_track.clips:
        # extract elements of the annotation
        annotation = unwrap_annot_shallow(annotation_clip)

        # insert the caption graphic and trim it
        caption_track.insertClip(caption, annotation_clip.start)
        caption_clip = get_last_clip(caption_track)
        caption_clip.end = annotation_clip.end

        # update the caption text
        caption_comp = [comp for comp in caption_clip.components if comp.displayName == "Graphic Parameters"][0]
        caption_comp.properties[0].setValue(annotation[0].upper(), False)

    print("- muting annotation track")
    annot_track.setMute(1)

    print("- adding bumper")
    # insert the bumper and trim/scale it
    caption_track.insertClip(bumper, get_last_clip(caption_track).end)
    inserted_bumper = get_last_clip(caption_track)
    inserted_bumper.end = time_from_seconds(inserted_bumper.start.seconds + BUMPER_LENGTH)

    clip_set_scale(inserted_bumper, BUMPER_SCALE)

    caption_track_audio = arm_seq.audioTracks[2]
    inserted_bumper_audio = get_last_clip(caption_track_audio)
    inserted_bumper_audio.end = time_from_seconds(inserted_bumper_audio.start.seconds + BUMPER_LENGTH)

    print("- resizing video")
    # resize the footage
    for clip in footage_track.clips:
        clip_set_scale(clip, VIDEO_SCALE)
        clip_set_position(clip, VIDEO_W, VIDEO_H)
    
    counter += 1
    if counter >= NUM_ARMATURES:
        break