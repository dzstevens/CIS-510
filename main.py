from factor import Factor
import numpy as np


input()
variables = [i for i in range(int(input()))]
cards = [int(i) for i in input().split(' ')]
cliques =[]
for i in range(int(input())):
    cliques.append([int(i) for i in input().split(' ')][1:])

prev = None
for clique in cliques:
    f = Factor(var=clique, card=cards)
    vals = []
    input()
    n = int(input().strip())
    while len(vals) < n:
        vals += [float(i.strip()) for i in input().strip().split(' ')]
    f.vals = vals
    if prev:
        prev*=f
    else: 
        prev = f
    print(prev)
print('Z =', sum(f.vals))
