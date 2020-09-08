import obspython as obs
import requests
from requests.auth import HTTPDigestAuth

# sources = obs.obs_frontend_get_scenes()
# for source in sources:
#     scene = obs.obs_scene_from_source(source)


scene_names = obs.obs_frontend_get_scene_names()

print(f"All scenes: {scene_names}") # We don't even have to release this! 


url = 'http://192.168.1.200/'



def move_camera(scene_name):
    info = f'cgi-bin/ptz.cgi?action=start&channel=0&code=GotoPreset&arg1=0&arg2={scene_name}&arg3=0'
    full_url = url+info
    
    print(requests.get(full_url, auth=HTTPDigestAuth('admin', 'password1')))



def on_event(event):
    if event == obs.OBS_FRONTEND_EVENT_SCENE_CHANGED:
        current_scene = obs.obs_frontend_get_current_scene()
        current_scene_name = obs.obs_source_get_name(current_scene)
        print(f"Moving to preset: {scene_preset_dict[current_scene_name]}!")
        move_camera(scene_preset_dict[current_scene_name])
        obs.obs_source_release(current_scene)

def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)
    
