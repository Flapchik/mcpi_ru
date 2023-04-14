try:
    import collections.abc as collections
except ImportError:
    import collections as collections


def flatten(l_arg):
    for e in l_arg:
        if isinstance(e, collections.Iterable) and not isinstance(e, str):
            for ee in flatten(e):
                yield ee
        else:
            yield e


def flatten_parameters_to_bytestring(l_arg):
    return b",".join(map(_misc_to_bytes, flatten(l_arg)))


def _misc_to_bytes(m):
    """
    Convert an arbitrary object into a string encoded as a UTF-8 series of bytes. 
    See `Connection.send` for more details.
    """

    return str(m).encode("UTF-8")
