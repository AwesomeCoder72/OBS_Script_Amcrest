import requests
from requests.auth import HTTPDigestAuth
from time import perf_counter

url = 'http://192.168.1.200/'

info = 'cgi-bin/ptz.cgi?action=start&channel=0&code=GotoPreset&arg1=0&arg2=2&arg3=0'

full_url = url+info

time_start = perf_counter()
move_camera_request = requests.get(full_url, auth=HTTPDigestAuth('admin', 'password1'))
time_end = perf_counter()

print(f"Request to:\n{full_url}\ntook {time_end-time_start} seconds.")

print(move_camera_request)

