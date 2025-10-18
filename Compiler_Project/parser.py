from typing import List, Optional
from lex import Token, TokenType

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements

class Function(ASTNode):
    def __init__(self, return_type: str, name: str, body: List[ASTNode]):
        self.return_type = return_type
        self.name = name
        self.body = body

class VarDecl(ASTNode):
    def __init__(self, type_: str, name: str, init: Optional[ASTNode] = None):
        self.type = type_
        self.name = name
        self.init = init

class Assignment(ASTNode):
    def __init__(self, name: str, expr: ASTNode):
        self.name = name
        self.expr = expr

class BinaryOp(ASTNode):
    def __init__(self, left: ASTNode, op: str, right: ASTNode):
        self.left = left
        self.op = op
        self.right = right

class Number(ASTNode):
    def __init__(self, value: str, type_: str = 'int'):
        self.value = value
        self.type = type_

class String(ASTNode):
    def __init__(self, value: str):
        self.value = value
        self.type = 'string'

class Char(ASTNode):
    def __init__(self, value: str):
        self.value = value
        self.type = 'char'

class Identifier(ASTNode):
    def __init__(self, name: str):
        self.name = name

class IfStmt(ASTNode):
    def __init__(self, cond: ASTNode, then_body: List[ASTNode], else_body: Optional[List[ASTNode]] = None):
        self.cond = cond
        self.then_body = then_body
        self.else_body = else_body or []

class WhileStmt(ASTNode):
    def __init__(self, cond: ASTNode, body: List[ASTNode]):
        self.cond = cond
        self.body = body

class ReturnStmt(ASTNode):
    def __init__(self, expr: Optional[ASTNode] = None):
        self.expr = expr

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else Token(TokenType.EOF, '', 1, 1)
    
    def eat(self, token_type: TokenType):
        if self.current_token.type == token_type:
            self.advance()
        else:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token.type} at {self.current_token.line}:{self.current_token.col}")
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = Token(TokenType.EOF, '', 1, 1)
    
    def parse(self) -> Program:
        statements = []
        while self.current_token.type != TokenType.EOF:
            if self.is_function_definition():
                statements.append(self.parse_function())
            else:
                statements.append(self.parse_statement())
        return Program(statements)
    
    def is_function_definition(self) -> bool:
        save_pos = self.pos
        try:
            if self.current_token.type not in (TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.CHAR, TokenType.VOID):
                return False
            
            self.advance()
            if self.current_token.type != TokenType.IDENT:
                return False
            
            self.advance()
            if self.current_token.type != TokenType.LPAREN:
                return False
            
            self.advance()
            if self.current_token.type != TokenType.RPAREN:
                return False
            
            self.advance()
            if self.current_token.type != TokenType.LBRACE:
                return False
            
            return True
        finally:
            self.pos = save_pos
            self.current_token = self.tokens[self.pos]
    
    def parse_function(self) -> Function:
        return_type = self.current_token.value
        self.eat(self.current_token.type)
        
        name = self.current_token.value
        self.eat(TokenType.IDENT)
        self.eat(TokenType.LPAREN)
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        
        body = []
        while self.current_token.type != TokenType.RBRACE and self.current_token.type != TokenType.EOF:
            body.append(self.parse_statement())
        self.eat(TokenType.RBRACE)
        
        return Function(return_type, name, body)
    
    def parse_statement(self) -> ASTNode:
        if self.current_token.type in (TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.CHAR):
            return self.parse_var_decl()
        elif self.current_token.type == TokenType.IF:
            return self.parse_if_stmt()
        elif self.current_token.type == TokenType.WHILE:
            return self.parse_while_stmt()
        elif self.current_token.type == TokenType.RETURN:
            return self.parse_return_stmt()
        elif self.current_token.type == TokenType.IDENT:
            return self.parse_assignment()
        else:
            raise SyntaxError(f"Unexpected token {self.current_token.type}")
    
    def parse_var_decl(self) -> VarDecl:
        type_token = self.current_token
        self.eat(type_token.type)
        
        name = self.current_token.value
        self.eat(TokenType.IDENT)
        
        init = None
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            init = self.parse_expression()
        
        self.eat(TokenType.SEMI)
        return VarDecl(type_token.value, name, init)
    
    def parse_assignment(self) -> Assignment:
        name = self.current_token.value
        self.eat(TokenType.IDENT)
        self.eat(TokenType.ASSIGN)
        expr = self.parse_expression()
        self.eat(TokenType.SEMI)
        return Assignment(name, expr)
    
    def parse_if_stmt(self) -> IfStmt:
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        cond = self.parse_expression()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        
        then_body = []
        while self.current_token.type != TokenType.RBRACE and self.current_token.type != TokenType.EOF:
            then_body.append(self.parse_statement())
        self.eat(TokenType.RBRACE)
        
        else_body = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            self.eat(TokenType.LBRACE)
            else_body = []
            while self.current_token.type != TokenType.RBRACE and self.current_token.type != TokenType.EOF:
                else_body.append(self.parse_statement())
            self.eat(TokenType.RBRACE)
        
        return IfStmt(cond, then_body, else_body)
    
    def parse_while_stmt(self) -> WhileStmt:
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        cond = self.parse_expression()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        
        body = []
        while self.current_token.type != TokenType.RBRACE and self.current_token.type != TokenType.EOF:
            body.append(self.parse_statement())
        self.eat(TokenType.RBRACE)
        
        return WhileStmt(cond, body)
    
    def parse_return_stmt(self) -> ReturnStmt:
        self.eat(TokenType.RETURN)
        expr = None
        if self.current_token.type != TokenType.SEMI:
            expr = self.parse_expression()
        self.eat(TokenType.SEMI)
        return ReturnStmt(expr)
    
    def parse_expression(self) -> ASTNode:
        return self.parse_equality()
    
    def parse_equality(self) -> ASTNode:
        node = self.parse_comparison()
        
        while self.current_token.type in (TokenType.EQ, TokenType.NEQ):
            op = self.current_token.value
            self.eat(self.current_token.type)
            node = BinaryOp(node, op, self.parse_comparison())
        
        return node
    
    def parse_comparison(self) -> ASTNode:
        node = self.parse_term()
        
        while self.current_token.type in (TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
            op = self.current_token.value
            self.eat(self.current_token.type)
            node = BinaryOp(node, op, self.parse_term())
        
        return node
    
    def parse_term(self) -> ASTNode:
        node = self.parse_factor()
        
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token.value
            self.eat(self.current_token.type)
            node = BinaryOp(node, op, self.parse_factor())
        
        return node
    
    def parse_factor(self) -> ASTNode:
        node = self.parse_unary()
        
        while self.current_token.type in (TokenType.MULT, TokenType.DIV):
            op = self.current_token.value
            self.eat(self.current_token.type)
            node = BinaryOp(node, op, self.parse_unary())
        
        return node
    
    def parse_unary(self) -> ASTNode:
        if self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token.value
            self.eat(self.current_token.type)
            return BinaryOp(Number('0', 'int'), op, self.parse_unary())
        return self.parse_primary()
    
    def parse_primary(self) -> ASTNode:
        token = self.current_token
        
        if token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return Number(token.value, 'int')
        elif token.type == TokenType.FLOATLIT:
            self.eat(TokenType.FLOATLIT)
            return Number(token.value, 'float')
        elif token.type == TokenType.STRINGLIT:
            self.eat(TokenType.STRINGLIT)
            return String(token.value)
        elif token.type == TokenType.CHARLIT:
            self.eat(TokenType.CHARLIT)
            return Char(token.value)
        elif token.type == TokenType.IDENT:
            self.eat(TokenType.IDENT)
            return Identifier(token.value)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            expr = self.parse_expression()
            self.eat(TokenType.RPAREN)
            return expr
        else:
            raise SyntaxError(f"Unexpected token {token.type}")

def ast_to_string(node: ASTNode, indent: int = 0) -> str:
    pad = "  " * indent
    
    if isinstance(node, Program):
        s = pad + "Program\n"
        for stmt in node.statements:
            s += ast_to_string(stmt, indent + 1)
        return s
    
    elif isinstance(node, Function):
        s = pad + f"Function({node.return_type} {node.name})\n"
        for stmt in node.body:
            s += ast_to_string(stmt, indent + 1)
        return s
    
    elif isinstance(node, VarDecl):
        s = pad + f"VarDecl({node.type} {node.name})\n"
        if node.init:
            s += ast_to_string(node.init, indent + 1)
        return s
    
    elif isinstance(node, Assignment):
        s = pad + f"Assignment({node.name})\n"
        s += ast_to_string(node.expr, indent + 1)
        return s
    
    elif isinstance(node, BinaryOp):
        s = pad + f"BinaryOp({node.op})\n"
        s += ast_to_string(node.left, indent + 1)
        s += ast_to_string(node.right, indent + 1)
        return s
    
    elif isinstance(node, Number):
        return pad + f"Number({node.value}, {node.type})\n"
    
    elif isinstance(node, String):
        return pad + f"String('{node.value}')\n"
    
    elif isinstance(node, Char):
        return pad + f"Char('{node.value}')\n"
    
    elif isinstance(node, Identifier):
        return pad + f"Identifier({node.name})\n"
    
    elif isinstance(node, IfStmt):
        s = pad + "IfStmt\n"
        s += pad + "  Condition:\n"
        s += ast_to_string(node.cond, indent + 2)
        s += pad + "  Then:\n"
        for stmt in node.then_body:
            s += ast_to_string(stmt, indent + 2)
        if node.else_body:
            s += pad + "  Else:\n"
            for stmt in node.else_body:
                s += ast_to_string(stmt, indent + 2)
        return s
    
    elif isinstance(node, WhileStmt):
        s = pad + "WhileStmt\n"
        s += pad + "  Condition:\n"
        s += ast_to_string(node.cond, indent + 2)
        s += pad + "  Body:\n"
        for stmt in node.body:
            s += ast_to_string(stmt, indent + 2)
        return s
    
    elif isinstance(node, ReturnStmt):
        s = pad + "ReturnStmt\n"
        if node.expr:
            s += ast_to_string(node.expr, indent + 1)
        return s
    
    return pad + f"Unknown({type(node)})\n"