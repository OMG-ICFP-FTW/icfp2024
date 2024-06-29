import copy
import numpy as np
from dataclasses import dataclass
from tabulate import tabulate

def represents_int(s):
    try: 
        int(s)
    except ValueError:
        return False
    else:
        return True


@dataclass
class Atom:
    ty: str
    val: int


class SubmittedException(Exception):
    def __init__(self, result, message):
        self.result = result
        self.message = message
    def __str__(self):
        return self.message


class Timegrid(object):
    def __init__(self, board, A, B):
        rows = board.splitlines()
        self.boards = {}
        self.new_board(1)
        for y, row in enumerate(rows):
            print(row)
            for x, tok in enumerate(row.split(' ')):
                if tok == '.':
                    continue
                elif represents_int(tok):
                    self.write(1, x, y, Atom(ty='N', val=int(tok)))
                elif tok == 'A':
                    self.write(1, x, y, Atom(ty='N', val=A))
                elif tok == 'B':
                    self.write(1, x, y, Atom(ty='N', val=B))
                else:
                    self.write(1, x, y, Atom(ty=tok, val=0))
        print(self.boards[1])

    def new_board(self, t):
        self.boards[t] = {}

    def clone_board(self, t, tc):
        self.boards[t] = copy.deepcopy(self.boards[tc])
        return self.boards[t]

    def write(self, t, x, y, v):
        idx = (x, y)
        old = self.boards[t].get(idx)
        if old != None and old.ty == 'S':
            raise SubmittedException(result=v, message="Submitted")
        self.boards[t][idx] = v
        return old

    def read(self, t, x, y):
        idx = (x, y)
        return self.boards[t].get(idx)

    def board(self, t):
        return self.boards[t]

    def remove(self, t, x, y):
        idx = (x, y)
        if self.boards[t].get(idx) != None:
            #print(f'remove at ({x}, {y}) {self.boards[t]}')
            del self.boards[t][idx]

    def dump(self, t):
        b = self.boards[t]
        idxs = b.keys()
        xs, ys = list(zip(*idxs))
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        dx, dy = maxx-minx+1, maxy-miny+1
        print(minx, maxx, miny, maxy)
        print(dx, dy)
        board = [dx*['.'] for i in range(dy)]
        for idx in idxs:
            x,y = idx
            atom = b[idx]
            if atom.ty == 'N':
                v = atom.val
            else:
                v = atom.ty
            #print('d', v, x, y, minx, miny)
            board[y-miny][x-minx] = v
        #print(board)
        print(tabulate(board, headers='firstrow', tablefmt='fancy_grid'))


class Evaluator(object):
    def __init__(self, board, A, B, step=False):
        self.grid = Timegrid(board, A, B)
        self.t = 1
        self.steps = 0
        self.step = step

    def check_arg(self, x, y):
        t = self.t
        v = self.grid.read(t, x, y)
        return v != None and v.ty != '.'

    def check_arg_num(self, x, y):
        t = self.t
        v = self.grid.read(t, x, y)
        return v != None and v.ty == 'N'

    def eval_step(self):
        g = self.grid
        t = self.t
        nt = t + 1
        b = g.board(t)
        nb = g.clone_board(nt, t)

        nz = b.keys()
        idxs = sorted(list(nz))
        removes = []
        writes = []
        timestep = 1
        for idx in idxs:
            x,y = idx
            atom = g.read(t, x, y)
            #print(f'eval {atom} at ({x}, {y})')
            match atom.ty:
                case '^':
                    if self.check_arg(x, y+1):
                        v = g.read(t, x, y+1)
                        writes.append((nt, x, y-1, v))
                        removes.append((nt, x, y+1))
                case 'v':
                    if self.check_arg(x, y-1):
                        v = g.read(t, x, y-1)
                        writes.append((nt, x, y+1, v))
                        removes.append((nt, x, y-1))
                case '<':
                    if self.check_arg(x+1, y):
                        v = g.read(t, x+1, y)
                        writes.append((nt, x-1, y, v))
                        removes.append((nt, x+1, y))
                case '>':
                    if self.check_arg(x-1, y):
                        v = g.read(t, x-1, y)
                        writes.append((nt, x+1, y, v))
                        removes.append((nt, x-1, y))
                case '+':
                    if self.check_arg_num(x-1, y) and self.check_arg_num(x, y-1):
                        v1 = g.read(t, x-1, y).val
                        v2 = g.read(t, x, y-1).val
                        s = Atom(ty='N', val= v1+v2)
                        writes.append((nt, x+1, y, s))
                        writes.append((nt, x, y+1, s))
                        removes.append((nt, x-1, y))
                        removes.append((nt, x, y-1))
                case '-':
                    if self.check_arg_num(x-1, y) and self.check_arg_num(x, y-1):
                        v1 = g.read(t, x-1, y).val
                        v2 = g.read(t, x, y-1).val
                        s = Atom(ty='N', val= v1-v2)
                        writes.append((nt, x+1, y, s))
                        writes.append((nt, x, y+1, s))
                        removes.append((nt, x-1, y))
                        removes.append((nt, x, y-1))
                case '*':
                    if self.check_arg_num(x-1, y) and self.check_arg_num(x, y-1):
                        v1 = g.read(t, x-1, y).val
                        v2 = g.read(t, x, y-1).val
                        s = Atom(ty='N', val= v1*v2)
                        writes.append((nt, x+1, y, s))
                        writes.append((nt, x, y+1, s))
                        removes.append((nt, x-1, y))
                        removes.append((nt, x, y-1))
                case '/':
                    if self.check_arg_num(x-1, y) and self.check_arg_num(x, y-1):
                        v1 = g.read(t, x-1, y).val
                        v2 = g.read(t, x, y-1).val
                        s = Atom(ty='N', val= v1//v2)
                        writes.append((nt, x+1, y, s))
                        writes.append((nt, x, y+1, s))
                        removes.append((nt, x-1, y))
                        removes.append((nt, x, y-1))
                case '%':
                    if self.check_arg_num(x-1, y) and self.check_arg_num(x, y-1):
                        v1 = g.read(t, x-1, y).val
                        v2 = g.read(t, x, y-1).val
                        s = Atom(ty='N', val= v1%v2)
                        writes.append((nt, x+1, y, s))
                        writes.append((nt, x, y+1, s))
                        removes.append((nt, x-1, y))
                        removes.append((nt, x, y-1))
                case '=':
                    if self.check_arg_num(x-1, y) and self.check_arg_num(x, y-1):
                        v1 = g.read(t, x-1, y).val
                        v2 = g.read(t, x, y-1).val
                        if v1 == v2:
                            e = Atom(ty='N', val=v1)
                            writes.append((nt, x+1, y, e))
                            writes.append((nt, x, y+1, e))
                            removes.append((nt, x-1, y))
                            removes.append((nt, x, y-1))
                    elif self.check_arg(x-1, y) and self.check_arg(x, y-1):
                        t1 = g.read(t, x-1, y).ty
                        t2 = g.read(t, x, y-1).ty
                        if t1 == t2:
                            e = Atom(ty=t1, val=0)
                            writes.append((nt, x+1, y, e))
                            writes.append((nt, x, y+1, e))
                            removes.append((nt, x-1, y))
                            removes.append((nt, x, y-1))
                case '#':
                    if self.check_arg_num(x-1, y) and self.check_arg_num(x, y-1):
                        v1 = g.read(t, x-1, y).val
                        v2 = g.read(t, x, y-1).val
                        if v1 != v2:
                            e1 = Atom(ty='N', val=v1)
                            e2 = Atom(ty='N', val=v2)
                            writes.append((nt, x+1, y, e2))
                            writes.append((nt, x, y+1, e1))
                            removes.append((nt, x-1, y))
                            removes.append((nt, x, y-1))
                    elif self.check_arg(x-1, y) and self.check_arg(x, y-1):
                        t1 = g.read(t, x-1, y).ty
                        t2 = g.read(t, x, y-1).ty
                        if t1 != 'N' and t2 != 'N' and t1 != t2:
                            e1 = Atom(ty=t1, val=0)
                            e2 = Atom(ty=t2, val=0)
                            writes.append((nt, x+1, y, e2))
                            writes.append((nt, x, y+1, e1))
                            removes.append((nt, x-1, y))
                            removes.append((nt, x, y-1))
                case 'S':
                    pass
                case 'A':
                    pass
                case 'B':
                    pass
                case '@':
                    if not self.check_arg_num(x+1, y):
                        continue
                    if not self.check_arg_num(x, y+1):
                        continue
                    if not self.check_arg_num(x-1, y):
                        continue
                    if not self.check_arg(x, y-1):
                        continue
                    dx = g.read(t, x-1, y).val
                    dy = g.read(t, x+1, y).val
                    dt = g.read(t, x, y+1).val
                    if dt < 1:
                        raise ValueError(f'dt must be >= 1 but is {dt}')
                    v = g.read(t, x, y-1)
                    timestep = -dt
                    writes.append((t - dt, x-dx, y-dy, v))
        for remove in removes:
            g.remove(*remove)
        for write in writes:
            g.write(*write)
        return timestep
                    



    def eval(self, max_steps):
        self.grid.dump(1)
        g = self.grid
        for step in range(max_steps):
            try:
                e.t += e.eval_step()
            except SubmittedException(e):
                print(f'Submitted {e.result}')
                break
        self.grid.dump(self.t)


