from itertools import product


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

    def ComputeJointDistribution(cliques):
	return reduce(lambda x,y:x*y,cliquess)
    
    def ComputeMarginal(V,F):
   """
	V is the variables to be marginalized
	F is a factor list that contains V
   """
	variableList = []
	for factor in F:
		var = factor.var
		variablelist.append(var)
	union_variables = set().union(*variableList)
	v = list(union_variables.difference(V))
	jointE = ComputeJointDistribution(F)
	jointE_normalizedVal = jointE.vals/np.sum(jointE.vals)
	jointE.vals = jointE_normalizedVal
	return FactorMarginalization(jointE,v)

    def SumProductEliminaterVar(z,factorList):
	useFactors = []
	unusedFactors = []
	scope = []
	for fi in factorList:
		if z in fi.var:
			useFactors.append(fi)
			scope = list(set.union(set(scope),fi.var)
		else:
			unusedFactors.append(fi)
	psiFactor = ComputeJointDistribution(useFactors)
	tauFactor = FactorMarginalization(psiFactor,[z])
	return unusedFactors+[tauFactor]i

    def SumProductVE(self,Z,F):
	for z in Z:
		F = SumProductEliminaterVar(z,F)
	return reduce(lambda x,y:x*y,F)
 
