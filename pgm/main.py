import argparse
import time
import pgm.util as util


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='python -m pgm.main', 
                                     description='This program is use to create and manipulate '
                                                 'probabilistic graphical models')
    parser.add_argument('model', help='the model file for your network')
    parser.add_argument('function', help='the function to perform on your network. '
                                         'Current choices: joint_distribution, '
                                         'variable_elimination, partition_function, map')
    parser.add_argument('-e', '--evidence', help='an evidence file to condition on')
    parser.add_argument('-u', '--heuristic', help='the heuristic to be used when performing '
                                                  'variable elimination. If not specified, '
                                                  'variables will be simply be eliminated in '
                                                  'the order they were given. Current choices: '
                                                  'min_neighbor, min_weights, min_fill, weighed_min_fill')
    parser.add_argument('-v', '--vars', help='The list of variables for variable elimination'
                                              'or MAP inference',
                        nargs='+', type=int, default=[])
    parser.add_argument('-t', '--time', help='Set this to get timing stats at runtinme',
                        action='store_true')

    args = parser.parse_args()
    network = util.create_network(args.model)
    if args.evidence:
        evidence = util.get_evidence(args.evidence)
        network.condition(evidence)
    if args.time:
        start = time.time()
    if args.function == 'joint_distribution':
        print(network.joint_distribution())
    elif args.function == 'partition_function':
        network.partition_function(args.heuristic)
#        print('Z =', network.partition_function(args.heuristic))
    elif args.function == 'variable_elimination':
        print(network.variable_elimination(args.vars, args.heuristic))
    elif args.function == 'map':
        assignment, prob = network.map(args.vars)
        print('Max assignment:\n')
        for v, a in assignment.items():
                print('{} = {}'.format(v, a))
        print('\nProbability:', prob)

    if args.time:
        print('Runtime: {:.3} ms'.format((time.time() - start)*1000))
