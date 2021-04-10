# &  -- a & b  -- Bitwise AND
# |  -- a | b  -- Bitwise OR
# ^  -- a ^ b  -- Bitwise XOR
# ~  -- ~a     -- Bitwise NOT
# << -- a << n -- Bitwise left shift
# >> -- a >> n -- Bitwise right shift

# ord(character) will reveal ordinal values on unicode characters
# (42).bit_length() will return the bit-length of any integer
# Use Hoffman coding to find unambiguous bit patterns for every character in a particular text
# len("string".encode("utf-8")) # -> 6

def call(x):
    print(f"call({x=})")
    return x


def NOR(a, b):
    if (a == 0) and (b == 0):
        return 1
    elif (a == 0) and (b == 1):
        return 0
    elif (a == 1) and (b == 0):
        return 0
    elif (a == 1) and (b == 1):
        return 0


if __name__ == '__main__':
    age = 18
    is_self_excluded = True

    comparison_eval = age >= 18 and not is_self_excluded  # False
    bitwise_eval_01 = age >= 18 & ~is_self_excluded  # True
    bitwise_eval_02 = age >= (18 & ~is_self_excluded)  # True
    bitwise_eval_03 = (age >= 18) & ~is_self_excluded  # 0

    print(call(False) or call(True))  # both operands evaluated
    print(call(True) or call(False))  # only left operand evaluated

    print((1 + 1) or "default")  # prints 2
    print((1 - 1) or "default")  # prints "default"

    # Bitwise AND
    #
    #     1 0 0 1 1 1 0 0
    # AND 0 0 1 1 0 1 0 0
    # --------------------
    #     0 0 0 1 0 1 0 0
    #
    # 0b10011100 & 0b00110100 == 0b00010100
    # bin(10011100) & bin(00110100) == bin(00010100)
    x = 0b10011100 & 0b00110100  # x=, bin(x)='0b00010100'
    print(f"{x=}, {bin(x)=}")

    # 11011111 NOR 00010111
    #
    #     1 1 0 1 1 1 1 1
    # NOR 0 0 0 1 0 1 1 1
    # --------------------
    #     0 0 1 0 0 0 0 0    # binary literal
    # ====================
    #     0  0  1   0   0  0  0  0    # binary literal
    #           32  16  8  4  2  1
    #  0b100000     # binary literal
    #  16           # decimal litera
    or_ = (0b11011111 | 0b00010111)
    print(f"{or_=}, {bin(or_)=}")
    a = ~or_ + 2
    print(f"{a=}, {bin(a)=}")

    # 10101010 XOR 11110000
    #     1 0 1 0 1 0 1 0
    # XOR 1 1 1 1 0 0 0 0
    # --------------------
    #     0 1 0 1 1 0 1 0
    #
    # 0b10101010 ^ 0b11110000 => 0b01011010
    #
    # bin to num -> 0b01011010
    #     0    1   0   1   1  0  1  0
    #     128  64  32  16  8  4  2  1
    # 64 + 16 + 8 + 2 => 90
    b = 0b10101010 ^ 0b11110000  # b=90, bin(b)=0b01011010
    print(f"{b=}, {bin(b)=}")

    # 11011 AND 101
    #
    #     1 1 0 1 1
    # AND 0 0 1 0 1
    # ---------------
    #     0 0 0 0 1
    c = 0b11011 & 0b101  # 1
    bin_c = bin(c)  # 0b1

    print(f"{c=}\t{bin_c=}")
