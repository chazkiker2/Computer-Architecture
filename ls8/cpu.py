"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0 for _ in range(256)]
        self.reg = [0 for _ in range(8)]
        self.pc = 0

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010,  # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111,  # PRN R0
            0b00000000,
            0b00000001,  # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """print the CPU state

        A helper function to print out the CPU state. call from run() for debugging
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        # execution sequence
        # 1. instruction pointed to by PC is fetched from RAM, decoded, executed
        # 2. if the instruction does NOT set the PC itself, the PC will advance to subsequent instruction
        # 3. if the CPU is not halted by a HLT instruction, go to step 1
        while True:
            # self.trace()

            # read the address in register `PC` and store that result in our instruction register
            instruction_register = self.ram_read(self.pc)

            # read adjacent bytes in case the instruction requires them
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # Then, depending on the value of the opcode, perform the actions
            # needed for the instruction per the LS-8 spec.
            if instruction_register == 0b00000001:
                print("HALTING")
                exit()
                break
            elif instruction_register == 0b10000010:
                self.reg[operand_a] = operand_b
            elif instruction_register == 0b01000111:
                print(f"{self.reg[operand_a]}")

            # update PC to point to the next instruction
            # number of bytes used by an instruction can be determined from the two high bits (6-7) of opcode
            self.pc += 1

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
