from pgm.networks import Factor, Network

def create_network(model_file, evidence=None):
    with open(model_file) as f:
        ntype = f.readline().strip()
        variables = [i for i in range(int(f.readline().strip()))]
        cards = [int(i) for i in f.readline().strip().split()]
        network = Network(variables, card=cards, ntype=ntype)
        cliques =[]
        for i in range(int(f.readline())):
            cliques.append([int(i) for i in f.readline().strip().split()][1:])
        vals = []
        F=[]
        for clique in cliques:
            line = None
            while not vals:
                vals += [float(i) for i in f.readline().strip().split()]
               
            n = int(vals.pop(0))
            while len(vals) < n:
                vals += [float(i) for i in f.readline().strip().split()]
            network.add_factor(Factor(clique, vals[:n], network))
            vals = vals[n:]
        return network