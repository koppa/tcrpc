"""
Types for explicit TwinCAT ST mapping.
Variables can be annotated with these types so the generator knows which exact TwinCAT type to use.
"""

import ctypes

import pyads


class REAL(float):
    pass


class SINT(int):
    pass


class INT(int):
    pass


class DINT(int):
    pass


class LINT(int):
    pass


class USINT(int):
    pass


class UINT(int):
    pass


class UDINT(int):
    pass


class ULINT(int):
    pass


class BYTE(int):
    pass


class WORD(int):
    pass


class DWORD(int):
    pass


class LWORD(int):
    pass


# Mapping from Python types to TwinCAT types
TYPE_MAPPING = {
    int: ("DINT", pyads.PLCTYPE_DINT),
    float: ("LREAL", pyads.PLCTYPE_LREAL),
    bool: ("BOOL", pyads.PLCTYPE_BOOL),
    str: ("STRING(255)", pyads.PLCTYPE_STRING),
    REAL: ("REAL", pyads.PLCTYPE_REAL),
    SINT: ("SINT", pyads.PLCTYPE_SINT),
    INT: ("INT", pyads.PLCTYPE_INT),
    DINT: ("DINT", pyads.PLCTYPE_DINT),
    LINT: ("LINT", pyads.PLCTYPE_LINT),
    USINT: ("USINT", pyads.PLCTYPE_USINT),
    UINT: ("UINT", pyads.PLCTYPE_UINT),
    UDINT: ("UDINT", pyads.PLCTYPE_UDINT),
    ULINT: ("ULINT", pyads.PLCTYPE_ULINT),
    BYTE: ("BYTE", pyads.PLCTYPE_BYTE),
    WORD: ("WORD", pyads.PLCTYPE_WORD),
    DWORD: ("DWORD", pyads.PLCTYPE_DWORD),
    LWORD: ("LWORD", pyads.PLCTYPE_LWORD),
    ctypes.c_bool: ("BOOL", pyads.PLCTYPE_BOOL),
    ctypes.c_byte: ("SINT", pyads.PLCTYPE_SINT),
    ctypes.c_ubyte: ("BYTE", pyads.PLCTYPE_BYTE),
    ctypes.c_short: ("INT", pyads.PLCTYPE_INT),
    ctypes.c_ushort: ("UINT", pyads.PLCTYPE_UINT),
    ctypes.c_int: ("DINT", pyads.PLCTYPE_DINT),
    ctypes.c_uint: ("UDINT", pyads.PLCTYPE_UDINT),
    ctypes.c_long: ("LINT", pyads.PLCTYPE_LINT),
    ctypes.c_ulong: ("ULINT", pyads.PLCTYPE_ULINT),
    ctypes.c_float: ("REAL", pyads.PLCTYPE_REAL),
    ctypes.c_double: ("LREAL", pyads.PLCTYPE_LREAL),
    ctypes.c_char: ("STRING(255)", pyads.PLCTYPE_STRING),
}
