"""flux-opcodes — Bytecode instruction set for agent runtimes.

Language-agnostic opcode spec. Define, validate, encode, decode.
The instruction set that agents speak natively.
"""
__version__ = "0.1.0"
from .opcodes import Opcode, OperandType, Instruction, InstructionSet
__all__ = ["Opcode", "OperandType", "Instruction", "InstructionSet"]
