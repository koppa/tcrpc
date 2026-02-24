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


# Note: Python's built-in int is mapped to DINT by default.
# Python's built-in float is mapped to LREAL by default.

# Mapping from Python types to pyads constants
ADS_TYPE_MAPPING = {
    int: pyads.PLCTYPE_DINT,
    float: pyads.PLCTYPE_LREAL,
    bool: pyads.PLCTYPE_BOOL,
    str: pyads.PLCTYPE_STRING,
    REAL: pyads.PLCTYPE_REAL,
    SINT: pyads.PLCTYPE_SINT,
    INT: pyads.PLCTYPE_INT,
    DINT: pyads.PLCTYPE_DINT,
    LINT: pyads.PLCTYPE_LINT,
    USINT: pyads.PLCTYPE_USINT,
    UINT: pyads.PLCTYPE_UINT,
    UDINT: pyads.PLCTYPE_UDINT,
    ULINT: pyads.PLCTYPE_ULINT,
    BYTE: pyads.PLCTYPE_BYTE,
    WORD: pyads.PLCTYPE_WORD,
    DWORD: pyads.PLCTYPE_DWORD,
    LWORD: getattr(pyads, "PLCTYPE_LWORD", pyads.PLCTYPE_ULINT),
}

# Mapping from Python types to TwinCAT types
TYPE_MAPPING = {
    int: "DINT",
    float: "LREAL",
    bool: "BOOL",
    str: "STRING(255)",
    REAL: "REAL",
    SINT: "SINT",
    INT: "INT",
    DINT: "DINT",
    LINT: "LINT",
    USINT: "USINT",
    UINT: "UINT",
    UDINT: "UDINT",
    ULINT: "ULINT",
    BYTE: "BYTE",
    WORD: "WORD",
    DWORD: "DWORD",
    LWORD: "LWORD",
    ctypes.c_bool: "BOOL",
    ctypes.c_byte: "SINT",
    ctypes.c_ubyte: "BYTE",
    ctypes.c_short: "INT",
    ctypes.c_ushort: "UINT",
    ctypes.c_int: "DINT",
    ctypes.c_uint: "UDINT",
    ctypes.c_long: "LINT",
    ctypes.c_ulong: "ULINT",
    ctypes.c_float: "REAL",
    ctypes.c_double: "LREAL",
    ctypes.c_char: "STRING(255)",
}
