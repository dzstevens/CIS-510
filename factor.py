import numpy as np
from itertools import product

class Factor(object):
    
    def __init__(self, var=[], vals=[], card=[], name= 'None'):
        """ a factor has list of variables, each with a cardinality, and for each possible assignment to its variable(s),
        a position in the vals array."""
        self.var= np.array(var)
        self.card=card
        self.vals=np.array(vals)
        self.name=name
        self.strides = [0]*len(card)
        prev = None
        for v in reversed(var):
            if not prev:
                self.strides[v] = 1
            else:
                self.strides[v] = self.strides[prev]*card[prev]
            prev = v

    def __str__(self):
        s = '  '.join([chr(65+i) for i in self.var])
        s += '  | {:<5}\n'.format(chr(934))
        s += '-'*len(s) + '\n'
        for i, assignment in enumerate(product(*[list(range(self.card[n])) for n in self.var])):
            s += '  '.join([str(x) for x in assignment])
            s+= '  | {:<5.2}\n'.format(self.vals[i])
        return(s)

    def __mul__(self, other):
        var = sorted(set(self.var) | set(other.var))
        psi = dict()
        j = k = 0
        v = var[0]
        assignment = [0]*len(var)
        for i in range(np.prod([self.card[v] for v in var])):
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
        return Factor(var=var,vals=to_array(psi), card=self.card)


    def __rmul__(self, other):
        return self *other

    
    def __imul__(self, other):
        return self * other


def to_array(d):
    return [d[k] for k in sorted(d)]
