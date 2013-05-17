from factor import *
import sys


def main(heuristic):
    input()
    variables = [i for i in range(int(input().strip()))]
    cards = [int(i) for i in input().strip().split()]
    cliques =[]
    for i in range(int(input())):
        cliques.append([int(i) for i in input().strip().split()][1:])

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

    Z = joint_distribution(variable_elimination(variables, F, heuristic=heuristic))
    print('Z =', sum(Z.values()))

if __name__ == '__main__':
    args = sys.argv[1:]
    heuristic = args[0] if args else None
    main(heuristic)
