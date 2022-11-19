"""Arithmetic & Logic Operations"""
__author__ = "Chaz Kiker"

from utils import BColors


class AluOperations:
    ADD = 0b10100000
    AND = 0b10101000
    CMP = 0b10100111
    DEC = 0b01100110
    DIV = 0b10100011
    INC = 0b01100101
    MOD = 0b10100100
    MUL = 0b10100010
    NOT = 0b01101001
    OR = 0b10101010
    SUB = 0b10100001
    SHR = 0b10101101
    SHL = 0b10101100
    XOR = 10101011


class Alu:
    def __init__(self):
        self.branch_table = {
            AluOperations.ADD: self.add,
            AluOperations.MUL: self.mul,
            AluOperations.XOR: self.xor,
            AluOperations.SUB: self.sub,
            AluOperations.SHR: self.shr,
            AluOperations.SHL: self.shl,
            AluOperations.AND: self.alu_and,
            AluOperations.CMP: self.cmp,
            AluOperations.DEC: self.dec,
            AluOperations.DIV: self.div,
            AluOperations.INC: self.inc,
            AluOperations.OR: self.alu_or,
            AluOperations.NOT: self.alu_not,
            AluOperations.MOD: self.mod,
        }

    def __call__(self, op, reg_a, reg_b, *args, **kwargs):
        if op not in self.branch_table:
            raise Exception(f"{BColors.FAIL}Unsupported ALU operation{BColors.END_}")
        else:
            return self.branch_table[op](reg_a, reg_b)

    @staticmethod
    def add(a, b):
        a += b

    @staticmethod
    def mul(a, b):
        a *= b

    @staticmethod
    def xor(a, b):
        a ^= b

    @staticmethod
    def sub(a, b):
        a -= b

    @staticmethod
    def shr(a, b):
        a >>= b

    @staticmethod
    def shl(a, b):
        a <<= b

    @staticmethod
    def alu_and(a, b):
        a &= b

    @staticmethod
    def cmp(a, b):
        return 0 if a == b else 1 if a > b else -1

    @staticmethod
    def dec(a, _):
        a -= 1

    @staticmethod
    def div(a, b):
        if b == 0:
            print(f"{BColors.WARNING}{BColors.BOLD}CANNOT DIVIDE BY ZERO{BColors.END_}")
            exit()
        a /= b

    @staticmethod
    def inc(a, _):
        a += 1

    @staticmethod
    def mod(a, b):
        if b == 0:
            print(f"{BColors.WARNING}{BColors.BOLD}CANNOT DIVIDE BY ZERO{BColors.END_}")
            exit()
        a %= b

    @staticmethod
    def alu_not(a, _):
        a = ~a

    @staticmethod
    def alu_or(a, b):
        a |= b
