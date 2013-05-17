from itertools import product
from functools import reduce
from operator import mul
from collections import defaultdict


class Factor(dict):
    
    def __init__(self, vars_, vals, net):
        self.vars = vars_
        self.network = net
        assignments = [a for a in product(*[list(range(net.card[n]))
                                            for n in vars_])]
        self.update(zip(assignments, vals))

    def __str__(self):
        vars_ = [chr(65+i) for i in self.vars]
        s = '  '.join(vars_)
        s += '    {:<5}\n'.format(chr(934)+'(' + ', '.join(vars_)+')')
        line = '–'*len(s) + '\n'
        s += line
        for assignment in sorted(self):
            s += '  '.join([str(x) for x in assignment])
            value = self[assignment]
            s += '    '
            if isinstance(value, float):
                s += '{:<5.3}\n'.format(value)
            else:
                s += '{:<5}\n'.format(value)
        s += line
        return(s)

    def __mul__(self, other):
        vars_ = sorted(set(self.vars + other.vars))
        ind1 = tuple(vars_.index(v) for v in self.vars if v in vars_)
        ind2 = tuple(vars_.index(v) for v in other.vars if v in vars_)
        psi = []
        for assignment in product(*[range(self.network.card[v]) for v in vars_]):
            key1 = tuple(assignment[i] for i in ind1)
            key2 = tuple(assignment[i] for i in ind2)
            psi.append(self[key1] * other[key2])
        return Factor(vars_, psi, self.network)

    def __rmul__(self, other):
        return self * other
    
    def __imul__(self, other):
        return self * other

    def __truediv__(self, x):
        return Factor(self.vars, [self[v]/x for v in sorted(self)],
                      self.network.card)

    def __itruediv__(self, x):
        return self / x

    def normalize(self):
        self /= sum(self.values())

    def marginalize(self, v):
        ind = self.vars.index(v)
        vars_ = self.vars[:ind]+self.vars[ind+1:]
        tau = {}
        for assignment in [a for a in product(*[list(range(self.network.card[n]))
                                              for n in vars_])]:
            tau[assignment] = sum(self[assignment[:ind]+(i,)+assignment[ind:]]
                                        for i in range(self.network.card[v]))
        self.clear()
        self.update(tau)
        self.vars.remove(v)


class Network:

    def __init__(self, vars_, factors=[], card={}, ntype='MARKOV'):
        self.ntype=ntype
        self.card = card
        self.factors = factors
        self.vars = vars_

    def __str__(self):
        return '\n\n'.join([str(f) for f in self.factors])

    def add_factor(self, factor):
        self.factors.append(factor)

    def remove_factor(self, factor):
        self.factors.remove(factor)

    def joint_distribution(self, factors=None):
        if not factors:
            factors = self.factors
        return reduce(mul, factors)

    def partition_function(self, heuristic=None):
        self.variable_elimination(self.vars[:], heuristic)
        return sum(self.joint_distribution().values())

    def eliminate_var(self, v):
        used_factors = []
        for factor in self.factors[:]:
            if v in factor.vars:
                used_factors.append(factor)
                self.remove_factor(factor)
        psi = self.joint_distribution(used_factors)
        psi.marginalize(v)
        self.add_factor(psi)
        self.vars.remove(v)

    def variable_elimination(self, variables, heuristic=None):
        if not heuristic:
            for v in variables:
                self.eliminate_var(v)
        else:
            fn = {'min-neighbor     ': self._num_neighbors,
                  'min-weights'      : self._weights,
                  'min-fill'         : self._fill,
                  'weighted-min-fill': self._weighted_fill}

            while variables:
                best = self._best_var(variables, fn[heuristic], factors[0].card)
                eliminate_var(best)
                variables.remove(best)
        return self

    def _best_var(self, variables, f):
        best = None
        best_val = float('inf')
        neighbors = defaultdict(set)
        for factor in self.factors:
            for v in factor.vars:
                self.neighbors[v] |= set(factor.vars) - {v}

        for v in neighbors:
            if v in variables:
                temp = f(neighbors, v)
                if temp < best_val:
                    best_val = temp
                    best = v
        return best

    def _num_neighbors(self, neighbors, v):
        return len(neighbors[v])

    def _weights(self, neighbors, v):
       return reduce(mul, [self.card[i] for i in neighbors[v]], 0)

    def _fill(self, neighbors, v):
        fill = 0
        for n in neighbors[v]:
            fill += len(neighbors[v] - neighbors[n])
        return fill

    def _weighted_fill(self, neighbors, v):
        w_fill = 0
        for n in neighbors[v]:
            fills = neighbors[v] - neighbors[n]
            w_fill += sum(self.card[n] * self.card[i]
                          for i in fills)
        return w_fill    
