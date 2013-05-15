from factor import Factor
import factor
import numpy

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

prev = None
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
    #print(f)
# reorder the variable base on the count
inds = numpy.argsort(count)
sorted_variable = numpy.take(variables,inds)

prev = factor.sum_product_variable_elimination(sorted_variable,F)

"""if prev:
        prev *= f
    else: 
        prev = f
"""
print('Z =', sum(prev.values()))
