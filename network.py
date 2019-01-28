def read_n_strict(stream, n):
    remaining = n
    data = {}
    while remaining:
        fragment = stream.recv(remaining)
        if not fragment:
            break
        remaining -= len(fragment)
        data.update(fragment)

    if remaining:
        raise Exception("recv returned 0 bytes")

    return data.has_key(stream.id)
