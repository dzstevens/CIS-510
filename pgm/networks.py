from itertools import product
from functools import reduce
from operator import mul
from collections import defaultdict
from multiprocessing import Process, Pipe


class Factor(dict):
    
    def __init__(self, vars_, vals, net):
        self.vars = vars_
        self.network = net
        assignments = [a for a in product(*[net.card[v] for v in vars_])]
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

    def copy(self):
        vals = [self[i] for i in sorted(self)]
        return Factor(self.vars, vals, self.network)

    def __mul__(self, other):
        vars_ = sorted(set(self.vars + other.vars))
        ind1 = tuple(vars_.index(v) for v in self.vars if v in vars_)
        ind2 = tuple(vars_.index(v) for v in other.vars if v in vars_)
        psi = []
        for assignment in product(*[self.network.card[v] for v in vars_]):
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
                      self.network)

    def __itruediv__(self, x):
        return self / x

    def condition(self, evidence):
        for var, val in evidence.items():
            if var in self.vars:
                ind = self.vars.index(var)
                for assignment in list(self):
                    if assignment[ind] != val:
                        del self[assignment]

    def normalize(self):
        self.update(self/sum(self.values()))

    def marginalize(self, v):
        ind = self.vars.index(v)
        vars_ = self.vars[:ind]+self.vars[ind+1:]
        tau = {}
        for assignment in [a for a in product(*[self.network.card[n] for n in vars_])]:
            for i in self.network.card[v]:
                tau[assignment] = sum(self[assignment[:ind]+(i,)+assignment[ind:]]
                                      for i in self.network.card[v])
        self.clear()
        self.update(tau)
        self.vars.remove(v)


class Network:

    def __init__(self, factors=[], card=[], ntype='MARKOV'):
        self.ntype=ntype
        self.card = {i: list(range(v)) for i, v in enumerate(card)}
        self.factors = factors

    def __str__(self):
        return '\n\n'.join([self.ntype] + [str(f) for f in self.factors])

    def add_factor(self, factor):
        self.factors.append(factor)

    def remove_factor(self, factor):
        self.factors.remove(factor)

    def condition(self, evidence):
        for var, val in evidence.items():
            self.card[var] = [val]
        for factor in self.factors:
            factor.condition(evidence)

    def joint_distribution(self, factors=None):
        if not factors:
            factors = self.factors
        joint = reduce(mul, factors)
        joint.normalize()
        return joint

    def partition_function(self, heuristic=None):
        self.variable_elimination(list(self.card), heuristic)
        return sum(self.joint_distribution().values())

    def eliminate_var(self, v):
        used_factors = []
        new_factors = []
        for factor in self.factors[:]:
            if v in factor.vars:
                used_factors.append(factor)
            else:
                new_factors.append(factor)
        psi = self.joint_distribution(used_factors)
        psi.marginalize(v)
        self.factors = new_factors + [psi]
        del self.card[v]

    def variable_elimination(self, variables, heuristic=None):
        if not heuristic:
            for v in variables:
                self.eliminate_var(v)
        else:
            fn = {'min-neighbor'      : self._num_neighbors,
                  'min-weights'       : self._weights,
                  'min-fill'          : self._fill,
                  'weighted-min-fill' : self._weighted_fill}

            while variables:
                best = self._best_var(variables, fn[heuristic])
                self.eliminate_var(best)
                variables.remove(best)
        return self.joint_distribution()

    def map(self,variables):

        inference_variables = list(set(self.card)-set(variables)) 
        f1=self.variable_elimination(inference_variables)
        f2 = self.joint_distribution(f1.factors)
        f2.assignments = [a for a in product(*[f2.network.card[v] for v in f2.vars])]
        f2.update(zip(f2.assignments,f2.values()))
        f2.normalize()
        max_assignment = max(f2, key=lambda x: f2[x])
        return dict(zip(variables, max_assignment)), f2[max_assignment]

    def loopy_bp(self, threshold=0.0001, iterations=50):
        var_map = defaultdict(list)
        for i, f in enumerate(self.factors):
            for v in f.vars:
                var_map[v].append(i)
        # msg[f,v] = m(f->v), m(v->f)
        msgs = {(f,v): [None, None] for v in var_map
                                for f in var_map[v]}  
        converged = {(f,v): [False, False] for v in var_map
                                for f in var_map[v]}  
        for i in range(iterations):
            done = True
            for v, factors in var_map.items():
                for f in factors:
                    if not converged[f, v][1]:
                        done = False
                        neighbors = set(factors) - {f}
                        msg = self._mul_msgs(v, [msgs[n, v][0] for n in neighbors])
                        if msgs[f, v][1] is None or abs(1 - msg[0]/msgs[f, v][1][0]) > threshold:
                            msgs[f, v][1] = msg
                        else:
                            converged[f, v][1] = True

            for i, f in enumerate(self.factors):
                for v in f.vars:
                    if not converged[i, v][0]:
                        done = False
                        temp = f.copy()
                        neighbors = set(f.vars) - {v}
                        for n, m in [(n, msgs[i, n][1]) for n in neighbors]:
                            if m is not None:
                                temp *= Factor([n], m, self)
                        for n in neighbors:
                            temp.marginalize(n)
                        temp.normalize()
                        msg = tuple(temp[val] for val in sorted(temp))
                        if msgs[i, v][0] is None or abs(1 - msg[0]/msgs[i, v][0][0]) > threshold:
                            msgs[i, v][0] = msg
                        else:
                            converged[i, v][0] = True
            if done:
                break

        marginals = []
        for v, factors in var_map.items():
            neighbors = set(factors)
            msg = self._mul_msgs(v, [msgs[n, v][0] for n in neighbors])
            marginal = Factor([v], msg, self)
            marginal.normalize()
            marginals.append(marginal)
        return marginals

    def _mul_msgs(self, v, msgs):
        msg = (1, ) * len(self.card[v])
        for m in msgs:
            if m is not None:
                msg = tuple(msg[i] * val for i, val in enumerate(m))
#        print(msg)
        s = sum(msg)
        msg = tuple(i/s for i in msg)
        return msg
       
    def _best_var(self, variables, f):
        best = None
        best_val = float('inf')
        neighbors = defaultdict(set)
        for factor in self.factors:
            for v in factor.vars:
                neighbors[v] |= set(factor.vars) - {v}

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
       return reduce(mul, [len(self.card[i]) for i in neighbors[v]], 0)

    def _fill(self, neighbors, v):
        fill = 0
        for n in neighbors[v]:
            fill += len(neighbors[v] - neighbors[n])
        return fill

    def _weighted_fill(self, neighbors, v):
        w_fill = 0
        for n in neighbors[v]:
            fills = neighbors[v] - neighbors[n]
            w_fill += sum(len(self.card[n]) * len(self.card[i])
                          for i in fills)
        return w_fill    


