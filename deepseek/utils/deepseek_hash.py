import os
import struct
from wasmtime import Engine, Module, Store, Instance

class DeepSeekHash:
    def __init__(self):
        self.offset   = 0
        self.store    = None
        self.memory   = None
        self.instance = None

        self.init(os.path.join(os.path.dirname(__file__), 'sign.wasm'))

    def init(self, wasm_path):
        engine        = Engine()
        self.store    = Store(engine)
        module        = Module.from_file(engine, wasm_path)
        self.instance = Instance(self.store, module, [])
        self.memory   = self.instance.exports(self.store)["memory"]

        return self.instance

    def encode_string(self, text, allocate, reallocate):
        str_len   = len(text)
        ascii_len = 0
        ptr       = allocate(self.store, str_len, 1) & 0xFFFFFFFF

        for i in range(str_len):
            code = ord(text[i])
            if code > 127:
                break

            self.memory.data_ptr(self.store)[ptr + i] = code
            ascii_len += 1

        if ascii_len == str_len:
            self.offset = ascii_len
            return ptr

        remaining = text[ascii_len:].encode('utf-8')
        new_size  = ascii_len + len(remaining)
        ptr       = reallocate(self.store, ptr, str_len, new_size, 1) & 0xFFFFFFFF

        self.memory.data_ptr(self.store)[ptr + ascii_len : ptr + new_size] = remaining
        self.offset = new_size

        return ptr

    def solve_hash(self, challenge, salt, difficulty, expire_at):
        prefix = f"{salt}_{expire_at}_"
        try:
            retptr  = self.instance.exports(self.store)["__wbindgen_add_to_stack_pointer"](self.store, -16) & 0xFFFFFFFF
            alloc   = self.instance.exports(self.store)["__wbindgen_export_0"]
            realloc = self.instance.exports(self.store)["__wbindgen_export_1"]

            ptr0    = self.encode_string(challenge, alloc, realloc)
            len0    = self.offset
            ptr1    = self.encode_string(prefix, alloc, realloc)
            len1    = self.offset

            difficulty_float = float(difficulty)

            self.instance.exports(self.store)["wasm_solve"](
                self.store, retptr, ptr0, len0, ptr1, len1, difficulty_float
            )

            status = struct.unpack('<i', bytes(self.memory.data_ptr(self.store)[retptr:retptr+4]))[0]
            value  = struct.unpack('<d', bytes(self.memory.data_ptr(self.store)[retptr+8:retptr+16]))[0]

            return int(value) if status != 0 else None
        
        finally:
            self.instance.exports(self.store)["__wbindgen_add_to_stack_pointer"](self.store, 16)


