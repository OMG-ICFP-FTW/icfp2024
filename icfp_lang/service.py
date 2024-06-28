import requests

from icfp_lang import language

competition_server = 'https://boundvariable.space/communicate'

def message(msg: str) -> language.Program:
    return send(language.Program(language.Value(msg)))


def send(program: language.Program) -> language.Program:
    program_message = language.encode(program)
    auth_header = read_auth_header()
    (key, val) = auth_header.split(': ')
    response = requests.post(
        competition_server, data=program_message, headers={key: val})
    return language.decode(str(response.content, 'utf-8'))


def read_auth_header() -> str:
    with open('misc/SUBMISSION_HEADER.txt') as auth_header:
        return auth_header.readlines()[0].strip()
