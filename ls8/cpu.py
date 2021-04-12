"""CPU functionality."""

from utils import BColors

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000

operations_string = f"""
HLT = {bin(HLT)} = {HLT}
LDI = {bin(LDI)} = {LDI}
PRN = {bin(PRN)} = {PRN}
MUL = {bin(MUL)} = {MUL}
PUSH = {bin(PUSH)} = {PUSH}
POP = {bin(POP)} = {POP}
CALL = {bin(CALL)} = {CALL}
RET = {bin(RET)} = {RET}
ADD = {bin(ADD)} = {ADD}
"""


class AluOperations:
    ADD = "ADD"
    MUL = "MUL"
    XOR = "XOR"


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


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""

        # Random Access Memory (256 bytes)
        self.ram = [0 for _ in range(256)]

        # 8 general-purpose 8-bit numeric registers R0-R7.
        self.reg = [0 for _ in range(8)]

        # TODO: R5 is reserved as the interrupt mask (IM)
        # self.irr_m = self.reg[5] = 0
        # TODO: R6 is reserved as the interrupt status (IS)
        # self.irr_s = self.reg[6] = 0

        # R7 is reserved as the stack pointer (SP)
        self.sp = self.reg[7] = 0xF4
        # program count
        self.pc = 0

        # branch table for handling various instructions
        self.branch_table = {
            HLT: self.handle_hlt,
            LDI: self.handle_ldi,
            PRN: self.handle_prn,
            MUL: self.handle_mul,
            POP: self.handle_pop,
            PUSH: self.handle_push,
            CALL: self.handle_call,
            RET: self.handle_ret,
            ADD: self.handle_add,
        }

    def load(self, seed_file):
        """Load a program into memory."""
        try:
            file_path = f"ls8/{seed_file}"
            with open(file_path) as file:
                print(
                    f"{BColors.BOLD}{BColors.OK_GREEN}"
                    f"Loading program from {BColors.UNDERLINE}{BColors.OK_CYAN}{file_path}{BColors.END_}"
                )
                program = [int(line.split()[0], 2) for line in file.readlines() if line[0] != "#"]
        except IOError:
            print(
                f"{BColors.FAIL}"
                f"An error occurred! Defaulting to 'print8.ls8'"
                f"{BColors.END_}"
            )
            program = DEFAULT_PROGRAM

        for address, instruction in enumerate(program):
            self.ram[address] = instruction

    def alu(self, op, reg_a, reg_b):
        """ALU operations. Arithmetic and Logic Unit"""

        if op == AluOperations.ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == AluOperations.MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception(f"{BColors.FAIL}Unsupported ALU operation{BColors.END_}")

    def trace(self):
        """print the CPU state

        A helper function to print out the CPU state. call from CPU::run() for debugging
        """
        ir, op_a, op_b = self.ram_read(self.pc)

        print(f"{BColors.BOLD}{BColors.OK_BLUE}TRACE: %02X {BColors.END_}| %02X %02X %02X |{BColors.OK_CYAN}" % (
            self.pc,
            ir,
            op_a,
            op_b
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print(f"{BColors.END_}")

    def run(self):
        """Run the CPU."""

        # this loop will be killed with .exit() in CPU::handle_hlt() method
        while True:
            # uncomment the call to self.trace() below for debugging
            # self.trace()

            # read the address in PC register and store that result in our "instruction register"
            # additionally, read adjacent bytes in case the instruction requires them
            ir, op_a, op_b = self.ram_read(self.pc)
            # handle the instruction according to its spec
            # returns the number of additional bytes consumed or `None` if the operation manipulates self.pc directly
            out = self.branch_table[ir](op_a=op_a, op_b=op_b)
            # check if operation manipulated self.pc directly... if `out` is not None,
            # then we'll increment `self.pc` accordingly
            if out:
                # update PC to point to the next instruction
                # PC will increase by 1 at minimum, and 1 additional for each additional byte (op_a and op_b)
                # the instruction consumes... so at least 1, at most 3
                self.pc += 1 + out

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
    def bits(n):
        """return a generator of only set bits (bits with a value of 1) from the bitset"""
        while n:
            b = n & (~n + 1)
            yield b
            n ^= b

    # --------------------------------------
    # INSTRUCTION HANDLERS
    # --------------------------------------
    def handle_ret(self, **_):
        """return from the subroutine and pick up where we left off execution"""
        # pop the top of stack and store it in our PC
        # this resumes executing where we left off
        self.pc = self.ram[self.sp]
        # increase sp b/c we're popping
        self.sp += 1

    def handle_call(self, **kwargs):
        """calls a subroutine at the address stored in the register"""

        register = kwargs[OP_A]
        # push the address of the instruction directly after CALL onto the stack
        # we will return here when subroutine finishes execution

        # decrease sp b/c we're pushing
        self.sp -= 1
        self.ram[self.sp] = self.pc + 2

        # The PC is set to the address stored in the given register.
        # We jump to that location in RAM and execute the first instruction in the subroutine.
        # The PC can move forward or backwards from its current location.
        self.pc = self.reg[register]

    def handle_pop(self, **kwargs):
        """POP -- pop the value at the top of the stack into the given register"""
        op_a = kwargs[OP_A]
        self.reg[op_a] = self.ram[self.sp]
        self.sp += 1
        return 1

    def handle_push(self, **kwargs):
        """PUSH -- push the value in the given register onto the stack"""
        register = kwargs[OP_A]
        self.sp -= 1
        self.ram[self.sp] = self.reg[register]
        return 1

    def handle_ldi(self, **kwargs):
        """LDI -- set the value of a register to an integer

        LDI register immediate: register = immediate
        """
        register, immediate = kwargs[OP_A], kwargs[OP_B]
        self.reg[register] = immediate
        return 2

    def handle_prn(self, **kwargs):
        """PRN -- print numeric value in the given register

        Print to the console the decimal integer value that is stored in a given register

        PRN register: prints decimal representation of the value stored in register
        """
        register = kwargs[OP_A]
        print(f"{self.reg[register]}")
        return 1

    @staticmethod
    def handle_hlt(**_):
        """HLT -- Halt the CPU (and exit the emulator)"""
        print(f"{BColors.BOLD}{BColors.WARNING}HALTING{BColors.END_}")
        exit()
        return 0

    # --------------------------------------
    # HANDLERS FOR ALU OPERATIONS
    # --------------------------------------
    def handle_mul(self, **kwargs):
        """MUL -- multiply the values in two registers together and store the result in registerA

        this instruction is handled by the ALU
        MUL registerA registerB: registerA = registerA * registerB
        """

        register_a, register_b = kwargs[OP_A], kwargs[OP_B]
        self.alu(AluOperations.MUL, register_a, register_b)
        return 2

    def handle_add(self, **kwargs):
        """ADD -- add the value in two registers and store the result in registerA

        this instruction is handled by the ALU
        ADD registerA registerB: registerA = registerA + registerB
        """
        register_a, register_b = kwargs[OP_A], kwargs[OP_B]
        self.alu(AluOperations.ADD, register_a, register_b)
        return 2
