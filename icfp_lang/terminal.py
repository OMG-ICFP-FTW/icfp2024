from icfp_lang import service, language

def start():
    command = input("> ")
    while command not in ('end', 'bye', 'stop'):
        print(language.human_readable(service.message(command)))
        command = input("> ")
    print("Goodbye!")


if __name__ == '__main__':
    start()
