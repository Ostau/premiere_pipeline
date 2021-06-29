import pymiere
import time
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
NUM_ARMATURES = 20
PROJECT_PATH = project.path[0:len(project.path)-14]
DEBUG = False

registry = open(PROJECT_PATH+"armature_registry.txt", "w")

# make a temporary copy of source to not destroy anything by accident
temp_src_copy = dup_seq(SOURCE_SEQUENCE, "temp")
empty_annotation = find_project_item("annotation", [])

# create a folder for the short sequences
armatures_bin = project.rootItem.createBin(BASE_SEQUENCE_NAME + "s")

print("Clearing source...")
clear_video_track(temp_src_copy, TRACKS["original"])
clear_audio_track(temp_src_copy, TRACKS["original"])

# dictonary to keep track of seen armatures and their folders
armatures = {}
annotation_time_pointer = {}

# armature counter
counter = 1

# annotion counter
annot_processed = 0

# loop over each annotation track and clip
track_num = TRACKS["annotations"]
while track_num < len(temp_src_copy.videoTracks):
    for annotation_clip in temp_src_copy.videoTracks[track_num].clips:
        # wait for Premiere to catch up
        time.sleep(10)
        annot_processed+=1

        # extract the armature/caption/start/end values
        unwrapped_annot = unwrap_annot(annotation_clip)
        armature = unwrapped_annot[0]
        notes = unwrapped_annot[1]

        # get the start and end of the annotation clip
        start = annotation_clip.start.seconds
        end = annotation_clip.end.seconds

        if DEBUG:
            print("start, end: "+ str(start) + ", " + str(end))

        print()
        print("Armature: " + armature)

        print("- calculating duration of useful clips.")
        track = temp_src_copy.videoTracks[TRACKS["footage"]]
        useful_duration = 0
        for clip in track.clips:
            if (clip.start.seconds >= start and clip.end.seconds <= end):
                useful_duration += clip.duration.seconds
            if (clip.start.seconds >= end):
                break

        if DEBUG:
            print("useful_duration: " + str(useful_duration))

        if (armature in armatures):
            print("- adding to an existing sequence.")
            # sequence already exists
            new_seq = armatures[armature]

            # specify the tracks that we'll be using
            src_footage_track = temp_src_copy.videoTracks[TRACKS["footage"]]
            footage_track = new_seq.videoTracks[TRACKS["footage"]]

            src_audio_track = temp_src_copy.audioTracks[TRACKS["footage"]]
            audio_track = new_seq.audioTracks[TRACKS["footage"]]

            # find where the video and audio left off
            move_point_footage = get_last_clip(footage_track).end.seconds
            move_point_audio = get_last_clip(audio_track).end.seconds
            
            if DEBUG:
                print("move_point_footage: " + str(move_point_footage))
                print("move_point_audio: " + str(move_point_audio))

            print ("- moving clips over")
            # iterate over the original footage and move it to the new sequence
            for footage_clip in src_footage_track.clips:

                if DEBUG:
                    print("footage_clip.start: " + str(footage_clip.start.seconds))
                    print("footage_clip.end: " + str(footage_clip.end.seconds))

                if (footage_clip.start.seconds >= end - 0.0001): 
                    break
                elif (footage_clip.start.seconds >= start):
                    # insert the clip
                    footage_track.insertClip(footage_clip.projectItem, time_from_seconds(move_point_footage))

                    # trim it to the right time
                    inserted_clip = get_last_clip(footage_track)
                    inserted_clip.end = time_from_seconds(move_point_footage + footage_clip.duration.seconds)
                    inserted_clip.inPoint = footage_clip.inPoint

                    # update the end point
                    move_point_footage += footage_clip.duration.seconds

                    # trim it to the right time
                    inserted_audio_clip = get_last_clip(audio_track)
                    inserted_audio_clip.end = time_from_seconds(move_point_audio + footage_clip.duration.seconds)
                    inserted_audio_clip.inPoint = footage_clip.inPoint

                    # update the end point
                    move_point_audio += footage_clip.duration.seconds

            print("- adding associated annotation")
            annot_track_num = TRACKS["annotations"]
            main_annot_track = new_seq.videoTracks[annot_track_num]
            main_annot_track.insertClip(empty_annotation, annotation_time_pointer[armature])
            inserted_annotation = get_last_clip(main_annot_track)
            populate_annot(inserted_annotation, armature, notes)
            inserted_annotation.end = time_from_seconds(annotation_time_pointer[armature] + useful_duration)
            annotation_time_pointer[armature] = inserted_annotation.end.seconds

        else:
            # create a new sequence and remove all of the annotations and source footage
            new_seq_name = BASE_SEQUENCE_NAME + "_" + str(counter) + "_footage"
            new_seq = dup_seq("temp", new_seq_name)
            # move it to the armatures bin
            armature_bin = armatures_bin.createBin(str(counter))
            new_seq.projectItem.moveBin(armature_bin)

            # set the annotation time pointer for this armature to the start
            annotation_time_pointer[armature] = 0
 
            
            print("- clearing annotations")
            annot_track_num = TRACKS["annotations"]
            # iterate over each annotation track
            while annot_track_num < len(temp_src_copy.videoTracks):
                clear_video_track(new_seq, annot_track_num)
                annot_track_num+=1

            footage_track = new_seq.videoTracks[TRACKS["footage"]]
            audio_track = new_seq.audioTracks[TRACKS["footage"]]

            print("- clearing extra footage")
            # remove all the clips that are not under the annotations
            clear_track_outside_of(footage_track, start, end)

            print("- clearing extra audio")
            # remove all the audio clips that are not under the annotations
            clear_track_outside_of(audio_track, start, end)

            print("- pushing footage to front")
            # push all the clips to the front
            compress_track(footage_track, 0)

            print("- pushing audio to front")
            # push all the audio clips to the front
            compress_track(audio_track, 0)

            print("- adding associated annotation")
            
            annot_track_num = TRACKS["annotations"]
            main_annot_track = new_seq.videoTracks[annot_track_num]
            main_annot_track.insertClip(empty_annotation, annotation_time_pointer[armature])
            inserted_annotation = get_last_clip(main_annot_track)
            populate_annot(inserted_annotation, armature, notes)
            inserted_annotation.end = time_from_seconds(annotation_time_pointer[armature] + useful_duration)
            annotation_time_pointer[armature] = inserted_annotation.end.seconds

            armatures[armature] = new_seq
            registry.write(str(counter) + ": " + armature + "\n")
            counter+=1


        if (counter >= NUM_ARMATURES):
            break
    
    track_num+=1

# Delete the temp source sequence
project.deleteSequence(temp_src_copy)

print()

# close the regsitry text file
registry.close()

print()
print("Annotations processed: " + str(annot_processed))
print("Armatures created: " + str(counter))