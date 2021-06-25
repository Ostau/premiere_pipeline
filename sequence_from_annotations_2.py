import pymiere
from pymiere.wrappers import time_from_seconds
from utility_methods import *

project = pymiere.objects.app.project

"""

SCRIPT DESCRIPTION:
Split a cut up podcast into separate projects with the right footage in it.

BY: Volodymyr Loyko

"""

# where the cut footage lives
SOURCE_SEQUENCE = "content"
# what to name the subsequences created
BASE_SEQUENCE_NAME = "armature"
# order of the tracks
TRACKS = {"annotations": 2, "original": 0, "footage": 1} 
# various scaling constants
BUMPER_SCALE_SQUARE = 317
BUMPER_SCALE_VERT = 179
BUMPER_CLIP_LENGTH = 5 # seconds
NUM_ARMATURES = 3

# where certain specific elements live
#yaas_bumper = project.rootItem.children[2].children[0].children[0]
temp_src_copy = dup_seq(SOURCE_SEQUENCE, "temp")

armatures_bin = project.rootItem.createBin(BASE_SEQUENCE_NAME + "s")

print("Clearing source...")
clear_video_track(temp_src_copy, TRACKS["original"])
clear_audio_track(temp_src_copy, TRACKS["original"])


armatures = {}

# loop over each annotation clip
counter = 0
track_num = TRACKS["annotations"]
while track_num < len(temp_src_copy.videoTracks):
    for annotation_clip in temp_src_copy.videoTracks[track_num].clips:
        # get the annotation componenet
        annotation = [comp for comp in annotation_clip.components if comp.displayName == "Graphic Parameters"][0]

        # extract the armature/caption/start/end values
        armature = annotation.properties[0].getValue()['textEditValue']
        caption = annotation.properties[1].getValue()['textEditValue']
        start = annotation_clip.start.seconds
        end = annotation_clip.end.seconds

        print()
        print("Armature: " + armature)

        if (armature in armatures):
            print("Adding to existing sequence...")
            # sequence already exists
            new_seq = armatures[armature]

            # find where the video and audio left off
            move_point_footage = footage_track.clips[len(footage_track.clips) - 1].end.seconds
            move_point_audio = audio_track.clips[len(footage_track.clips) - 1].end.seconds

            # specify the tracks that we'll be using
            src_footage_track = temp_src_copy.videoTracks[TRACKS["footage"]]
            footage_track = new_seq.videoTracks[TRACKS["footage"]]

            src_audio_track = temp_src_copy.audioTracks[TRACKS["footage"]]
            audio_track = new_seq.audioTracks[TRACKS["footage"]]

            print ("Moving clips...")
            # iterate over the original footage and move it to the new sequence
            for footage_clip in src_footage_track.clips:
                if (footage_clip.start.seconds >= end): 
                    break
                elif (footage_clip.start.seconds >= start):
                    # insert the clip
                    footage_track.insertClip(footage_clip.projectItem, time_from_seconds(move_point_footage))

                    # trim it to the right time
                    inserted_clip = footage_track.clips[len(footage_track.clips)-1]
                    inserted_clip.end = time_from_seconds(move_point_footage + footage_clip.duration.seconds)
                    inserted_clip.inPoint = footage_clip.inPoint

                    # update the end point
                    move_point_footage += footage_clip.duration.seconds

                    # trim it to the right time
                    inserted_clip = audio_track.clips[len(audio_track.clips)-1]
                    inserted_clip.end = time_from_seconds(move_point_audio + footage_clip.duration.seconds)
                    inserted_clip.inPoint = footage_clip.inPoint

                    # update the end point
                    move_point_audio += footage_clip.duration.seconds

        else:
            # create a new sequence and remove all of the annotations and source footage
            new_seq_name = BASE_SEQUENCE_NAME + "_" + str(counter)
            new_seq = dup_seq("temp", new_seq_name)
            # move it to the armatures bin
            new_seq.projectItem.moveBin(armatures_bin)
 
            
            print("Filtering and clearing annotations...")
            annot_track_num = TRACKS["annotations"]
            while annot_track_num < len(temp_src_copy.videoTracks):
                for clip in new_seq.videoTracks[annot_track_num].clips:
                    curr_annotation = [comp for comp in clip.components if comp.displayName == "Graphic Parameters"][0]
                    # extract the armature/caption/start/end values
                    curr_armature = curr_annotation.properties[0].getValue()['textEditValue']

                    if (not curr_armature == armature):
                        clip.remove(False, False)
                annot_track_num+=1

            footage_track = new_seq.videoTracks[TRACKS["footage"]]
            audio_track = new_seq.audioTracks[TRACKS["footage"]]

            print("Clearing extra footage...")
            # remove all the clips that are not under the annotations
            clear_track_outside_of(footage_track, start, end)

            print("Clearing extra audio...")
            # remove all the audio clips that are not under the annotations
            clear_track_outside_of(audio_track, start, end)

            print("Pushing footage to front...")
            # push all the clips to the front
            compress_track(footage_track, 0)

            print("Pushing audio to front...")
            # push all the audio clips to the front
            compress_track(audio_track, 0)

            print("Pushing annotations...")
            annot_track_num = TRACKS["annotations"]
            time_pointer = 0
            while annot_track_num < len(temp_src_copy.videoTracks):
                annot_track = new_seq.videoTracks[annot_track_num]
                compress_track(annot_track, time_pointer)
                annot_track_num+=1

            armatures[armature] = new_seq
            counter+=1


        if (counter >= NUM_ARMATURES):
            break
    
    track_num+=1

# Delete the temp source sequence
project.deleteSequence(temp_src_copy)

print()

for i in range(len(armatures)):

    new_seq_name = BASE_SEQUENCE_NAME + "_" + str(i)
    # Duplicate sequence in vertical form
    print("Creating vertical version...")
    new_seq_vert = dup_seq(new_seq_name, new_seq_name+"_9_16")
    new_seq_vert.projectItem.moveBin(armatures_bin)

    # resize the sequence
    settings = new_seq_vert.getSettings()
    settings.videoFrameWidth = 1080
    settings.videoFrameHeight = 1920
    new_seq_vert.setSettings(settings)