command_mapping = {None: 0, "u": 1, "l": 2, "d": 3, "r": 4, "s": 5, "h": 6}


command_rev_mapping = {v: k for k, v in command_mapping.items()}


command_readable_mapping = [
    "NOP",
    "FORWARD",
    "LEFT",
    "DOWN",
    "RIGHT",
    "STRAIGHTEN",
    "HALT"
]

try:
    import cPickle as pkl
except ImportError:
    import pickle as pkl

def load_mapping(infile):
    with open(infile) as fp:
        mapping = pkl.load(fp)
    return mapping

def write_mapping(mapping, outfile):
    with open(outfile, "wb") as out:
        pkl.dump(mapping, out)

