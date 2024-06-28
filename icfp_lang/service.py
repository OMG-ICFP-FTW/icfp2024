import requests

from icfp_lang import strings
from icfp_lang import language

competition_server = 'https://boundvariable.space/communicate'

def message(msg: str) -> Program:
    send(language.String(msg))

def send(program: Program) -> Program:
    program_message = language.serialize(program)
    requests.post(competition_server, headers={"Content-Type":"text"})
