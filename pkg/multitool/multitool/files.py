import os
import fnmatch


def match_file(name, include, exclude):
    for pattern in exclude:
        if fnmatch.fnmatch(name, pattern):
            return False

    for pattern in include:
        if fnmatch.fnmatch(name, pattern):
            return True

    return False


def find_files(path, include=['*'], exclude=[], extra=[]):
    """
    Recursively find files in the given path that match an include pattern but
    none of the exclude patterns. Allows extra files to be given that are not
    checked against any patterns.
    """

    files = [os.path.join(path, file) for file in extra]

    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if match_file(filename, include, exclude):
                files.append(os.path.join(root, filename))

    return files
