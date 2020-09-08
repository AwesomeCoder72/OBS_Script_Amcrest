from requests.auth import HTTPDigestAuth

requests.get('http://192.168.1.200/cgi-bin/ptz.cgi?action=start&channel=0&code=GotoPreset&arg1=0&arg2=2&arg3=0',
              auth=HTTPDigestAuth('admin', 'password1'))