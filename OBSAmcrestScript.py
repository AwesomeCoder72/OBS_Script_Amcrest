import obspython as obs
import requests
from requests.auth import HTTPDigestAuth
import json
import os.path
import sys

print("---------------------------------------------")

scene_preset_dict = {}
scene_name = ""
preset_num = 99
os_username = os.path.expanduser("~")
directory = os_username+"\\obs-amcrest-presets\\"
full_directory = directory+"presets.json"
current_scene_collection = obs.obs_frontend_get_current_scene_collection()


if not os.path.exists(directory):
    os.makedirs(directory)
    print("Created Directory:", directory)
    open(full_directory, 'x').close()
else:
    print("Directory already existed:", directory)
    

def add_to_dict(igmore1, ignore2):
    global current_scene_collection
    global scene_name, preset_num
    global amcrest_IP, amcrest_password, amcrest_username
    if preset_num == 0:
        preset_num = 1

    dict_on_start = {current_scene_collection:{}}
    
    if os.stat(full_directory).st_size == 0:
        with open(full_directory, 'w') as jsonfile:
            json.dump(dict_on_start, jsonfile, indent=4)
    
    with open(full_directory, 'r') as jsonfile:
        json_dict = json.load(jsonfile)
    
    json_dict_scene_preset = json_dict[current_scene_collection]
    json_dict_scene_preset.update({scene_name:[amcrest_IP, amcrest_username, amcrest_password, preset_num]})
        
    with open(full_directory, 'w') as jsonfile:
        json.dump(json_dict, jsonfile, indent=4)
        
    with open(full_directory, 'r') as jsonfile:
        json_dict = json.load(jsonfile)
        
    
    move_camera(json_dict[current_scene_collection][scene_name])
    
    
def del_from_dict(props, prop):
    global current_scene_collection
    global scene_name
    try:
        with open(full_directory, 'r') as jsonfile:
            json_dict = json.load(jsonfile)
        print(f'Deleted Camera Preset: {scene_name} from Scene:{json_dict[current_scene_collection][scene_name][0]}')
        del(json_dict[current_scene_collection][scene_name])
        with open(full_directory, 'w') as jsonfile:
            json.dump(json_dict,jsonfile,indent=4)
    
    except:
        pass        
    
# def ignore_func(ignore1, ignore2):
#     pass
    

# def add_but(ignore1, ignore2):
#     global props
#     obs.obs_properties_add_button(props, "new_but", "Button!", ignore_func)
#     print('did it?')

def script_properties():
    global props
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "amcrest_IP", "IP", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "amcrest_username", "Username", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "amcrest_password", "Password", obs.OBS_TEXT_DEFAULT)
    
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

    obs.obs_properties_add_button(props, "del", "Delete Camera Preset Scene", del_from_dict)

    obs.obs_properties_add_int(props, "preset", "Preset:",
                                    1, 25, 1) # min, max, step
    
    obs.obs_properties_add_button(props, "add", "Add Camera Preset Scene", add_to_dict)
     
    # obs.obs_properties_add_button(props, "add_button", "Add Button.", add_but)
    
    return props

def script_update(settings):
    """
    Called when the script’s settings (if any) have been changed by the user.
    """
    global scene_name, preset_num, amcrest_IP, amcrest_username, amcrest_password
    
    scene_name = obs.obs_data_get_string(settings, "scene")
    preset_num = obs.obs_data_get_int(settings, "preset")
    
    amcrest_IP       = obs.obs_data_get_string(settings, "amcrest_IP")
    amcrest_username = obs.obs_data_get_string(settings, "amcrest_username")
    amcrest_password = obs.obs_data_get_string(settings, "amcrest_password")


    
def move_camera(move_info):
    info = f'cgi-bin/ptz.cgi?action=start&channel=0&code=GotoPreset&arg1=0&arg2={move_info[3]}&arg3=0'
    protocol = "http://"+move_info[0]+"/"
    full_url = protocol+info
    
    move_request = requests.get(full_url, auth=HTTPDigestAuth(move_info[1], move_info[2]))
    if move_request.status_code == 200:
        helpful_string = "Moved camera successfully!" 
    
    elif move_request.status_code == 404:
        helpful_string = "Could not request from URL."

    elif move_request.status_code == 401:
        helpful_string = "Invalid username and/or password."    
    
    return f"{helpful_string} {move_request}"


def on_event(event):
    global current_scene_collection
    # if event == obs.OBS_FRONTEND_EVENT_PREVIEW_SCENE_CHANGED:
    #     print("Preview Scene changed!")
    try:
        with open(full_directory, 'r') as jsonfile:
            json_dict = json.load(jsonfile)

        if event == obs.OBS_FRONTEND_EVENT_PREVIEW_SCENE_CHANGED:
            current_scene = obs.obs_frontend_get_current_scene()
            current_scene_name = obs.obs_source_get_name(current_scene)
            current_preview_scene = obs.obs_frontend_get_current_preview_scene()
            current_preview_scene_name = obs.obs_source_get_name(current_preview_scene)
            if current_scene_name not in json_dict[current_scene_collection]:
                print(f'Moving to preset: {json_dict[current_scene_collection][current_preview_scene_name]}!')
                print(move_camera(json_dict[current_scene_collection][current_preview_scene_name]))
            obs.obs_source_release(current_preview_scene)
            current_preview_scene = None
            obs.obs_source_release(current_scene)
            current_scene = None
            
        elif event == obs.OBS_FRONTEND_EVENT_SCENE_CHANGED:
            current_scene = obs.obs_frontend_get_current_scene()
            current_scene_name = obs.obs_source_get_name(current_scene)
            print(f'Moving to preset: {json_dict[current_scene_collection][current_scene_name]}!')
            print(move_camera(json_dict[current_scene_collection][current_scene_name]))
            obs.obs_source_release(current_scene)
            current_scene = None
            
        elif event == obs.OBS_FRONTEND_EVENT_EXIT:
            obs.sceneitem_list_release(current_scene_collection)
            current_scene_collection = None
            
    except KeyError:
        pass
    
    if event == obs.OBS_FRONTEND_EVENT_SCENE_COLLECTION_CHANGED:
        current_scene_collection = obs.obs_frontend_get_current_scene_collection()
        with open(full_directory, 'r') as jsonfile:
            json_dict = json.load(jsonfile)
            
        if current_scene_collection not in json_dict:
            json_dict.update({current_scene_collection:{}})
            with open(full_directory, 'w') as jsonfile:
                json.dump(json_dict, jsonfile, indent=4)
            
    
def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)
