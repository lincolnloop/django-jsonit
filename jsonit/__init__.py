VERSION = (1, 0, 'alpha', 3)


def get_version(major=None):
    """
    Return the current version as a string.

    :param major: Build the major version, consisting of a maximum of this
        many integer parts. For example, ``get_version(major=2)`` for a version
        of ``(1, 0, 4)`` will return ``'1.0'``.
    """
    version = [str(VERSION[0])]
    number = True
    for i, bit in enumerate(VERSION[1:]):
        if major and i >= major:
            break
        if not isinstance(bit, int):
            if major:
                break
            number = False
        version.append(number and '.' or '-')
        version.append(str(bit))
    return ''.join(version)
