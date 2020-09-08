import obspython as obs
import requests
from requests.auth import HTTPDigestAuth
import json
import os
import sys

scene_preset_dict = {}
scene_name = ""
preset_num = 2
change_desc = "This is a new description!!!!"

json_file_path = "\\Users\\Noah\\AppData\\Local\\Programs\\Python\\Python36\\OBSScripts\\data_for_amcrest.json"

def add_to_dict(props, prop):
    global scene_name, preset_num
    
    with open(json_file_path, "r") as jsonfile:
        json_dict = json.load(jsonfile)
        
    scene_collections_dict = json_dict["SceneCollections"]
    current_scene_collection_dict = scene_collections_dict["Living room Amcrest"]

    current_scene_collection_dict.update({scene_name:preset_num})
    
    with open(json_file_path, "w") as jsonfile:
        json.dump(json_dict, jsonfile, indent=4)
    
    print(scene_preset_dict)
    
def del_from_dict(props, prop):
    global scene_name
    try:
        with open(json_file_path, "r") as jsonfile:
            json_dict = json.load(jsonfile)
            
        scene_collections_dict = json_dict["SceneCollections"]
        current_scene_collection_dict = scene_collections_dict["Living room Amcrest"]
        
        del(current_scene_collection_dict[scene_name])
        
        with open(json_file_path, "w") as jsonfile:
            json.dump(json_dict, jsonfile, indent=4)
        
    finally:
        print(scene_preset_dict)
        
def script_description():
    global change_desc
    return change_desc

    
def script_properties():
    props = obs.obs_properties_create()
    scene_prop = obs.obs_properties_add_list(props, "scene", "Scene:",
                                    obs.OBS_COMBO_TYPE_LIST,
                                    obs.OBS_COMBO_FORMAT_STRING)
    scenes = obs.obs_frontend_get_scenes()
    if scenes is not None:
        for i in range(len(scenes)):
            scene_name_in_loop = obs.obs_frontend_get_scene_names()[i]
            obs.obs_property_list_add_string(scene_prop, scene_name_in_loop, scene_name_in_loop)

        obs.source_list_release(scenes)
        scenes = None

    obs.obs_properties_add_button(props, "del", "Delete from Dict.", del_from_dict)

    preset_prop = obs.obs_properties_add_int(props, "preset", "Preset:",
                                    1, 25, 1) # min, max, step
    
    obs.obs_properties_add_button(props, "add", "Add to Dict.", add_to_dict)
    
    dict_prop = obs.obs_properties_add_list(props, "dict", "Scene Name/Preset",
                                             obs.OBS_COMBO_TYPE_EDITABLE,
                                             obs.OBS_COMBO_FORMAT_STRING)
    
    
    return props

def script_update(settings):
    global change_desc
    """
    Called when the script’s settings (if any) have been changed by the user.
    """
    global scene_name, preset_num
    
    scene_name = obs.obs_data_get_string(settings, "scene")
    preset_num = obs.obs_data_get_int(settings, "preset")
    
    change_desc = "HAHAHAH you found me!"
    
    script_description()
url = 'http://192.168.1.200/'

def move_camera(scene_name):
    info = f'cgi-bin/ptz.cgi?action=start&channel=0&code=GotoPreset&arg1=0&arg2={scene_name}&arg3=0'
    full_url = url+info
    
    print(requests.get(full_url, auth=HTTPDigestAuth('admin', 'password1')))


def on_event(event):
    # if event == obs.OBS_FRONTEND_EVENT_PREVIEW_SCENE_CHANGED:
    #     print("Preview Scene changed!")
    try:
        if event == obs.OBS_FRONTEND_EVENT_PREVIEW_SCENE_CHANGED:
            current_scene = obs.obs_frontend_get_current_scene()
            current_scene_name = obs.obs_source_get_name(current_scene)
            current_preview_scene = obs.obs_frontend_get_current_preview_scene()
            current_preview_scene_name = obs.obs_source_get_name(current_preview_scene)
            if current_scene_name not in scene_preset_dict:
                print(f"Moving to preset: {scene_preset_dict[current_preview_scene_name]}!")
                move_camera(scene_preset_dict[current_preview_scene_name])
            obs.obs_source_release(current_preview_scene)
            current_preview_scene = None
            obs.obs_source_release(current_scene)
            current_scene = None
            
        elif event == obs.OBS_FRONTEND_EVENT_SCENE_CHANGED:
            current_scene = obs.obs_frontend_get_current_scene()
            current_scene_name = obs.obs_source_get_name(current_scene)
            print(f"Moving to preset: {scene_preset_dict[current_scene_name]}!")
            move_camera(scene_preset_dict[current_scene_name])
            obs.obs_source_release(current_scene)
            current_scene = None
            
    except KeyError:
        pass
    
def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)
