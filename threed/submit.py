from icfp_lang import language, service
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Submit 3d solution from file')
    parser.add_argument('-f','--file', help='Source file with grid', required=True)
    parser.add_argument('N', type=int)
    args = parser.parse_args()

    problem = args.N
    solution = open(args.file).read()
    args = parser.parse_args()
    solve_cmd = f'''solve 3d{problem}
{solution}
'''
    resp = service.send(language.Program(language.Value(solve_cmd)))
    print('response:')
    print(language.String.parse(resp))
