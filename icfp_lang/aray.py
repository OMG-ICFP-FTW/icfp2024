#!/usr/bin/env python
# %% Run as jupyter notebook inside of vscode

'''
ICFP language

An Interstellar Communication Functional Program (ICFP) consists of a list of space-separated tokens. A token consists of one or more printable ASCII characters, from ASCII code 33 ('!') up to and including code 126 ('~'). In other words, there are 94 possible characters, and a token is a nonempty sequence of such characters.

The first character of a token is called the indicator, and determines the type of the token. The (possibly empty) remainder of the token is called body. The different token types are explained in the next subsections.
Booleans

indicator = T and an empty body represents the constant true, and indicator = F and an empty body represents the constant false.
Integers

indicator = I, requires a non-empty body.

The body is interpreted as a base-94 number, e.g. the digits are the 94 printable ASCII characters with the exclamation mark representing 0, double quotes 1, etc. For example, I/6 represent the number 1337.
Strings

indicator = S

The Cult of the Bound variable seems to use a system similar to ASCII to encode characters, but ordered slightly differently. Specifically, ASCII codes 33 to 126 from the body can be translated to human readable text by converting them according to the following order:

abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&'()*+,-./:;<=>?@[\]^_`|~<space><newline>

Here <space> denotes a single space character, and <newline> a single newline character. For example, SB%,,/}Q/2,$_ represents the string "Hello World!".
Unary operators

indicator = U, requires a body of exactly 1 character long, and should be followed by an ICFP which can be parsed from the tokens following it.
Character	Meaning	Example
-	Integer negation	U- I$ -> -3
!	Boolean not	U! T -> false
#	string-to-int: interpret a string as a base-94 number	U# S4%34 -> 15818151
$	int-to-string: inverse of the above	U$ I4%34 -> test

The -> symbol in this table should be read as "will evaluate to", see Evaluation.
Binary operators

indicator = B, requires a body of exactly 1 character long, and should be followed by two ICFPs (let's call them x and y).
Character	Meaning	Example
+	Integer addition	B+ I# I$ -> 5
-	Integer subtraction	B- I$ I# -> 1
*	Integer multiplication	B* I$ I# -> 6
/	Integer division (truncated towards zero)	B/ U- I( I# -> -3
%	Integer modulo	B% U- I( I# -> -1
<	Integer comparison	B< I$ I# -> false
>	Integer comparison	B> I$ I# -> true
=	Equality comparison, works for int, bool and string	B= I$ I# -> false
|	Boolean or	B| T F -> true
&	Boolean and	B& T F -> false
.	String concatenation	B. S4% S34 -> "test"
T	Take first x chars of string y	BT I$ S4%34 -> "tes"
D	Drop first x chars of string y	BD I$ S4%34 -> "t"
$	Apply term x to y (see Lambda abstractions)	
If

indicator = ? with an empty body, followed by three ICFPs: the first should evaluate to a boolean, if it's true then the second is evaluated for the result, else the third. For example:

? B> I# I$ S9%3 S./

evaluates to no.
Lambda abstractions

indicator = L is a lambda abstraction, where the body should be interpreted as a base-94 number in the same way as integers, which is the variable number, and it takes one ICFP as argument. indicator = v is a variable, with again a body being the base-94 variable number.

When the first argument of the binary application operator $ evaluates to a lambda abstraction, the second argument of the application is assigned to that variable. For example, the ICFP

B$ B$ L# L$ v# B. SB%,,/ S}Q/2,$_ IK

represents the program (e.g. in Haskell-style)

((\v2 -> \v3 -> v2) ("Hello" . " World!")) 42

which would evaluate to the string "Hello World!".
Evaluation

The most prevalent ICFP messaging software, Macroware Insight, evaluates ICFP messages using a call-by-name strategy. This means that the binary application operator is non-strict; the second argument is substituted in the place of the binding variable (using capture-avoiding substitution). If an argument is not used in the body of the lambda abstraction, such as v3 in the above example, it is never evaluated. When a variable is used several times, the expression is evaluated multiple times.

For example, evaluation would take the following steps:

B$ L# B$ L" B+ v" v" B* I$ I# v8
B$ L" B+ v" v" B* I$ I#
B+ B* I$ I# B* I$ I#
B+ I' B* I$ I#
B+ I' I'
I-

Limits

As communication with Earth is complicated, the Cult seems to have put some restrictions on their Macroware Insight software. Specifically, message processing is aborted when exceeding 10_000_000 beta reductions. Built-in operators are strict (except for B$, of course) and do not count towards the limit of beta reductions. Contestants' messages therefore must stay within these limits.

For example, the following term, which evaluates to 16, uses 109 beta reductions during evaluation:

B$ B$ L" B$ L# B$ v" B$ v# v# L# B$ v" B$ v# v# L" L# ? B= v# I! I" B$ L$ B+ B$ v" v$ B$ v" v$ B- v# I" I%

Researchers expect that the limit on the amount beta reductions is the only limit that contestants may run into, but there seem to also be some (unknown) limits on memory usage and total runtime.
'''


# %% imports
import requests
import os
import json
import hashlib
import time
import random
from dataclasses import dataclass, field

# %% file paths and constants

post_addr = "https://boundvariable.space/communicate"
# Authorization header
auth_path = '../misc/SUBMISSION_HEADER.txt'
with open(auth_path, 'r') as file:
    auth = file.read()
assert auth.startswith("Authorization: Bearer ")
# convert to dict for requests
auth = {"Authorization": auth.lstrip("Authorization: ").strip()}

# Cache for requests and responses, as simple json files
cache_path = '../cache/'
os.makedirs(cache_path, exist_ok=True)

# %% decode and encode

str_reference = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n"
decode_map = {chr(k): v for (k, v) in zip(list(range(33,33 + len(str_reference))),str_reference)}
encode_map = {v: k for (k, v) in decode_map.items()}
decode_trans = str.maketrans(decode_map)
encode_trans = str.maketrans(encode_map)

def decode(s):
    assert isinstance(s, str), f"Expected string, got {type(s)}"
    assert s.startswith("S"), f"Expected string, got {s}"
    return s[1:].translate(decode_trans)

def encode(s):
    assert isinstance(s, str), f"Expected string, got {type(s)}"
    return "S" + s.translate(encode_trans)


assert encode("Hello World!") == "SB%,,/}Q/2,$_", encode("Hello World!")
assert decode("SB%,,/}Q/2,$_") == "Hello World!", decode("SB%,,/}Q/2,$_")

# %% cache requests with the server

def request(s, force=False):
    assert isinstance(s, str), f"Expected string, got {type(s)}"
    assert not s.startswith("S"), "Send bare string not encoded"
    data = encode(s)
    filename = hashlib.sha256(data.encode()).hexdigest()
    filepath = os.path.join(cache_path, filename)
    if force or not os.path.exists(filepath) and not force:
        time.sleep(5)
        response = requests.post(post_addr, headers=auth, data=data)
        response.raise_for_status()
        decoded = decode(response.text)
        with open(filepath, 'w') as file:
            json.dump({"request": s, "encoded":data, "response": response.text, "decoded": decoded}, file)
    with open(filepath, 'r') as file:
        return json.load(file)

request('get index')

# %% lambdaman
'''
Welcome to the Lambda-Man course.

It was the year 2014, and many members of our community worked hard to control Lambda-Man. Now, ten years later, this wonderful event is still memorized by holding a small Lambda-Man competition.

This course will teach you how to optimally control Lambda-Man to eat all pills. There is no fruit involved (neither low-hanging nor high-hanging), and even better: no ghosts! The input to each problem is a simple rectangular grid such as the following:

```
###.#...
...L..##
.#######
```

The grid contains exactly one `L` character, which is the starting position of Lambda-Man. There will be one or more `.` characters indicating the locations of pills to be eaten, and `#` characters are walls. The outside boundary of the grid is considered to consist of walls as well.

A solution should be a string of `U`, `R`, `D` and `L` characters (up, right, down, left, respectively) indicating the path to take. For example, a possible solution to the above example grid is the following path:
```
LLLDURRRUDRRURR
```
When Lambda-Man is instructed to move into a square containing a wall, nothing happens and the instruction is skipped. Your solution may consist of at most `1,000,000` characters.

The following levels are available:
* [lambdaman1] Best score: 33.
* [lambdaman2] Best score: 44.
* [lambdaman3] Best score: 58.
* [lambdaman4] Best score: 176.
* [lambdaman5] Best score: 159.
* [lambdaman6] Best score: 73.
* [lambdaman7] Best score: 181.
* [lambdaman8] Best score: 143.
* [lambdaman9] Best score: 116.
* [lambdaman10] Best score: 857.
* [lambdaman11] Best score: 1668.
* [lambdaman12] Best score: 1668.
* [lambdaman13] Best score: 1668.
* [lambdaman14] Best score: 1668.
* [lambdaman15] Best score: 1668.
* [lambdaman16] Best score: 2633.
* [lambdaman17] Best score: 991.
* [lambdaman18] Best score: 4361.
* [lambdaman19] Best score: 5122.
* [lambdaman20] Best score: 6489.
* [lambdaman21] Best score: 10609.

To submit a solution, send an ICFP expression that evaluates to:

```
solve lambdamanX path
```

Your score is number of bytes that the ICFP expressions consists of (i.e. the size of the POST body), so a lower score is better.
'''


@dataclass
class LambdaMan:
    X: int
    grid: list
    solution: str = ''

    def __str__(self):
        return '\n'.join(''.join(row) for row in self.grid)

    @property
    def height(self):
        return len(self.grid)
    
    @property
    def width(self):
        return len(self.grid[0])

    @property
    def remaining(self):
        """ number of remaining pills """
        return sum(row.count('.') for row in self.grid)
    
    @property
    def L(self):
        """ location of Lambda in the grid """
        for i, row in enumerate(self.grid):
            if 'L' in row:
                return (i, row.index('L'))
        raise ValueError("No Lambda in the grid")
    
    def step(self, direction):
        """ Move Lambda in the given direction """
        assert direction in 'UDLR', f"Expected one of 'UDLR', got {direction}"
        src = self.L
        x, y = src
        if direction == 'U':
            assert x > 0, f"Cannot move up from {self.L}"
            x -= 1
        elif direction == 'D':
            assert x < self.height - 1, f"Cannot move down from {self.L}"
            x += 1
        elif direction == 'L':
            assert y > 0, f"Cannot move left from {self.L}"
            y -= 1
        elif direction == 'R':
            assert y < self.width - 1, f"Cannot move right from {self.L}"
            y += 1
        dst = (x, y)
        if 0 <= x < self.height and 0 <= y < self.width and self.grid[x][y] != '#':
            # move Lambda
            self.grid[dst[0]][dst[1]] = 'L'
            # previous space is now empty
            self.grid[src[0]][src[1]] = ' '
            # add to solution
            self.solution += direction
        else:
            raise ValueError(f"Cannot move {direction} from {self.L} in:\n{self}")
        print(f"Moved {direction} from {self.L} to {(x, y)} in:\n{self}")

    def pills(self):
        """ All remaining pill locations as (x, y) """
        for i, row in enumerate(self.grid):
            for j, c in enumerate(row):
                if c == '.':
                    yield (i, j)
    
    def random_pill(self):
        """ Return a random pill location """
        return random.choice(list(self.pills()))
    
    def neighbors(self, x, y):
        """ Neighbors of a location """
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.height and 0 <= ny < self.width and self.grid[nx][ny] != '#':
                yield (nx, ny)
    
    def flood_path(self, dst):
        """ flood-fill to find a path to get to a location """
        src = self.L
        queue = [dst]
        visited = set()
        parent = {src: None}  # map from location to parent location
        while queue:
            x, y = queue.pop(0)
            visited.add((x, y))
            if (x, y) == src:
                break
            for nx, ny in self.neighbors(x, y):
                if (nx, ny) not in visited:
                    parent[(nx, ny)] = (x, y)
                    queue.append((nx, ny))
        else:
            raise ValueError(f"No path from {src} to {dst}. in {self}")
        print("Parents", parent)
        # step back to find the path
        path = []
        x, y = src
        while (x, y) != dst:
            path.append((x, y))
            x, y = parent[(x, y)]
        path.append(dst)
        print("Path", path)
        # convert to directions
        directions = []
        for (ny, nx), (y, x) in zip(path, path[1:]):
            if x < nx:
                assert y == ny, f"Invalid path from {src} to {dst}"
                directions.append('L')
            elif x > nx:
                assert y == ny, f"Invalid path from {src} to {dst}"
                directions.append('R')
            elif y < ny:
                assert x == nx, f"Invalid path from {src} to {dst}"
                directions.append('U')
            elif y > ny:
                assert x == nx, f"Invalid path from {src} to {dst}"
                directions.append('D')
            else:
                raise ValueError(f"Invalid path from {src} to {dst}")
        print("Directions", directions)
        # take steps
        for direction in directions:
            self.step(direction)

    def solve(self):
        print("Solving level", self.X)
        while self.remaining:
            pill = self.random_pill()
            print("Pill", pill, "remaining", self.remaining)
            self.flood_path(pill)
            assert self.L == pill, f"Lambda did not reach pill {pill} in:\n{self}"
            print("Current solution", self.solution)
        return self.solution

    @classmethod
    def get(cls, i):
        assert isinstance(i, int) and 1 <= i <= 21, f"Expected int in [1,21], got {i}"
        level = request(f"get lambdaman{i}")['decoded']
        # convert to list of lists
        level = [list(row) for row in level.strip().split('\n')]
        # assert all rows are the same length
        assert all(len(row) == len(level[0]) for row in level), level
        return cls(i, level)

for i in range(1, 6):
    print(f"Level {i}")
    level = LambdaMan.get(i)
    print(level)
    level.solve()
    level.solution
    print("Solution", level.solution)
    response = request(f"solve lambdaman{i} " + level.solution)
    print(response['decoded'])


# %%
lm_cache_path = '../lambdaman/'
os.makedirs(lm_cache_path, exist_ok=True)
for i in range(1, 6):
    level = LambdaMan.get(i)
    with open(os.path.join(lm_cache_path, f"level{i}.txt"), 'w') as file:
        file.write(str(level))
