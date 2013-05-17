from itertools import product
from functools import reduce
from operator import mul
from collections import defaultdict

class Factor(dict):
    
    def __init__(self, vars_, vals, card):
        self.card = card
        self.vars = vars_
        self.assignments = [a for a in product(*[list(range(card[n])) for n in vars_])]
        self.update(zip(self.assignments, vals))

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
        for assignment in product(*[range(self.card[v]) for v in vars_]):
            key1 = tuple(assignment[i] for i in ind1)
            key2 = tuple(assignment[i] for i in ind2)
            psi.append(self[key1] * other[key2])
        return Factor(vars_, psi, self.card)

    def __rmul__(self, other):
        return self * other
    
    def __imul__(self, other):
        return self * other

    def __truediv__(self, x):
        return Factor(self.vars, [self[v]/x for v in sorted(self)], self.card)

    def __itruediv__(self, x):
        return self / x

    def normalize(self):
        self /= sum(self.values())


def joint_distribution(cliques):
    return reduce(mul, cliques)

def marginalize(factor, marginal_var):
    ind = factor.vars.index(marginal_var)
    vars_ = factor.vars[:ind]+factor.vars[ind+1:]
    tau = Factor(vars_, [], factor.card)
    for assignment in [a for a in product(*[list(range(factor.card[n])) for n in vars_])]:
        tau[assignment] = sum(factor[assignment[:ind]+(i,)+assignment[ind:]]
                                    for i in range(factor.card[marginal_var]))
    return tau

def _eliminate_var(v, factors):
    used_factors = []
    for factor in factors[:]:
        if v in factor.vars:
            used_factors.append(factor)
            factors.remove(factor)
    psi = joint_distribution(used_factors)
    factors.append(marginalize(psi, v))
    return factors


def variable_elimination(variables, factors, heuristic=None):
    F = factors
    if not heuristic:
        for v in variables:
            F = _eliminate_var(v, F)
    else:
        fn = {'min-neighbor': neighborhood, 'min-weights': weights,
              'min-fill': fill, 'weighted-min-fill': weighted_fill}
        while variables:
            neighbors = defaultdict(set)
            for factor in F:
                for v in factor.vars:
                    neighbors[v] |= set(factor.vars) - {v}
            best = best_var(variables, neighbors, fn[heuristic], factors[0].card)
            _eliminate_var(best, F)
            variables.remove(best)
    return F


def best_var(variables, neighbors, f, cards):
    best = None
    best_val = float('inf')
    for v in neighbors:
        if v in variables:
            temp = f(neighbors, v, cards)
            if temp < best_val:
                best_val = temp
                best = v
    return best



def neighborhood(neighbors, v, *args):
    return len(neighbors[v])


def weights(neighbors, v, card, *args):
   return reduce(mul, [card[i] for i in neighbors[v]], 0)


def fill(neighbors, v, *args):
    fill = 0
    for n in neighbors[v]:
        fill += len(neighbors[v] - neighbors[n])
    return fill

def weighted_fill(neighbors, v, card, *args):
    w_fill = 0
    for n in neighbors[v]:
        fills = neighbors[v] - neighbors[n]
        w_fill += sum(card[n]*card[i] for i in fills)
    return w_fill
    
