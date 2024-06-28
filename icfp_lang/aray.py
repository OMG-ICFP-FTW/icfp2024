#!/usr/bin/env python
# Run as jupyter notebook inside of vscode
# %%
import requests

# talk to server
post_addr = "https://boundvariable.space/communicate"
auth_path = '../misc/SUBMISSION_HEADER.txt'
with open(auth_path, 'r') as file:
    auth = file.read()
assert auth.startswith("Authorization: Bearer ")
# convert to dict for requests
auth = {"Authorization": auth.lstrip("Authorization: ").strip()}

send_msg = "S'%4}).$%8"
# post to the server, with the auth header
response = requests.post(post_addr, headers=auth, data=send_msg)
print(response.text)