from typing import List
from tac_generator import ThreeAddressCode

class Optimizer:
    def optimize(self, tac_code: List[ThreeAddressCode]) -> List[ThreeAddressCode]:
        optimized = []
        
        for instr in tac_code:
            if instr.op in ('+', '-', '*', '/') and instr.arg1 and instr.arg2:
                if self.is_constant(instr.arg1) and self.is_constant(instr.arg2):
                    try:
                        result = eval(f"{instr.arg1} {instr.op} {instr.arg2}")
                        optimized.append(ThreeAddressCode("=", str(result), None, instr.result))
                        continue
                    except:
                        pass
            optimized.append(instr)
        
        return optimized
    
    def is_constant(self, val: str) -> bool:
        return val.replace('.', '').replace('-', '').isdigit()