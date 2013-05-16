from factor import *
import numpy as np

input()
variables = [i for i in range(int(input().strip()))]
cards = [int(i) for i in input().strip().split()]
cliques =[]
for i in range(int(input())):
    cliques.append([int(i) for i in input().strip().split()][1:])
count = [0]*len(variables)
for clique in cliques:
    for v in variables:
        if v in clique: 
            count[v] += 1 

vals = []
F=[]
for clique in cliques:
    line = None
    while not vals:
        vals += [float(i) for i in input().strip().split()]
       
    n = int(vals.pop(0))
    #print (n)
    while len(vals) < n:
        vals += [float(i) for i in input().strip().split()]
    f = Factor(clique, vals[:n], cards)
    vals = vals[n:]
    F.append(f)

# reorder the variable base on the count
inds = np.argsort(count)
sorted_variable = np.take(variables,inds)

Z = variable_elimination(sorted_variable,F)
print('Z =', sum(Z.values()))