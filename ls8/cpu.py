"""CPU functionality."""
__author__ = "Chaz Kiker"

from alu import Alu, AluOperations
from utils import BColors

DEFAULT_PROGRAM = [
    # From print8.ls8
    0b10000010,  # LDI R0,8
    0b00000000,
    0b00001000,
    0b01000111,  # PRN R0
    0b00000000,
    0b00000001,  # HLT
]

OP_A = "op_a"
OP_B = "op_b"

NOP = 0b00000000
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
# IN PROGRESS
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
# TODO: IMPLEMENT THE FOLLOWING INSTRUCTIONS
INT = 0b01010010
IRET = 0b00010011
JGE = 0b01011010
JGT = 0b01010111
JLE = 0b01011001
JLT = 0b01011000
LD = 0b10000011
ST = 0b10000100

inverse_table = {
 0b00000000: "NOP",
 0b00000001: "HLT",
 0b10000010: "LDI",
 0b01000111: "PRN",
 0b01000101: "PUSH",
 0b01000110: "POP",
 0b01010000: "CALL",
 0b00010001: "RET",
 0b10000100: "ST",
 0b01010100: "JMP",
 0b01010010: "INT",
 0b00010011: "IRET",
 0b01010101: "JEQ",
 0b01011010: "JGE",
 0b01010111: "JGT",
 0b01011001: "JLE",
 0b01011000: "JLT",
 0b01010110: "JNE",
 0b10000011: "LD",
 0b10100000: "ALU_ADD",
 0b10101000: "ALU_AND",
 0b10100111: "ALU_CMP",
 0b01100110: "ALU_DEC",
 0b10100011: "ALU_DIV",
 0b01100101: "ALU_INC",
 0b10100100: "ALU_MOD",
 0b10100010: "ALU_MUL",
 0b01101001: "ALU_NOT",
 0b10101010: "ALU_OR",
 0b10100001: "ALU_SUB",
 0b10101101: "ALU_SHR",
 0b10101100: "ALU_SHL",
 10101011: "ALU_XOR",
}


class BitUtils:
    @staticmethod
    def bits(n):
        """return a generator of only set bits (bits with a value of 1) from the bitset"""
        while n:
            b = n & (~n + 1)
            yield b
            n ^= b

    @staticmethod
    def read_bits(n, k, p):
        """reads k bits from number n starting at position p (0-indexed)"""
        return ((1 << k) - 1) & (n >> p)

    @staticmethod
    def set(num, n):
        num |= 1 << n
        return num

    @staticmethod
    def clear(num, n):
        """clear the nth bit of num"""
        num &= ~(1 << n)
        return num

    @staticmethod
    def toggle(num, n):
        num ^= 1 << n
        return num

    @staticmethod
    def read(num, n):
        return (num >> n) & 1

    @staticmethod
    def set_to(num, n, x):
        num ^= (-x ^ num) & (1 << n)
        return num


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # arithmetic & logic unit
        self.alu = Alu()
        # Random Access Memory (256 bytes)
        self.ram = [0 for _ in range(256)]
        # 8 general-purpose 8-bit numeric registers R0-R7.
        self.reg = [0 for _ in range(8)]
        # R7 is reserved as the stack pointer (SP)
        self.sp = self.reg[7] = 0xF4
        # FL: flags -- 00000LGE
        self.fl = 0b00000000
        # TODO: # R5 is reserved as the interrupt mask (IM)
        # self.irr_m = self.reg[5] = 0
        # TODO: # R6 is reserved as the interrupt status (IS)
        # self.irr_s = self.reg[6] = 0
        # program count
        self.pc = 0

        # branch table for handling various instructions
        self.branch_table = {
            HLT: self.handle_hlt,
            LDI: self.handle_ldi,
            PRN: self.handle_prn,
            POP: self.handle_pop,
            PUSH: self.handle_push,
            CALL: self.handle_call,
            RET: self.handle_ret,
            AluOperations.CMP: self.handle_cmp,
            NOP: lambda: "pass",
            JEQ: self.handle_jeq,
            JGE: self.handle_jge,
            JNE: self.handle_jne,
            JMP: self.handle_jmp,
        }

    @property
    def fl_l(self):
        return BitUtils.read(self.fl, 2) != 0

    @property
    def fl_g(self):
        return BitUtils.read(self.fl, 1) != 0

    @property
    def fl_e(self):
        return BitUtils.read(self.fl, 0) != 0

    def load(self, seed_file):
        """Load a program into memory."""
        try:
            file_path = f"ls8/{seed_file}"
            with open(file_path) as file:
                print(
                    f"{BColors.BOLD}{BColors.OK_GREEN}"
                    f"Loading program from {BColors.UNDERLINE}{BColors.OK_CYAN}{file_path}{BColors.END_}"
                )
                # split the line and cast the first entry into a base 2 int
                # for each line in file if the line doesn't start with a comment
                program = [
                    int(line.split()[0], 2)
                    for line in file.readlines()
                    if line != "" and line[0] != "#" and line.split()
                ]

        except IOError:
            print(
                f"{BColors.FAIL}"
                f"An error occurred! Defaulting to 'print8.ls8'"
                f"{BColors.END_}"
            )
            program = DEFAULT_PROGRAM

        for address, instruction in enumerate(program):
            self.ram[address] = instruction

    def trace(self):
        """print the CPU state

        A helper function to print out the CPU state. call from CPU::run() for debugging
        """

        ir, op_a, op_b = self.ram_read(self.pc)
        trace_key = inverse_table[self.pc] if self.pc in inverse_table \
            else inverse_table[ir] if ir in inverse_table \
            else f"ir=({bin(ir)}, {ir}) & pc=({bin(self.pc)}, {self.pc})"
        BOLD, OK_BLUE, END_ = BColors.BOLD, BColors.OK_BLUE, BColors.END_

        alt_message = f"{BOLD}{OK_BLUE}TRACE: {trace_key} {END_} | {'%02X %02X %02X' % (ir, op_a, op_b)} | "

        # print(f"{BColors.BOLD}{BColors.OK_BLUE}TRACE: %02X {BColors.END_}| %02X %02X %02X |{BColors.OK_CYAN}" % (
        #     self.pc,
        #     ir,
        #     op_a,
        #     op_b
        # ), end='')

        print(alt_message, end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print(f"{BColors.END_}")

    def run(self):
        """Run the CPU."""

        # this loop will be killed with .exit() in CPU::handle_hlt() method
        while True:
            # uncomment the call to self.trace() below for debugging
            # self.trace()

            # read the address in PC register and store that result in our "instruction_byte register"
            # additionally, read adjacent bytes in case the instruction_byte requires them
            ir, op_a, op_b = self.ram_read(self.pc)
            # break the instruction (AABCDDDD) down into relevant bits
            # AA       B         C       DDDD
            num_ops, is_alu, is_pc_set, instruct_id = self.destructure_byte(ir)

            kwargs = {}
            if num_ops >= 1:
                kwargs[OP_A] = op_a
            if num_ops == 2:
                kwargs[OP_B] = op_b

            # check to see if the instruction is an ALU operation
            if is_alu:
                # if so, handle it with the ALU handler class
                self.alu(ir, op_a, op_b)
            if ir in self.branch_table:
                # otherwise, handle it according to its unique handler
                self.branch_table[ir](**kwargs)

            # check if operation manipulates self.pc directly
            if not is_pc_set:
                # if not, then increase the program count accordingly
                # PC will increase by 1 at minimum, and 1 additional for each operand consumed
                self.pc += 1 + num_ops

    def ram_read(self, mar):
        """read data from memory

        :param mar: Memory Address Register, the address from which to read data
        :returns: a tuple with the data in the given MAR, as well as the two adjacent bytes
        """
        return tuple(self.ram[mar:mar + 3])

    def ram_write(self, mar, mdr):
        """write data to memory

        :param mar: Memory Address Register, the address that is being written to
        :param mdr: Memory Data Register, the data to write to memory
        """
        self.ram[mar] = mdr

    @staticmethod
    def destructure_byte(instruction_byte):
        """
        extracts each meaningful bit for any given instruction byte

        Meanings of the bits in the first byte of each instruction: `AABCDDDD`
        * `AA` Number of operands for this opcode, 0-2
        * `B` 1 if this is an ALU operation
        * `C` 1 if this instruction sets the PC
        * `DDDD` Instruction identifier
        """
        destructured = {
            "AA": BitUtils.read_bits(n=instruction_byte, k=2, p=6),
            "B": BitUtils.read_bits(n=instruction_byte, k=1, p=5),
            "C": BitUtils.read_bits(n=instruction_byte, k=1, p=4),
            "DDDD": BitUtils.read_bits(n=instruction_byte, k=4, p=0)
        }
        # number of operands for this opcode, 0-2
        num_operands = destructured["AA"]
        # True if this is an ALU operation
        is_alu_operation = destructured["B"] != 0
        # True if this instruction sets the PC
        is_pc_set = destructured["C"] != 0
        # Instruction identifier
        instruction_id = destructured["DDDD"]

        return num_operands, is_alu_operation, is_pc_set, instruction_id

    # --------------------------------------
    # INSTRUCTION HANDLERS
    # --------------------------------------
    def handle_cmp(self, op_a, op_b):
        """carries out the side effect of the CMP operation

        * If they are equal, set the Equal `E` flag to 1, otherwise set it to 0.
        * If registerA is less than registerB, set the Less-than `L` flag to 1,
          otherwise set it to 0.
        * If registerA is greater than registerB, set the Greater-than `G` flag
          to 1, otherwise set it to 0.

        """

        compared = self.alu(AluOperations.CMP, op_a, op_b)

        # FL: flags -- 00000LGE
        li, gi, ei = 2, 1, 0

        # if registers are equal
        if compared == 0:
            # set the E flag to 1
            self.fl = BitUtils.set(self.fl, ei)

        # else, registers are not equal
        else:
            # clear the E flag to 0
            self.fl = BitUtils.clear(self.fl, ei)

            # if regA is greater than regB
            if compared > 0:
                # set the G flag to 1
                self.fl = BitUtils.set(self.fl, gi)
                # clear the L flag to 0
                self.fl = BitUtils.clear(self.fl, li)

            # else, regA is less than regB
            else:
                # clear the G flag to 0
                self.fl = BitUtils.clear(self.fl, gi)
                # set the L flag to 1
                self.fl = BitUtils.set(self.fl, li)

    def handle_jmp(self, op_a):
        register = op_a
        self.pc = self.reg[register]

    def handle_jne(self, op_a):
        if not self.fl_e:
            self.handle_jmp(op_a)
        else:
            self.pc += 2

    def handle_jge(self, op_a):
        if self.fl_e or self.fl_g:
            self.handle_jmp(op_a)
        else:
            self.pc += 2

    def handle_jeq(self, op_a):
        if self.fl_e:
            self.handle_jmp(op_a)
        else:
            self.pc += 2

    def handle_ret(self):
        """return from the subroutine and pick up where we left off execution"""
        # pop the top of stack and store it in our PC
        # this resumes executing where we left off
        self.pc = self.ram[self.sp]
        # increase sp b/c we're popping
        self.sp += 1

    def handle_call(self, op_a):
        """calls a subroutine at the address stored in the register"""

        register = op_a
        # push the address of the instruction_byte directly after CALL onto the stack
        # we will return here when subroutine finishes execution

        # decrease sp b/c we're pushing
        self.sp -= 1
        self.ram[self.sp] = self.pc + 2

        # The PC is set to the address stored in the given register.
        # We jump to that location in RAM and execute the first instruction_byte in the subroutine.
        # The PC can move forward or backwards from its current location.
        self.pc = self.reg[register]

    def handle_pop(self, op_a):
        """POP -- pop the value at the top of the stack into the given register"""
        register = op_a
        self.reg[register] = self.ram[self.sp]
        self.sp += 1

    def handle_push(self, op_a):
        """PUSH -- push the value in the given register onto the stack"""
        register = op_a
        self.sp -= 1
        self.ram[self.sp] = self.reg[register]

    def handle_ldi(self, op_a, op_b):
        """LDI -- set the value of a register to an integer

        LDI register immediate: register = immediate
        """
        register, immediate = op_a, op_b
        self.reg[register] = immediate

    def handle_prn(self, op_a):
        """PRN -- print numeric value in the given register

        Print to the console the decimal integer value that is stored in a given register

        PRN register: prints decimal representation of the value stored in register
        """
        register = op_a
        print(f"{self.reg[register]}")

    @staticmethod
    def handle_hlt():
        """HLT -- Halt the CPU and exit the emulator"""
        print(f"{BColors.BOLD}{BColors.WARNING}HALTING{BColors.END_}")
        exit()
