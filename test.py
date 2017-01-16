qwe = [(1,2), (3,4), (5,6)]

a = next(((i, c[1]) for i, c in enumerate(qwe) if c[1] >= 4), None)

print(a)