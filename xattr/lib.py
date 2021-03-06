import os
import sys

try:
    from ._lib import lib, ffi
except ImportError:
    from .lib_build import ffi, C_SRC
    lib = ffi.verify(C_SRC)

XATTR_NOFOLLOW = lib.XATTR_XATTR_NOFOLLOW
XATTR_CREATE = lib.XATTR_XATTR_CREATE
XATTR_REPLACE = lib.XATTR_XATTR_REPLACE
XATTR_NOSECURITY = lib.XATTR_XATTR_NOSECURITY
XATTR_MAXNAMELEN = lib.XATTR_MAXNAMELEN

XATTR_FINDERINFO_NAME = "com.apple.FinderInfo"
XATTR_RESOURCEFORK_NAME = "com.apple.ResourceFork"

try:
    fs_encode = os.fsencode
except AttributeError:
    def fs_encode(val):
        encoding = sys.getfilesystemencoding()
        if encoding == 'mbcs':
            errors = 'strict'
        else:
            errors = 'surrogateescape'

        if not isinstance(val, bytes):
            return val.encode(encoding, errors)
        else:
            return val


def _check_bytes(val):
    if not isinstance(val, bytes):
        raise TypeError(
            "Value must be bytes, %s was passed." % type(val).__name__
        )


def error(path=None):
    errno = ffi.errno
    strerror = os.strerror(ffi.errno)
    if path:
        raise IOError(errno, strerror, path)
    else:
        raise IOError(errno, strerror)


def _getxattr(path, name, size=0, position=0, options=0):
    """
    getxattr(path, name, size=0, position=0, options=0) -> str
    """
    path = fs_encode(path)
    name = fs_encode(name)
    if size == 0:
        res = lib.xattr_getxattr(path, name, ffi.NULL, 0, position, options)
        if res == -1:
            raise error(path)
        size = res
    buf = ffi.new("char[]", size)
    res = lib.xattr_getxattr(path, name, buf, size, position, options)
    if res == -1:
        raise error(path)
    return ffi.buffer(buf)[:res]


def _fgetxattr(fd, name, size=0, position=0, options=0):
    """
    fgetxattr(fd, name, size=0, position=0, options=0) -> str
    """
    name = fs_encode(name)
    if size == 0:
        res = lib.xattr_fgetxattr(fd, name, ffi.NULL, 0, position, options)
        if res == -1:
            raise error()
        size = res
    buf = ffi.new("char[]", size)
    res = lib.xattr_fgetxattr(fd, name, buf, size, position, options)
    if res == -1:
        raise error()
    return ffi.buffer(buf)[:res]


def _setxattr(path, name, value, position=0, options=0):
    """
    setxattr(path, name, value, position=0, options=0) -> None
    """
    _check_bytes(value)
    path = fs_encode(path)
    name = fs_encode(name)
    res = lib.xattr_setxattr(path, name, value, len(value), position, options)
    if res:
        raise error(path)


def _fsetxattr(fd, name, value, position=0, options=0):
    """
    fsetxattr(fd, name, value, position=0, options=0) -> None
    """
    _check_bytes(value)
    name = fs_encode(name)
    res = lib.xattr_fsetxattr(fd, name, value, len(value), position, options)
    if res:
        raise error()


def _removexattr(path, name, options=0):
    """
    removexattr(path, name, options=0) -> None
    """
    path = fs_encode(path)
    name = fs_encode(name)
    res = lib.xattr_removexattr(path, name, options)
    if res:
        raise error(path)


def _fremovexattr(fd, name, options=0):
    """
    fremovexattr(fd, name, options=0) -> None
    """
    name = fs_encode(name)
    res = lib.xattr_fremovexattr(fd, name, options)
    if res:
        raise error()


def _listxattr(path, options=0):
    """
    listxattr(path, options=0) -> str
    """
    path = fs_encode(path)
    res = lib.xattr_listxattr(path, ffi.NULL, 0, options)
    if res == -1:
        raise error(path)
    elif res == 0:
        return b""
    buf = ffi.new("char[]", res)
    res = lib.xattr_listxattr(path, buf, res, options)
    if res == -1:
        raise error(path)
    return ffi.buffer(buf)[:res]


def _flistxattr(fd, options=0):
    """
    flistxattr(fd, options=0) -> str
    """
    res = lib.xattr_flistxattr(fd, ffi.NULL, 0, options)
    if res == -1:
        raise error()
    buf = ffi.new("char[]", res)
    res = lib.xattr_flistxattr(fd, buf, res, options)
    if res == -1:
        raise error()
    return ffi.buffer(buf)[:res]
