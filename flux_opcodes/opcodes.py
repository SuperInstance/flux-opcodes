"""Flux bytecode opcode definitions and validation."""

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Tuple


class OperandType(Enum):
    NONE = "none"
    REGISTER = "register"
    IMMEDIATE = "immediate"
    ADDRESS = "address"
    LABEL = "label"
    FLOAT = "float"


class Opcode(IntEnum):
    # Control flow
    NOP = 0x00
    HALT = 0x01
    JUMP = 0x10
    JUMP_IF = 0x11
    CALL = 0x12
    RET = 0x13
    
    # Arithmetic
    ADD = 0x20
    SUB = 0x21
    MUL = 0x22
    DIV = 0x23
    MOD = 0x24
    
    # Logic
    AND = 0x30
    OR = 0x31
    XOR = 0x32
    NOT = 0x33
    
    # Memory
    LOAD = 0x40
    STORE = 0x41
    PUSH = 0x42
    POP = 0x43
    
    # Comparison
    CMP_EQ = 0x50
    CMP_LT = 0x51
    CMP_GT = 0x52
    
    # Agent-specific
    EMIT = 0x60    # emit tile
    RECEIVE = 0x61 # receive message
    SLEEP = 0x62   # yield control
    
    # Extended
    SYSCALL = 0xF0
    DEBUG = 0xFE


@dataclass
class Instruction:
    """A single bytecode instruction."""
    opcode: Opcode
    operands: List[int] = field(default_factory=list)
    label: str = ""
    
    def encode(self) -> bytes:
        """Encode to bytes: [opcode, operand_count, operands...]"""
        data = bytes([self.opcode.value, len(self.operands)])
        for op in self.operands:
            data += op.to_bytes(4, 'little', signed=True)
        return data
    
    @classmethod
    def decode(cls, data: bytes) -> Tuple["Instruction", int]:
        """Decode from bytes. Returns (instruction, bytes_consumed)."""
        if len(data) < 2:
            raise ValueError("Need at least 2 bytes")
        opcode = Opcode(data[0])
        operand_count = data[1]
        consumed = 2 + operand_count * 4
        if len(data) < consumed:
            raise ValueError(f"Need {consumed} bytes, got {len(data)}")
        operands = []
        for i in range(operand_count):
            val = int.from_bytes(data[2 + i*4: 6 + i*4], 'little', signed=True)
            operands.append(val)
        return cls(opcode=opcode, operands=operands), consumed
    
    def size(self) -> int:
        return 2 + len(self.operands) * 4


class InstructionSet:
    """Flux bytecode instruction set manager.
    
    Usage:
        isa = InstructionSet()
        isa.define(Opcode.ADD, [OperandType.REGISTER, OperandType.REGISTER])
        isa.validate(Instruction(Opcode.ADD, [1, 2]))  # True
        isa.validate(Instruction(Opcode.ADD, [1]))      # False (wrong operand count)
    """
    
    def __init__(self):
        self.definitions: Dict[Opcode, List[OperandType]] = {}
    
    def define(self, opcode: Opcode, operand_types: List[OperandType]) -> "InstructionSet":
        self.definitions[opcode] = operand_types
        return self
    
    def define_defaults(self) -> "InstructionSet":
        """Load standard flux instruction definitions."""
        defs = {
            Opcode.NOP: [], Opcode.HALT: [],
            Opcode.JUMP: [OperandType.ADDRESS],
            Opcode.JUMP_IF: [OperandType.REGISTER, OperandType.ADDRESS],
            Opcode.CALL: [OperandType.ADDRESS], Opcode.RET: [],
            Opcode.ADD: [OperandType.REGISTER, OperandType.REGISTER],
            Opcode.SUB: [OperandType.REGISTER, OperandType.REGISTER],
            Opcode.MUL: [OperandType.REGISTER, OperandType.REGISTER],
            Opcode.DIV: [OperandType.REGISTER, OperandType.REGISTER],
            Opcode.LOAD: [OperandType.REGISTER, OperandType.ADDRESS],
            Opcode.STORE: [OperandType.REGISTER, OperandType.ADDRESS],
            Opcode.PUSH: [OperandType.REGISTER], Opcode.POP: [OperandType.REGISTER],
            Opcode.CMP_EQ: [OperandType.REGISTER, OperandType.REGISTER],
            Opcode.EMIT: [OperandType.REGISTER],
            Opcode.RECEIVE: [OperandType.REGISTER],
            Opcode.SLEEP: [OperandType.IMMEDIATE],
        }
        self.definitions.update(defs)
        return self
    
    def validate(self, instruction: Instruction) -> bool:
        expected = self.definitions.get(instruction.opcode)
        if expected is None:
            return False
        return len(instruction.operands) == len(expected)
    
    def encode_program(self, instructions: List[Instruction]) -> bytes:
        return b"".join(i.encode() for i in instructions)
    
    def decode_program(self, data: bytes) -> List[Instruction]:
        instructions = []
        pos = 0
        while pos < len(data):
            inst, consumed = Instruction.decode(data[pos:])
            instructions.append(inst)
            pos += consumed
        return instructions
    
    def opcode_names(self) -> Dict[int, str]:
        return {op.value: op.name for op in Opcode}
