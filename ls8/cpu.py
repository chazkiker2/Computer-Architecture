"""CPU functionality."""

import sys
from utils import BColors

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010

DEFAULT_PROGRAM = [
    # From print8.ls8
    0b10000010,  # LDI R0,8
    0b00000000,
    0b00001000,
    0b01000111,  # PRN R0
    0b00000000,
    0b00000001,  # HLT
]


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""

        self.ram = [0 for _ in range(256)]
        self.reg = [0 for _ in range(8)]
        self.pc = 0
        self.branch_table = {
            HLT: self.handle_hlt,
            LDI: self.handle_ldi,
            PRN: self.handle_prn,
            MUL: self.handle_mul,
        }

    def load(self, seed_file):
        """Load a program into memory."""

        address = 0

        try:
            file_path = f"ls8/{seed_file}"
            with open(file_path) as file:
                print(
                    f"{BColors.BOLD}{BColors.OK_GREEN}"
                    f"Loading program from {BColors.UNDERLINE}{BColors.OK_CYAN}{file_path}{BColors.END_}"
                )
                program = [int(line.split()[0], 2) for line in file.readlines()]
        except IOError:
            print(
                f"{BColors.FAIL}"
                f"An error occurred! Defaulting to 'print8.ls8'"
                f"{BColors.END_}"
            )
            program = DEFAULT_PROGRAM

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception(f"{BColors.FAIL}Unsupported ALU operation{BColors.END_}")

    def trace(self):
        """print the CPU state

        A helper function to print out the CPU state. call from run() for debugging
        """

        print(f"{BColors.BOLD}{BColors.OK_BLUE}TRACE: %02X {BColors.END_}| %02X %02X %02X |{BColors.OK_CYAN}" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print(f"{BColors.END_}")

    # --------------------------------------
    # OP HANDLERS
    # --------------------------------------
    def handle_hlt(self, **kwargs):
        # HALT
        print(f"{BColors.BOLD}{BColors.WARNING}HALTING{BColors.END_}")
        exit()
        return 0

    def handle_ldi(self, **kwargs):
        # LDI
        op_a, op_b = kwargs["op_a"], kwargs["op_b"]
        self.reg[op_a] = op_b
        return 2

    def handle_prn(self, **kwargs):
        # PRN
        op_a = kwargs["op_a"]
        print(f"{self.reg[op_a]}")
        return 1

    def handle_mul(self, **kwargs):
        # MUL
        op_a, op_b = kwargs["op_a"], kwargs["op_b"]
        self.alu("MUL", op_a, op_b)
        return 2

    def run(self):
        """Run the CPU."""
        # execution sequence
        # 1. instruction pointed to by PC is fetched from RAM, decoded, executed
        # 2. if the instruction does NOT set the PC itself, the PC will advance to subsequent instruction
        # 3. if the CPU is not halted by a HLT instruction, go to step 1
        while True:
            self.trace()
            # read the address in register `PC` and store that result in our instruction register
            ir = self.ram_read(self.pc)
            # read adjacent bytes in case the instruction requires them
            op_a = self.ram_read(self.pc + 1)
            op_b = self.ram_read(self.pc + 2)

            # handle the instruction according to the LS-8 spec
            # update PC to point to the next instruction
            self.pc += 1 + self.branch_table[ir](op_a=op_a, op_b=op_b)

    @staticmethod
    def bits(n):
        while n:
            b = n & (~n + 1)
            yield b
            n ^= b

    def ram_read(self, mar):
        """read data from memory

        :param mar: Memory Address Register, the address from which to read data
        """
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        """write data to memory

        :param mar: Memory Address Register, the address that is being written to
        :param mdr: Memory Data Register, the data to write to memory
        """
        self.ram[mar] = mdr
