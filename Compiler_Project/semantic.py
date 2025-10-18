from typing import List, Optional, Dict
from parser import ASTNode, Program, Function, VarDecl, Assignment, BinaryOp, Number, String, Char, Identifier, IfStmt, WhileStmt, ReturnStmt

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]
        self.current_scope = 0
    
    def enter_scope(self):
        self.scopes.append({})
        self.current_scope += 1
    
    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
            self.current_scope -= 1
    
    def declare(self, name: str, type_: str, kind: str = "var"):
        if name in self.scopes[-1]:
            raise RuntimeError(f"Symbol '{name}' already declared in current scope")
        self.scopes[-1][name] = {'type': type_, 'kind': kind, 'scope': self.current_scope}
    
    def lookup(self, name: str) -> Optional[Dict]:
        for i in range(len(self.scopes) - 1, -1, -1):
            if name in self.scopes[i]:
                return self.scopes[i][name]
        return None
    
    def get_all_symbols(self) -> Dict:
        all_symbols = {}
        for i, scope in enumerate(self.scopes):
            for name, info in scope.items():
                all_symbols[f"{name}@{i}"] = info
        return all_symbols

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.current_function = None
        self.has_main_function = False
    
    def analyze(self, node: ASTNode) -> bool:
        try:
            self.visit(node)
            return len(self.errors) == 0
        except Exception as e:
            self.errors.append(str(e))
            return False
    
    def visit(self, node: ASTNode):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ASTNode):
        raise RuntimeError(f"No visit method for {type(node).__name__}")
    
    def visit_Program(self, node: Program):
        for stmt in node.statements:
            self.visit(stmt)
        
        if not self.has_main_function and any(isinstance(stmt, ReturnStmt) for stmt in node.statements):
            pass
    
    def visit_Function(self, node: Function):
        self.symbol_table.declare(node.name, node.return_type, "function")
        if node.name == "main":
            self.has_main_function = True
        
        self.current_function = node.name
        self.symbol_table.enter_scope()
        
        for stmt in node.body:
            self.visit(stmt)
        
        self.symbol_table.exit_scope()
        self.current_function = None
    
    def visit_VarDecl(self, node: VarDecl):
        self.symbol_table.declare(node.name, node.type, "variable")
        if node.init:
            init_type = self.visit(node.init)
            if init_type and init_type != node.type:
                self.errors.append(f"Type mismatch: cannot assign {init_type} to {node.type} variable '{node.name}'")
    
    def visit_Assignment(self, node: Assignment):
        var_info = self.symbol_table.lookup(node.name)
        if not var_info:
            self.errors.append(f"Undeclared variable '{node.name}'")
            return
        
        expr_type = self.visit(node.expr)
        if expr_type and var_info['type'] != expr_type:
            self.errors.append(f"Type mismatch: cannot assign {expr_type} to {var_info['type']} variable '{node.name}'")
    
    def visit_BinaryOp(self, node: BinaryOp):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        
        if left_type != right_type:
            self.errors.append(f"Type mismatch in binary operation: {left_type} {node.op} {right_type}")
            return left_type or right_type or 'int'
        
        if node.op == '+' and left_type == 'string' and right_type == 'string':
            return 'string'
        
        return left_type
    
    def visit_Number(self, node: Number):
        return node.type
    
    def visit_String(self, node: String):
        return 'string'
    
    def visit_Char(self, node: Char):
        return 'char'
    
    def visit_Identifier(self, node: Identifier):
        var_info = self.symbol_table.lookup(node.name)
        if not var_info:
            self.errors.append(f"Undeclared variable '{node.name}'")
            return 'int'
        return var_info['type']
    
    def visit_IfStmt(self, node: IfStmt):
        cond_type = self.visit(node.cond)
        if cond_type != 'int':
            self.errors.append(f"Condition expression must be integer type, got {cond_type}")
        
        self.symbol_table.enter_scope()
        for stmt in node.then_body:
            self.visit(stmt)
        self.symbol_table.exit_scope()
        
        if node.else_body:
            self.symbol_table.enter_scope()
            for stmt in node.else_body:
                self.visit(stmt)
            self.symbol_table.exit_scope()
    
    def visit_WhileStmt(self, node: WhileStmt):
        cond_type = self.visit(node.cond)
        if cond_type != 'int':
            self.errors.append(f"Condition expression must be integer type, got {cond_type}")
        
        self.symbol_table.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.symbol_table.exit_scope()
    
    def visit_ReturnStmt(self, node: ReturnStmt):
        if not self.current_function:
            if node.expr:
                self.visit(node.expr)
            return
        
        func_info = self.symbol_table.lookup(self.current_function)
        if not func_info:
            return
        
        return_type = func_info['type']
        
        if node.expr:
            expr_type = self.visit(node.expr)
            if expr_type != return_type and return_type != 'void':
                self.errors.append(f"Return type mismatch: function returns {return_type}, got {expr_type}")
        elif return_type != 'void':
            self.errors.append(f"Non-void function '{self.current_function}' must return a value")