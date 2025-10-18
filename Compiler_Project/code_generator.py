from typing import List
from tac_generator import ThreeAddressCode
from semantic import SymbolTable

class CodeGenerator:
    def generate(self, tac_code: List[ThreeAddressCode], symbol_table: SymbolTable) -> str:
        asm = ["section .data"]
        
        all_vars = set()
        string_data = []
        symbols = symbol_table.get_all_symbols()
        
        for name, info in symbols.items():
            if info['kind'] == 'var':
                var_name = name.split('@')[0]
                all_vars.add(var_name)
        
        for instr in tac_code:
            if instr.result and instr.result.startswith('t'):
                all_vars.add(instr.result)
            if instr.arg1 and instr.arg1.startswith('t'):
                all_vars.add(instr.arg1)
            if instr.arg2 and instr.arg2.startswith('t'):
                all_vars.add(instr.arg2)
            
            if instr.op == "STRING":
                string_data.append(f'{instr.result} db "{instr.arg1}", 0')
                all_vars.add(instr.result)
        
        for instr in tac_code:
            if instr.arg1 and not instr.arg1.startswith('t') and not self.is_constant(instr.arg1) and instr.arg1 not in ['+', '-', '*', '/'] and not instr.arg1.startswith('"'):
                all_vars.add(instr.arg1)
            if instr.arg2 and not instr.arg2.startswith('t') and not self.is_constant(instr.arg2) and instr.arg2 not in ['+', '-', '*', '/'] and not instr.arg2.startswith('"'):
                all_vars.add(instr.arg2)
            if instr.result and not instr.result.startswith('t') and not self.is_constant(instr.result) and instr.result not in ['+', '-', '*', '/'] and not instr.result.startswith('"'):
                all_vars.add(instr.result)
        
        all_vars = {v for v in all_vars if not v.startswith('L') and not v.startswith('func_') and v != '_start'}
        
        for var in sorted(all_vars):
            if var.startswith('str_'):
                continue
            asm.append(f"    {var} dd 0")
        
        asm.extend(string_data)
        
        asm.extend(["", "section .text", "global _start", "_start:"])
        
        for instr in tac_code:
            if instr.op == "=":
                asm.append(f"    ; {instr.result} = {instr.arg1}")
                if self.is_constant(instr.arg1):
                    asm.append(f"    mov dword [{instr.result}], {instr.arg1}")
                else:
                    asm.append(f"    mov eax, [{instr.arg1}]")
                    asm.append(f"    mov [{instr.result}], eax")
            
            elif instr.op in ('+', '-', '*', '/'):
                asm.append(f"    ; {instr.result} = {instr.arg1} {instr.op} {instr.arg2}")
                asm.append(f"    mov eax, [{instr.arg1}]")
                
                if instr.op == '+':
                    asm.append(f"    add eax, [{instr.arg2}]")
                elif instr.op == '-':
                    asm.append(f"    sub eax, [{instr.arg2}]")
                elif instr.op == '*':
                    asm.append(f"    imul eax, [{instr.arg2}]")
                elif instr.op == '/':
                    asm.append("    cdq")
                    asm.append(f"    idiv dword [{instr.arg2}]")
                
                asm.append(f"    mov [{instr.result}], eax")
            
            elif instr.op == "STRCAT":
                asm.append(f"    ; {instr.result} = strcat({instr.arg1}, {instr.arg2})")
                asm.append(f"    mov dword [{instr.result}], 0")
            
            elif instr.op in ('==', '!=', '<', '>', '<=', '>='):
                asm.append(f"    ; {instr.result} = {instr.arg1} {instr.op} {instr.arg2}")
                asm.append(f"    mov eax, [{instr.arg1}]")
                asm.append(f"    cmp eax, [{instr.arg2}]")
                asm.append("    mov eax, 0")
                
                op_map = {
                    '==': 'sete', '!=': 'setne',
                    '<': 'setl', '>': 'setg',
                    '<=': 'setle', '>=': 'setge'
                }
                asm.append(f"    {op_map[instr.op]} al")
                asm.append("    movzx eax, al")
                asm.append(f"    mov [{instr.result}], eax")
            
            elif instr.op == "IF_FALSE":
                asm.append(f"    ; if false goto {instr.result}")
                asm.append(f"    cmp dword [{instr.arg1}], 0")
                asm.append(f"    je {instr.result}")
            
            elif instr.op == "GOTO":
                asm.append(f"    jmp {instr.result}")
            
            elif instr.op == "LABEL":
                asm.append(f"{instr.result}:")
            
            elif instr.op == "RETURN":
                if instr.arg1:
                    asm.append(f"    mov eax, [{instr.arg1}]")
                asm.extend([
                    "    ; Exit program",
                    "    mov ebx, eax",
                    "    mov eax, 1",
                    "    int 0x80"
                ])
        
        if not any(instr.op == "RETURN" for instr in tac_code):
            asm.extend([
                "    ; Exit program (default)",
                "    mov eax, 1",
                "    mov ebx, 0",
                "    int 0x80"
            ])
        
        return "\n".join(asm)
    
    def is_constant(self, val: str) -> bool:
        return val.replace('.', '').replace('-', '').isdigit()