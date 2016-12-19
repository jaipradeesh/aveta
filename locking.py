# flock based locking
import os
import fcntl

lock_root = "/var/lock/aveta"


def _lock_name(name):
    lockname = os.path.join(lock_root, name)
    return lockname
    

def lock(name, block=False):
    """Given a string, tries to create a lock with that string in the lock root."""
    if not os.path.exists(lock_root):
        os.makedirs(lock_root)
    flag = fcntl.LOCK_EX
    if not block:
        flag |= fcntl.LOCK_NB
    fp = open(_lock_name(name), "wb")
    try:
        fcntl.flock(fp, flag)
        return (fp, name)
    except IOError:
        pass
    return None

def release(lock):
    fp, name = lock
    os.unlink(_lock_name(name))
    try:
        fp.close()
    except IOError:
        pass

