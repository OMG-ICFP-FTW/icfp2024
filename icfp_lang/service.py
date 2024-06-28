import requests

from icfp_lang import strings
from icfp_lang import language

competition_server = 'https://boundvariable.space/communicate'

def message(msg: str) -> Program:
    send(language.Program(language.String(msg)))

def send(program: Program) -> Program:
    program_message = language.encode(program)
    auth_header = read_auth_header()
    (key, val) = auth_header.split(': ')
    response = requests.post(competition_server, data=program_message, headers={key: val})
    return language.decode(response.content)

def read_auth_header() -> str:
    with open('misc/SUBMISSION_HEADER.txt') as auth_header:
        return auth_header.readlines()[0]
