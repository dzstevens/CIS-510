import argparse
import pgm.networks as networks
import pgm.util as util

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
    parser = argparse.ArgumentParser(prog='python -m pgm.main', 
                                     description='This program is use to create and manipulate '
                                                 'probabilistic graphical models')
    parser.add_argument('model', help='the model file for your network')
    parser.add_argument('function', help='the function to perform on your network. '
                                         'Current choices: joint_distribution, '
                                         'variable_elimination, partition_function')
    parser.add_argument('-e', '--evidence', help='an evidence file to condition on')
    parser.add_argument('-u', '--heuristic', help='the heuristic to be used when performing '
                                                  'variable elimination. If not specified, '
                                                  'variables will be simply be eliminated in '
                                                  'the order they were given')
    parser.add_argument('-v', '--vars', help='The list of variables you wish to eliminate.',
                        nargs='+', type=int, default=[])
    parser.add_argument('-i','--var1s',help = 'MAP inference on the list of variables.',
                        nargs='+', type=int, default=[])
    args = parser.parse_args()
    network = util.create_network(args.model)
    if args.evidence:
        evidence = util.get_evidence(args.evidence)
        network.condition(evidence)
    if args.function == 'joint_distribution':
        print(network.joint_distribution())
    elif args.function == 'partition_function':
        print('Z =', network.partition_function(args.heuristic))
    elif args.function == 'variable_elimination':
        print(network.variable_elimination(args.vars, args.heuristic))
    elif args.function == 'map':
        print(network.map(args.vars))
