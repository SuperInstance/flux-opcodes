# flux-opcodes

Bytecode instruction set for agent runtimes. Language-agnostic opcode spec: define, validate, encode, decode. The instruction set that agents speak natively.

## Usage

```python
from flux_opcodes import Opcode, Instruction, InstructionSet

isa = InstructionSet().define_defaults()
program = [
    Instruction(Opcode.LOAD, [0, 100]),
    Instruction(Opcode.ADD, [0, 1]),
    Instruction(Opcode.EMIT, [0]),
    Instruction(Opcode.HALT),
]

# Encode to bytes
data = isa.encode_program(program)

# Decode back
decoded = isa.decode_program(data)
```

Includes agent-specific opcodes: EMIT (tile), RECEIVE (message), SLEEP (yield).

Zero deps. `pip install flux-opcodes`
