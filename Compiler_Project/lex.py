import re
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

class TokenType(Enum):
    INT = 'INT'
    FLOAT = 'FLOAT'
    STRING = 'STRING'
    CHAR = 'CHAR'
    IF = 'IF'
    ELSE = 'ELSE'
    WHILE = 'WHILE'
    RETURN = 'RETURN'
    VOID = 'VOID'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULT = 'MULT'
    DIV = 'DIV'
    ASSIGN = 'ASSIGN'
    EQ = 'EQ'
    NEQ = 'NEQ'
    LT = 'LT'
    GT = 'GT'
    LTE = 'LTE'
    GTE = 'GTE'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACE = 'LBRACE'
    RBRACE = 'RBRACE'
    SEMI = 'SEMI'
    COMMA = 'COMMA'
    QUOTE = 'QUOTE'
    INTEGER = 'INTEGER'
    FLOATLIT = 'FLOATLIT'
    STRINGLIT = 'STRINGLIT'
    CHARLIT = 'CHARLIT'
    IDENT = 'IDENT'
    EOF = 'EOF'

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    col: int
    
    def __repr__(self):
        return f"({self.type.value:8} '{self.value:5}' at {self.line:2}:{self.col:2})"

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []
    
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            
            if ch in ' \t\r':
                self.advance()
                continue
                
            if ch == '\n':
                self.line += 1
                self.col = 1
                self.advance()
                continue
            
            if ch == '/' and self.peek() == '/':
                self.skip_line_comment()
                continue
                
            if ch == '/' and self.peek() == '*':
                self.skip_block_comment()
                continue
            
            if ch == '"':
                self.read_string()
                continue
                
            if ch == "'":
                self.read_char()
                continue
            
            if ch.isalpha() or ch == '_':
                self.read_identifier()
                continue
                
            if ch.isdigit():
                self.read_number()
                continue
                
            token = self.read_operator()
            if token:
                self.tokens.append(token)
                continue
                
            raise SyntaxError(f"Unexpected character '{ch}' at {self.line}:{self.col}")
        
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.col))
        return self.tokens
    
    def advance(self, n=1):
        self.pos += n
        self.col += n
    
    def peek(self, n=1):
        if self.pos + n < len(self.source):
            return self.source[self.pos + n]
        return ''
    
    def skip_line_comment(self):
        while self.pos < len(self.source) and self.source[self.pos] != '\n':
            self.advance()
    
    def skip_block_comment(self):
        self.advance(2)
        while self.pos < len(self.source) - 1:
            if self.source[self.pos] == '*' and self.peek() == '/':
                self.advance(2)
                return
            if self.source[self.pos] == '\n':
                self.line += 1
                self.col = 1
            self.advance()
        raise SyntaxError("Unterminated block comment")
    
    def read_string(self):
        self.advance()
        start = self.pos
        escaped = False
        
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            
            if escaped:
                escaped = False
                self.advance()
                continue
                
            if ch == '\\':
                escaped = True
                self.advance()
                continue
                
            if ch == '"':
                string_lit = self.source[start:self.pos]
                self.tokens.append(Token(TokenType.STRINGLIT, string_lit, self.line, self.col - len(string_lit)))
                self.advance()
                return
                
            if ch == '\n':
                raise SyntaxError("Unterminated string literal")
                
            self.advance()
        
        raise SyntaxError("Unterminated string literal")
    
    def read_char(self):
        self.advance()
        if self.pos >= len(self.source):
            raise SyntaxError("Unterminated character literal")
            
        ch = self.source[self.pos]
        if ch == '\\':
            self.advance()
            if self.pos >= len(self.source):
                raise SyntaxError("Unterminated character literal")
            escape_char = self.source[self.pos]
            if escape_char == 'n':
                ch = '\n'
            elif escape_char == 't':
                ch = '\t'
            elif escape_char == '\\':
                ch = '\\'
            elif escape_char == "'":
                ch = "'"
            else:
                ch = escape_char
        
        self.advance()
        
        if self.pos >= len(self.source) or self.source[self.pos] != "'":
            raise SyntaxError("Unterminated character literal")
            
        self.tokens.append(Token(TokenType.CHARLIT, ch, self.line, self.col - 1))
        self.advance()
    
    def read_identifier(self):
        start = self.pos
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self.advance()
        
        ident = self.source[start:self.pos]
        
        keywords = {
            'int': TokenType.INT,
            'float': TokenType.FLOAT,
            'string': TokenType.STRING,
            'char': TokenType.CHAR,
            'void': TokenType.VOID,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'return': TokenType.RETURN
        }
        
        token_type = keywords.get(ident, TokenType.IDENT)
        self.tokens.append(Token(token_type, ident, self.line, self.col - len(ident)))
    
    def read_number(self):
        start = self.pos
        is_float = False
        
        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            self.advance()
        
        if self.pos < len(self.source) and self.source[self.pos] == '.':
            is_float = True
            self.advance()
            while self.pos < len(self.source) and self.source[self.pos].isdigit():
                self.advance()
        
        number = self.source[start:self.pos]
        token_type = TokenType.FLOATLIT if is_float else TokenType.INTEGER
        self.tokens.append(Token(token_type, number, self.line, self.col - len(number)))
    
    def read_operator(self) -> Optional[Token]:
        ch = self.source[self.pos]
        two_char = self.source[self.pos:self.pos+2]
        
        operators = {
            '==': TokenType.EQ, '!=': TokenType.NEQ,
            '<=': TokenType.LTE, '>=': TokenType.GTE,
            '=': TokenType.ASSIGN, '+': TokenType.PLUS, '-': TokenType.MINUS,
            '*': TokenType.MULT, '/': TokenType.DIV, '<': TokenType.LT, '>': TokenType.GT,
            '(': TokenType.LPAREN, ')': TokenType.RPAREN, '{': TokenType.LBRACE,
            '}': TokenType.RBRACE, ';': TokenType.SEMI, ',': TokenType.COMMA
        }
        
        if two_char in operators:
            token = Token(operators[two_char], two_char, self.line, self.col)
            self.advance(2)
            return token
            
        if ch in operators:
            token = Token(operators[ch], ch, self.line, self.col)
            self.advance()
            return token
            
        return None