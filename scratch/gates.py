# Basic Logic Gates
#   OR
#   AND
#   NOT
# Universal Logic Gates
#   NAND
#   NOR
# Exclusive Logic Gates
#   XOR
#   XNOR

# ----------------------------------------
# EXAMPLE OF USE FOR bits() generator
# bits(109) would go through the following steps
# ----------------------------------------
#    109 is .............. 0110 1101
#    ~109 is -110 which is 1001 0010   NOTE: It's -110 instead of -109 because of 1's compliment
#    ~109+1 is -109....... 1001 0011
#    109 AND ~109 is...... 0000 0001 = 1  <---- 1st value yielded by the generator
#    109 XOR 1 is......... 0110 1100 = n = 108
#
#    108.................. 0110 1100
#    ~108+1= -108......... 1001 0100
#    108 AND -108......... 0000 0100 = 4  <---- 2nd value yielded by the generator
#    108 XOR 4............ 0110 1000 = n = 104
#
#    104.................. 0110 1000
#    ~104+1............... 1001 1000
#    104 AND -104......... 0000 1000 = 8  <---- 3rd value yielded by the generator
#    104 XOR 8............ 0110 0000 = n = 96
#
#    96................... 0110 0000
#    ~96+1................ 1010 0000
#    96 AND -96........... 0010 0000 = 32 <---- 4th value yielded by the generator
#    96 XOR 32............ 0100 0000 = n = 64
#
#    64................... 0100 0000
#    ~64+1................ 1100 0000
#    64 AND -64........... 0100 0000 = 64 <---- 5th value yielded by the generator
#    64 XOR 64............ 0000 0000 = n = 0; thus, the while loop terminates.
#
#
# bitset AND ~bitset returns an integer representing the
# least significant bit of the bitset that is turned on,
# (i.e., 1, then 2, then 4, then 8, etc.)
# src: https://stackoverflow.com/questions/8898807/pythonic-way-to-iterate-over-bits-of-integer
# additional: https://lemire.me/blog/2018/02/21/iterating-over-set-bits-quickly/
def bits(n):
    """generate only set bits (bits having a value of 1)"""
    while n:
        b = n & (~n + 1)
        yield b
        n ^= b


def OR(a, b):
    if (a == 1):
        return 1
    elif (b == 1):
        return 1
    else:
        return 0


def NOR(a, b):
    if (a == 0) and (b == 0):
        return 1
    elif (a == 1) and (b == 1):
        return 0
    elif (a == 1) and (b == 0):
        return 0
    elif (a == 1) and (b == 1):
        return 0


def OR_PY(a, b):
    """(a | b)_i = a_i + b_i - (a_i * b_i)"""
    return a | b


def NOT_PY(a):
    return ~a


def NOR_PY(a, b):
    return NOT_PY(OR_PY(a, b))


if __name__ == '__main__':
    a_, b_ = 0b10011100, 0b110100
    a_or_b_py = OR_PY(a_, b_)
    a_or_b = OR(a_, b_)
    print(f"{a_or_b=}, {a_or_b_py=}")

    x = [bit for bit in bits(27)]

    print(f"{x=}")
    # for b in bits(27):
    #     print(f"{b=}")
