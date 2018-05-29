
def get_chunks(l, n, max_chunks=None):
    """
    Returns a chunked version of list l with a maximum of n items in each chunk

    :param iterable[T] l: list of items of type T
    :param int n: max size of each chunk
    :param int max_chunks: maximum number of chunks that can be returned. Pass none (the default) for unbounded
    :return: list of chunks
    :rtype: list[T]
    """
    if n is None:
        return [l]

    if n <= 0:
        raise ValueError('get_chunk: n must be a positive value. Received {}'.format(n))

    if max_chunks is not None and max_chunks > 0:
        n = max(max_chunks, int(float(len(l)) / float(n)) + 1)

    return [l[i:i+n] for i in range(0, len(l), n)]

