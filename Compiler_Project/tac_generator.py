from typing import List, Optional
from dataclasses import dataclass
from parser import ASTNode, Program, Function, VarDecl, Assignment, BinaryOp, Number, String, Char, Identifier, IfStmt, WhileStmt, ReturnStmt
from semantic import SymbolTable

@dataclass
class ThreeAddressCode:
    op: str
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    result: Optional[str] = None
    
    def __str__(self):
        if self.op in ("LABEL", "GOTO", "IF_FALSE"):
            return f"{self.op} {self.result}"
        if self.arg2 is not None:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        if self.arg1 is not None:
            return f"{self.result} = {self.arg1}" if self.op == "=" else f"{self.result} = {self.op} {self.arg1}"
        return f"{self.result} = {self.op}"

class TACGenerator:
    def __init__(self):
        self.tac_code: List[ThreeAddressCode] = []
        self.temp_counter = 0
        self.label_counter = 0
        self.symbol_table = SymbolTable()
        self.in_function = False
        self.current_function = None
        self.string_counter = 0
    
    def generate(self, node: ASTNode) -> List[ThreeAddressCode]:
        self.visit(node)
        return self.tac_code
    
    def new_temp(self) -> str:
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
    
    def new_label(self) -> str:
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def new_string_label(self) -> str:
        label = f"str_{self.string_counter}"
        self.string_counter += 1
        return label
    
    def emit(self, op: str, arg1: Optional[str] = None, arg2: Optional[str] = None, result: Optional[str] = None):
        self.tac_code.append(ThreeAddressCode(op, arg1, arg2, result))
    
    def visit(self, node: ASTNode):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ASTNode):
        raise RuntimeError(f"No TAC visit method for {type(node).__name__}")
    
    def visit_Program(self, node: Program):
        has_functions = any(isinstance(stmt, Function) for stmt in node.statements)
        
        if not has_functions:
            self.emit("LABEL", None, None, "_start")
            for stmt in node.statements:
                self.visit(stmt)
            if not any(isinstance(instr, ThreeAddressCode) and instr.op == "RETURN" for instr in self.tac_code):
                self.emit("=", "0", None, "exit_code")
                self.emit("RETURN", "exit_code", None, None)
        else:
            for stmt in node.statements:
                self.visit(stmt)
    
    def visit_Function(self, node: Function):
        self.symbol_table.declare(node.name, node.return_type, "function")
        self.in_function = True
        self.current_function = node.name
        
        self.symbol_table.enter_scope()
        
        if node.name == "main":
            self.emit("LABEL", None, None, "_start")
        else:
            self.emit("LABEL", None, None, f"func_{node.name}")
        
        for stmt in node.body:
            self.visit(stmt)
        
        if not any(isinstance(instr, ThreeAddressCode) and instr.op == "RETURN" for instr in self.tac_code[-5:]):
            if node.return_type != 'void':
                self.emit("=", "0", None, "default_return")
                self.emit("RETURN", "default_return", None, None)
            else:
                self.emit("RETURN", None, None, None)
        
        self.symbol_table.exit_scope()
        self.in_function = False
        self.current_function = None
        return ""
    
    def visit_VarDecl(self, node: VarDecl):
        self.symbol_table.declare(node.name, node.type, "variable")
        if node.init:
            temp = self.visit(node.init)
            self.emit("=", temp, None, node.name)
        else:
            if node.type == 'int':
                default_value = "0"
            elif node.type == 'float':
                default_value = "0.0"
            elif node.type == 'string':
                default_value = '""'
            elif node.type == 'char':
                default_value = "0"
            else:
                default_value = "0"
            self.emit("=", default_value, None, node.name)
        return ""
    
    def visit_Assignment(self, node: Assignment):
        temp = self.visit(node.expr)
        self.emit("=", temp, None, node.name)
        return ""
    
    def visit_BinaryOp(self, node: BinaryOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        result = self.new_temp()
        
        if node.op == '+' and isinstance(node.left, String) and isinstance(node.right, String):
            self.emit("STRCAT", left, right, result)
        else:
            self.emit(node.op, left, right, result)
        return result
    
    def visit_Number(self, node: Number):
        return node.value
    
    def visit_String(self, node: String):
        string_label = self.new_string_label()
        self.emit("STRING", f'"{node.value}"', None, string_label)
        return string_label
    
    def visit_Char(self, node: Char):
        return str(ord(node.value))
    
    def visit_Identifier(self, node: Identifier):
        return node.name
    
    def visit_IfStmt(self, node: IfStmt):
        else_label = self.new_label()
        end_label = self.new_label()
        
        cond_temp = self.visit(node.cond)
        self.emit("IF_FALSE", cond_temp, None, else_label)
        
        self.symbol_table.enter_scope()
        for stmt in node.then_body:
            self.visit(stmt)
        self.symbol_table.exit_scope()
        
        self.emit("GOTO", None, None, end_label)
        
        self.emit("LABEL", None, None, else_label)
        if node.else_body:
            self.symbol_table.enter_scope()
            for stmt in node.else_body:
                self.visit(stmt)
            self.symbol_table.exit_scope()
        
        self.emit("LABEL", None, None, end_label)
        return ""
    
    def visit_WhileStmt(self, node: WhileStmt):
        start_label = self.new_label()
        end_label = self.new_label()
        
        self.emit("LABEL", None, None, start_label)
        cond_temp = self.visit(node.cond)
        self.emit("IF_FALSE", cond_temp, None, end_label)
        
        self.symbol_table.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.symbol_table.exit_scope()
        
        self.emit("GOTO", None, None, start_label)
        self.emit("LABEL", None, None, end_label)
        return ""
    
    def visit_ReturnStmt(self, node: ReturnStmt):
        if node.expr:
            temp = self.visit(node.expr)
            self.emit("RETURN", temp, None, None)
        else:
            self.emit("RETURN", None, None, None)
        return ""