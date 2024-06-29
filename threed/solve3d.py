from threed import threedlang
import argparse

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-m','--max_iters', type=int, default=1000000, help='Max iters of VM')
    parser.add_argument('-f','--file', help='Source file with grid', required=True)
    parser.add_argument('-s','--step', help='Single step mode', default=False, action='store_true')
    parser.add_argument('A', nargs='?', default=0, type=int)
    parser.add_argument('B', nargs='?', default=0, type=int)

    args = parser.parse_args()

    e = threedlang.Evaluator(open(args.file).read(), args.A, args.B, step=args.step)
    if args.step:
        getch = _Getch()
        g = e.grid
        do = True
        while do:
            e.grid.dump(e.t)
            c = getch()
            if c == '>' or c == '.':
                try:
                    e.t += e.eval_step()
                except threedlang.SubmittedException as se:
                    print(f'Submitted {se.result}')
                    do =  False
                continue
            # elif c == '<' or c == ',':
            #     if e.t > 1:
            #         e.t -= 1
            #     continue
            elif c == 'q':
                break
    else:
        e.eval(args.max_iters)
