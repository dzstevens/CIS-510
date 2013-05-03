from itertools import product
from functools import reduce
import operator


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


def marginalize(marginal_vars, factors):
    all_vars = set.union(*[set(factor.vars) for factor in F])
    marginalized_vars = [all_vars - set(marginal_vars)]
    joint = Factor.joint_distribution(factors)
    joint.normalize()
    return FactorMarginalization(joint, marginalized_vars) #what is this?


def _eliminate_var(v, factors):
    used_factors = {f for f in factors if v in f.var}
    psi = joint_distribution(used_factors)
    tau = marginalize([v], psi)
    return [set(factors) - used_factors] + [tau]


def sum_product_variable_elimination(variables, factors):
    F = []
    for v in variables:
        F += _eliminate_var(v, factors)
    return reduce(mul, F)

