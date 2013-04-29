from factor import Factor


input()
variables = [i for i in range(int(input().strip()))]
cards = [int(i) for i in input().strip().split()]
cliques =[]
for i in range(int(input())):
    cliques.append([int(i) for i in input().strip().split()][1:])

prev = None
for clique in cliques:
    f = Factor(var=clique, card=cards)
    vals = []
    line = None
    while not line:
        line = input().strip()
    n = int(line)
    while len(vals) < n:
        vals += [float(i) for i in input().strip().split()]
    f.vals = vals
    if prev:
        prev*=f
    else: 
        prev = f
    print(prev)
print('Z =', sum(f.vals))
