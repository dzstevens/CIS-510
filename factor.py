from itertools import product
from functools import reduce
import operator


class Factor(object):
    
    def __init__(self, var=[], vals=[], card=[]):
        """ a factor has list of variables, each with a cardinality, and for each possible assignment to its variable(s),
        a position in the vals array."""
        self.var= var
        self.card=card
        self.vals=vals
        self.strides = [0]*len(card)
        prev = None
        for v in reversed(var):
            if not prev:
                self.strides[v] = 1
            else:
                self.strides[v] = self.strides[prev]*card[prev]
            prev = v

    def __str__(self):
        vars_ = [chr(65+i) for i in self.var]
        s = '  '.join(vars_)
        s += '    {:<5}\n'.format(chr(934)+'(' + ', '.join(vars_)+')')
        line = '–'*len(s) + '\n'
        s += line
        for i, assignment in enumerate(product(*[list(range(self.card[n])) for n in self.var])):
            s += '  '.join([str(x) for x in assignment])
            s+= '    {:<5.3}\n'.format(self.vals[i])
        s += line
        return(s)

    def __mul__(self, other):
        var = sorted(set(self.var) | set(other.var))
        psi = dict()
        j = k = 0
        v = var[0]
        assignment = [0]*len(var)
        for i in range(self.prod([self.card[v] for v in var])):
            psi[tuple(assignment)] = self.vals[j]*other.vals[k]
            for l,v in enumerate(var):
                assignment[l] = (assignment[l] + 1) % self.card[v]
                if not assignment[l]:
                    j -= (self.card[v] - 1) * self.strides[v]
                    k -= (self.card[v] - 1) * other.strides[v]
                else:
                    j += self.strides[v] 
                    k += other.strides[v]
                    break
        psi = [psi[k] for k in sorted(psi)]
        return Factor(var=var,vals=psi, card=self.card)


    def __rmul__(self, other):
        return self *other

    
    def __imul__(self, other):
        return self * other

    @staticmethod
    def prod(l):
        p = 1
        for i in l:
            p *= i
        return p


def joint_distribution(cliques):
    return reduce(mul, cliques)


def marginalize(marginal_vars, factors):
    all_vars = set.union(*[set(factor.var) for factor in F])
    marginalized_vars = [all_vars - marginal_vars]
    joint = Factor.joint_distribution(factors)
    Z = sum(joint.vals)
    joint.vals = [val/Z for val in joint.vals]
    return FactorMarginalization(joint, marginalized_vars) #what is this?


def _eliminate_var(v, factors):
    used_factors = {f for f in factors if v in f.var}
    psi = Factor.joint_distribution(used_factors)
    tau = marginalize(psi,[v])
    return [set(factors) - used_factors] + [tau]


def sum_product_variable_elimination(variables, factors):
    F = []
    for v in variables:
        F += _eliminate_var(v, factors)
    return reduce(mul, F)

