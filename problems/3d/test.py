from icfp_lang import service, language


def run_test():
    test = """test 3d 3 4
S < A
"""

    print(test)
    print(language.human_readable(service.message(test)))

if __name__ == '__main__':
    run_test()