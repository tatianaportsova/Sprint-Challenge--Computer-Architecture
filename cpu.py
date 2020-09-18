"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = bytearray([0] * 256)  # Memory
        self.reg = bytearray([0] * 7 + [0xF4])  # 8 general registers

        # Internal registers:
        self.pc = 0   # PC: Program Counter, address of the currently executing instruction
        self.ir = 0   # IR: Instruction Register, contains a copy of the currently executing instruction
        self.mar = 0  # Memory Address Register, holds the memory address we're reading or writing
        self.mdr = 0  # MDR: Memory Data Register, holds the value to write or the value just read
        self.fl = [0b00000000]  # Flag

        # Instruction Registry Dictionary:
        self.ir = {0b10100111: self.CMP,
                   0b00000001: self.HLT,
                   0b10000010: self.LDI,
                   0b10100010: self.MUL,
                   0b01000110: self.POP,
                   0b01000111: self.PRN,
                   0b01000101: self.PUSH,
                #    0b01010000: self.CALL,
                #    0b00010001: self.RET,
                   0b01010101: self.JEQ,
                   0b01010100: self.JMP,
                   0b01010110: self.JNE,}


    def ram_read(self, mar):
        return self.ram[mar]  # Accepts the address to read and return the value stored there


    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr  # Accept a value to write, and the address to write it to


    def load(self, file):
        # Load a program into memory
        try:
            with open(file) as f:
                address = 0
                for line in f:
                    removed_comments = line.strip().split("#")  # Split the line if it has comments
                    line_string_value = removed_comments[0].strip()  # Take the 0th element and strip out spaces
                    # If line is blank, skip it
                    if line_string_value == "":
                        continue
                    num = int(line_string_value, 2)  # Convert line to an int value, base 2
                    self.ram[address] = num  # Save it to memory
                    address += 1   # Increment the address counter

                f.close()

        except FileNotFoundError:
            print("--- File Not Found ---")
            sys.exit(2)


    def run(self):
        while True:
            IR = self.ram[self.pc]
            # Get dictionary entry then execute returned instruction
            instruction = self.ir[IR]
            instruction()


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = [0b00000001]
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = [0b00000010]
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = [0b00000100]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
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


    def CMP(self):
        # Get the values from Memory
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        # Hit up the ALU to multiply
        self.alu("CMP", reg_a, reg_b)
        self.pc += 3


    def HLT(self):
        sys.exit(0)  # Stop the program


    def LDI(self):
        address = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[address] = value  # Write it to the registry
        self.pc += 3  # Increment the Program Counter


    def MUL(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("MUL", reg_a, reg_b)  # Hit up the ALU to multiply
        self.pc += 3  # Increment the Program Counter


    def POP(self):
        # Get the value from Memory using the Stack Pointer
        address = self.ram_read(self.pc + 1)
        value = self.ram[self.reg[7]]
        self.reg[address] = value  # Copy it to the given registry
        self.reg[7] += 1  # Increment the Stack Pointer
        self.pc += 2  # Increment the Program Counter


    def PRN(self):
        address = self.ram_read(self.pc + 1)  # Get the address
        print(self.reg[address])  # Print the value
        self.pc += 2  # Increment the Program Counter


    def PUSH(self):
        # Get the value from Register
        address = self.ram_read(self.pc + 1)
        value = self.reg[address]

        self.reg[7] -= 1  # Decrement the Stack Pointer
        self.ram[self.reg[7]] = value  # Copy in the given registry value using the Stack Pointer
        self.pc += 2  # Increment the Program Counter


    # def CALL(self):
    #     address = self.ram_read(self.pc + 1)
    #     value = self.reg[address]
    #     self.PUSH()
    #     self.pc = self.reg[address]


    # def RET(self):
    #     self.pc = self.POP()


    def JEQ(self):
        if self.fl == [0b00000001]:
            self.JMP()
        else:
            self.pc += 2  # Increment the Program Counter


    def JMP(self):
        address = self.ram_read(self.pc + 1)
        self.pc = self.reg[address]


    def JNE(self):
        if self.fl != [0b00000001]:
            self.JMP()
        else:
            self.pc += 2  # Increment the Program Counter