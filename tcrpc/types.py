"""
Types for explicit TwinCAT ST mapping.
Variables can be annotated with these types so the generator knows which exact TwinCAT type to use.
"""

class REAL(float): pass

class SINT(int): pass
class INT(int): pass
class DINT(int): pass
class LINT(int): pass

class USINT(int): pass
class UINT(int): pass
class UDINT(int): pass
class ULINT(int): pass

class BYTE(int): pass
class WORD(int): pass
class DWORD(int): pass
class LWORD(int): pass

# Note: Python's built-in int is mapped to DINT by default.
# Python's built-in float is mapped to LREAL by default.
