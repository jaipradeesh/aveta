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

def load_mapping(infile, informat="pickle"):
    if informat == "pickle":
        with open(infile) as fp:
            mapping = pkl.load(fp)
        return mapping
    if informat == "hdf5":
        import h5py
        import numpy as np
        with h5py.File(infile, "r") as hf:
            mapping = {key: np.array(hf[key])
                       for key in ("frames", "commands", "speeds", "frame_size")}
        return mapping
    raise ValueError("Cannot handle input format {}.".format(informat))

def write_mapping(mapping, outfile, outformat="pickle"):
    if outformat == "pickle":
        with open(outfile, "wb") as out:
            pkl.dump(mapping, out)
    elif outformat == "hdf5":
        import h5py
        with h5py.File(outfile, "w") as hf:
            for key in ("frames", "commands", "speeds", "frame_size"):
                hf.create_dataset(key, data=mapping[key])
    else:
        raise ValueError("Cannot handle output format {}.".format(outformat))

