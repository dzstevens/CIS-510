from factor import Factor


input()
variables = [i for i in range(int(input().strip()))]
cards = [int(i) for i in input().strip().split()]
cliques =[]
for i in range(int(input())):
    cliques.append([int(i) for i in input().strip().split()][1:])

prev = None
vals = []
for clique in cliques:
    line = None
    while not vals:
        vals += [float(i) for i in input().strip().split()]
    n = int(vals.pop(0))
    while len(vals) < n:
        vals += [float(i) for i in input().strip().split()]
    f = Factor(clique, vals[:n], cards)
    vals = vals[n:]
    #print(f)
    if prev:
        prev *= f
    else: 
        prev = f

print('Z =', sum(prev.values()))
