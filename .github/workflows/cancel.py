import base64
import json
import os
import requests
from yaml import load, Loader

data = json.loads(os.getenv("GITHUB_CONTEXT"))
print(data)
token = data["token"]

headers = {"Authorization": "token %s" % token}
def call(method, url):
    res = getattr(requests, method)(url, headers=headers)
    res.raise_for_status()
    return res.json()


path = data["event"]["workflow"]["path"]
cancel = data["event"]["workflow_run"]["cancel_url"]
name = data["event"]["repository"]["name"]
owner = data["event"]["repository"]["owner"]["login"]

data = call("get", "https://api.github.com/repos/%s/%s/contents/%s" % (owner, name, path))
workflow = base64.b64decode(data['content'])
yaml = load(workflow, Loader=Loader)

allowed = ["self-hosted"]
for key in yaml:
    if key != 'jobs':
        continue

    for job in yaml[key].items():
        for runs_on in job[1]["runs-on"].split(" "):
            if runs_on not in allowed:
                print("%s not allowed" % runs_on)
                call("post", cancel)
                print("...cancelled.")
            

