
from pymiere.wrappers import time_from_seconds
from utility_methods import *

"""

SCRIPT DESCRIPTION:
Take annotatoted short sequences and add visual elements along with rearranging the videos.

BY: Volodymyr Loyko

"""

BUMPER_NAME = "bumper.mp4"
BASE_SEQUENCE_NAME = "armature"
BUMPER_LENGTH = 5 #seconds
BUMPER_SCALE = 179
VIDEO_SCALE = 134
VIDEO_W = 540.0/1080.0
VIDEO_H = 722.0/1920.0
YAAS_CAPTION = "yaas_caption_1"
YAAS_CAPTION_SQUARE = "yaas_caption_square"
YAAS_CAPTION_TIK_TOK = "yaas_caption_tik_tok"
SEQ_TAG = "_footage"
NUM_ARMATURES = 20

print("Locating footage sequences...")
arm_seq_list = [s for s in project.sequences if s.name.endswith(SEQ_TAG)]
print("Collected sequences...")

bumper = find_project_item(BUMPER_NAME, ["armatures"])
print("Found bumper...")
yaas_caption = find_project_item(YAAS_CAPTION, ["armatures"])
yaas_caption_square = find_project_item(YAAS_CAPTION_SQUARE, ["armatures"])
yaas_caption_tik_tok = find_project_item(YAAS_CAPTION_TIK_TOK, ["armatures"])
print("Found captions...")

print("Creating additional sequence versions...")
counter = 1
arm_seq_vert_list = []
arm_seq_tik_tok_list = []
arm_seq_square_list = []
for arm_seq in arm_seq_list:

    seq_name = arm_seq.name
    seq_name_base = seq_name[0:len(seq_name)-8]
    seq_idx = int(seq_name_base[9 : len(seq_name_base)])
    #print(seq_idx)
    armature_bin = project.rootItem.children[4].children[seq_idx-1]
    #print(armature_bin.name)
    # Duplicate sequence in vertical form
    new_seq_vert = dup_seq(seq_name, seq_name_base+"_9_16")
    new_seq_vert.projectItem.moveBin(armature_bin)

    # resize the sequence
    settings = new_seq_vert.getSettings()
    settings.videoFrameWidth = 1080
    settings.videoFrameHeight = 1920
    new_seq_vert.setSettings(settings)
    arm_seq_vert_list.append(new_seq_vert)

    # Duplicate sequence in square form
    new_seq_square = dup_seq(seq_name, seq_name_base+"_1_1")
    new_seq_square.projectItem.moveBin(armature_bin)

    # resize the sequence
    settings = new_seq_square.getSettings()
    settings.videoFrameWidth = 1920
    settings.videoFrameHeight = 1920
    new_seq_square.setSettings(settings)
    arm_seq_square_list.append(new_seq_square)

    # Duplicate sequence in vertical form for tik tok
    new_seq_tik_tok = dup_seq(seq_name, seq_name_base+"_tik_tok")
    new_seq_tik_tok.projectItem.moveBin(armature_bin)

    # resize the sequence
    settings = new_seq_tik_tok.getSettings()
    settings.videoFrameWidth = 1080
    settings.videoFrameHeight = 1920
    new_seq_tik_tok.setSettings(settings)
    arm_seq_tik_tok_list.append(new_seq_tik_tok)

    counter+=1
    if (counter >= NUM_ARMATURES):
            break

# iterate over each armature sequence
def insert_graphic_elements(seq_list, caption, video_w, video_h, video_scale, bumper_scale, caption_scale):
    counter = 1
    for arm_seq in seq_list:
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
            clip_set_scale(caption_clip, caption_scale)
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

        clip_set_scale(inserted_bumper, bumper_scale)

        caption_track_audio = arm_seq.audioTracks[3]
        inserted_bumper_audio = get_last_clip(caption_track_audio)
        inserted_bumper_audio.end = time_from_seconds(inserted_bumper_audio.start.seconds + BUMPER_LENGTH)

        print("- resizing video")
        # resize the footage
        for clip in footage_track.clips:
            clip_set_scale(clip, video_scale)
            clip_set_position(clip, video_w, video_h)
        
        counter += 1
        if counter >= NUM_ARMATURES:
            break

insert_graphic_elements(arm_seq_vert_list, yaas_caption, 540.0/1080.0, 824.0/1920.0, 197, 179, 101)
insert_graphic_elements(arm_seq_square_list, yaas_caption_square, 960.0/1920.0, 757.0/1920.0, 214, 315, 100)
insert_graphic_elements(arm_seq_tik_tok_list, yaas_caption_tik_tok, 540.0/1080.0, 699.0/1920.0, 134, 179, 101)