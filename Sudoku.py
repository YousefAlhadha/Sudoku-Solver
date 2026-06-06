def unsovable(xss): return any(map(lambda ys:[] in ys,xss))

#easy
sc3 = ".26...81.\n"\
      "3..7.8..6\n"\
      "4...5...7\n"\
      ".5.1.7.9.\n"\
      "..39.51..\n"\
      ".4.3.2.5.\n"\
      "1...3...2\n"\
      "5..2.4..9\n"\
      ".38...46."  

#medium
sc2 = "8156....4\n"\
      "6...75.8.\n"\
      "....9....\n"\
      "9...417..\n"\
      ".4.....2.\n"\
      "..623...8\n"\
      "....5....\n"\
      ".5.91...6\n"\
      "1....7895"
      
#hard          
sc4 = "....6..8.\n"\
      ".2.......\n"\
      "..1......\n"\
      ".7....1.2\n"\
      "5...3....\n"\
      "......4..\n"\
      "..42.1...\n"\
      "3..7..6..\n"\
      ".......5."       

#medium-hard
sc5 = ".5..6...1\n"\
      "..48...7.\n"\
      "8......52\n"\
      "2...57.3.\n"\
      ".........\n"\
      ".3.69...5\n"\
      "79......8\n"\
      ".1...65..\n"\
      "5...3..6."      

# ─────────────────────────────────────────────────────────────
# Aufgabe 1 – readSudoku
# Parse a newline-separated 9×9 string.
# Digits '1'-'9' → single-element list, everything else → [1..9].
# ─────────────────────────────────────────────────────────────
def readSudoku(cs):
    result = []
    for row in cs.split('\n'):
        r = []
        for c in row:
            if c in '123456789':
                r.append([int(c)])
            else:
                r.append([1, 2, 3, 4, 5, 6, 7, 8, 9])
        result.append(tuple(r))
    return tuple(result)


# ─────────────────────────────────────────────────────────────
# Aufgabe 2 – sudoku
# Parse a compact 81-character string where '0' means empty cell.
# ─────────────────────────────────────────────────────────────
def sudoku(s):
    result = []
    for i in range(9):
        row = []
        for j in range(9):
            c = s[i * 9 + j]
            if c != '0':
                row.append([int(c)])
            else:
                row.append([1, 2, 3, 4, 5, 6, 7, 8, 9])
        result.append(tuple(row))
    return tuple(result)

# ─────────────────────────────────────────────────────────────
# Aufgabe 3 – toLaTeX
# Render the sudoku as a LaTeX 'sudoku' environment.
# Cells with exactly one option are printed; multi-option cells stay blank.
# ─────────────────────────────────────────────────────────────
def toLaTeX(xss):
    result = "\\begin{sudoku}\n"
    for row in xss:
        line = ""
        for cell in row:
            if len(cell) == 1:
                line += "|" + str(cell[0])
            else:
                line += "| "
        line += "|.\n"
        result += line
    result += "\\end{sudoku}"
    return result

def transpose(xss): return tuple(zip(*xss))

def rows(x): return x
columns = transpose

# ─────────────────────────────────────────────────────────────
# Aufgabe 4 – boxes
# Rearrange the grid so each 3×3 box occupies one row.
# The transformation is its own inverse: boxes(boxes(xss)) == xss.
#
# Mapping:  new_row  = br*3 + bc
#           new_col  = r*3  + c
#           value    = xss[br*3 + r][bc*3 + c]
# ─────────────────────────────────────────────────────────────
def boxes(xss):
    result = []
    for br in range(3):            # box-row  (0..2)
        for bc in range(3):        # box-col  (0..2)
            row = []
            for r in range(3):     # row within box
                for c in range(3): # col within box
                    row.append(xss[br * 3 + r][bc * 3 + c])
            result.append(tuple(row))
    return tuple(result)

flatten = lambda xs: sum(xs, ())

def correct(xs):
    return all(map(lambda x: len(x) == 1, xs)) and \
           9 == len(set(map(lambda ys: ys[0], xs)))

def solved(xss):
    def okay(xs): return all(map(correct, xs))
    return okay(rows(xss)) and okay(columns(xss)) and okay(boxes(xss))

# ─────────────────────────────────────────────────────────────
# Aufgabe 5 – firstFillings
# Find the first cell that still has multiple options.
# Return one candidate sudoku per option (cell pinned to that value).
# ─────────────────────────────────────────────────────────────
def firstFillings(sudo):
    for i, row in enumerate(sudo):
        for j, cell in enumerate(row):
            if len(cell) > 1:
                result = []
                for val in cell:
                    new_sudo = []
                    for ri, r in enumerate(sudo):
                        new_row = []
                        for ci, c in enumerate(r):
                            if ri == i and ci == j:
                                new_row.append([val])   # pin this cell
                            else:
                                new_row.append(c)       # keep everything else
                        new_sudo.append(tuple(new_row))
                    result.append(tuple(new_sudo))
                return result
    return []   # all cells are already fixed

def bruteForce(xs):
    if solved(xs): return xs
    else:
        for ffs in firstFillings(xs):
            aSol = bruteForce(ffs)
            if aSol: return aSol
        return None


# ─────────────────────────────────────────────────────────────
# Aufgabe 6 – limitLine
# Given a row (or column / box) collect all already-fixed digits,
# then remove those digits from every multi-option cell in the line.
# ─────────────────────────────────────────────────────────────
def limitLine(lls):
    # Collect digits that are already determined (singleton lists)
    fixed = set(cell[0] for cell in lls if len(cell) == 1)
    return tuple(
        cell                                  # keep singletons unchanged
        if len(cell) == 1
        else [v for v in cell if v not in fixed]   # prune fixed digits
        for cell in lls
    )

def limitation(xss):
    def limit(xs): return tuple(map(limitLine, xs))
    return columns(boxes(limit(boxes(limit(columns(limit(rows(xss))))))))

import math
def versions(xss):
    return math.prod(tuple(map(lambda x: len(x), flatten(xss))))

def limitations(lls):
    lls2 = limitation(lls)
    if versions(lls2) == versions(lls): return lls
    else: return limitations(lls2)

def solve(xs):
    lxs = limitations(xs)
    vs = versions(lxs)
    if vs == 0:  return None
    elif vs == 1 and solved(lxs): return lxs
    else:
        for ffs in firstFillings(lxs):
            aSol = solve(ffs)
            if aSol: return aSol
        return None



def moin():
    print(toLaTeX(solve(readSudoku(sc2))))
    print(toLaTeX(solve(readSudoku(sc3))))
    print(toLaTeX(solve(readSudoku(sc4))))
    print(toLaTeX(solve(readSudoku(sc5))))
    
    
t1="000500020000704000000000030028060000000100900030000400000030005800000700100000000"
t2="000500300201000000600000000050000190000460000000020000000000726000801000000000004"
t3="000500300400060000010000000000300120000040000000000700008201000700000064000000009"
t4="000500300400700000100000000070950000020000090000000041800001000090000500000060000"
t5="000500300700004000000000200050320000008000001000600000400071000000000620000000050"
t6="000500300700300000060000000000000407003800000400000060000067100095000000000020000"
t7="000500300800400000100000000095000200030060000000080000700000608000302000000000010"
t8="000500301470020000000000900001600000000090080000000040840000000000301000200000000"
t9="000500301640020000000000800001700000000080090000000040490000000000301000200000000"
t0="000500301680020000000000900001700000000050060000000040260000000000301000400000000"
tA="000500301902800000400000000700630000000000020000000090000084000010000600000009000"
tB="000500301920000000000000007860000040400700000000103000000060090001000000000000500"
tC="000500301920000000000000007860000040400700000000103000000080090001000000000000500"
tD="000500304001007000000000200000046080290000000030080000300200000600000010000000000"
tE="000500306000300400010000000040010002600400000000000010800000500500000070000020000"
tF="000500306920000000000000000000820600009000400100700000000049010003000000060000000"
tG="000500308100070000000000600000091070083000000000000000000600240000308000900000000"
tH="000500308700200000401000000050000800000016000000070000020300400600000010000000000"
tI="000500309820000000000000100760000040000190000400300000001000500000020080000000000"
tJ="000500310240000000080000000001300500000000004000000800000084002300000070000600000"
tK="000500310240000000080000000001300600000000004000000800000084002300000050000700000"
tL="000500320041000000000600000070048000300000200000010000500200060000070004000000000"
tM="000500320041000000000600000070049000300000200000010000800200060000070004000000000"
tN="000500340100600000800000000000010090600080000050000400200070000040300000000000001"
tO="000620800534000000000000000000003047100060000000000050200000100000407000000300000"

ts=[t1,t2,t3,t4,t5,t6,t7,t8,t9,t0,tA,tB,tC,tD,tE,tF,tG,tH,tI,tJ,tK,tL,tM,tN,tO]

import time

def testAufgabe8():
    testSudokus = [t2, t3]

    for i, s in enumerate(testSudokus):
        print("Sudoku", i + 1)

        start = time.time()
        solution = solve(sudoku(s))
        ende = time.time()

        if solution == None:
            print("Keine Lösung gefunden")
        else:
            print("Gelöst")

        print("Laufzeit solve:", ende - start, "Sekunden")
        print()