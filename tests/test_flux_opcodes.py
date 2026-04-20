"""Tests for flux-opcodes."""
import pytest
from flux_opcodes import Opcode, Instruction, InstructionSet


def test_encode_decode_roundtrip():
    inst = Instruction(Opcode.ADD, [1, 2])
    encoded = inst.encode()
    decoded, _ = Instruction.decode(encoded)
    assert decoded.opcode == Opcode.ADD
    assert decoded.operands == [1, 2]


def test_instruction_size():
    inst = Instruction(Opcode.NOP)
    assert inst.size() == 2
    inst2 = Instruction(Opcode.ADD, [1, 2])
    assert inst2.size() == 10


def test_validate_correct():
    isa = InstructionSet().define_defaults()
    assert isa.validate(Instruction(Opcode.ADD, [1, 2]))
    assert isa.validate(Instruction(Opcode.NOP))


def test_validate_wrong_operands():
    isa = InstructionSet().define_defaults()
    assert not isa.validate(Instruction(Opcode.ADD, [1]))  # needs 2


def test_program_encode_decode():
    isa = InstructionSet().define_defaults()
    program = [
        Instruction(Opcode.LOAD, [0, 100]),
        Instruction(Opcode.LOAD, [1, 200]),
        Instruction(Opcode.ADD, [0, 1]),
        Instruction(Opcode.HALT),
    ]
    data = isa.encode_program(program)
    decoded = isa.decode_program(data)
    assert len(decoded) == 4
    assert decoded[0].opcode == Opcode.LOAD
    assert decoded[2].operands == [0, 1]


def test_opcode_names():
    isa = InstructionSet()
    names = isa.opcode_names()
    assert names[0x20] == "ADD"
    assert names[0x01] == "HALT"
