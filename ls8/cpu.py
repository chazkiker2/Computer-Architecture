"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0 for _ in range(256)]
        self.reg = [0 for _ in range(8)]
        self.pc = 0

    def load(self, seed_file):
        """Load a program into memory."""

        address = 0

        try:
            with open(f"ls8/{seed_file}") as file:
                read_file = file.readlines()
                program = [int(line.split()[0], 2) for line in read_file]
        except IOError:
            print("An error occurred! Defaulting to 'print8.ls8'")
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

        # print(f"{''.join(f'({i}:{v})' for i,v in enumerate(self.ram))}")

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
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

            next_pc_inc = 1

            # Then, depending on the value of the opcode, perform the actions
            # needed for the instruction per the LS-8 spec.
            if instruction_register == 0b00000001:
                # HALT
                print("HALTING")
                exit()
                break
            elif instruction_register == 0b10000010:
                # LDI
                self.reg[operand_a] = operand_b
                next_pc_inc += 2
            elif instruction_register == 0b01000111:
                # PRN
                print(f"{self.reg[operand_a]}")
                next_pc_inc += 1
            elif instruction_register == 0b10100010:
                # MUL
                self.alu("MUL", operand_a, operand_b)
                next_pc_inc += 2

            # update PC to point to the next instruction
            self.pc += next_pc_inc

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
