from typing import List, Dict, Any, Set, Tuple
from lex import Token, TokenType

class GrammarAnalyzer:
    def __init__(self, tokens: List[Token] = None):
        self.tokens = tokens or []
        self.used_terminals = set()
        self.used_non_terminals = set()
        
    def analyze_actual_usage(self):
        if not self.tokens:
            return
            
        for token in self.tokens:
            if token.type in [TokenType.INTEGER, TokenType.FLOATLIT]:
                self.used_terminals.add('number')
            elif token.type == TokenType.STRINGLIT:
                self.used_terminals.add('string')
            elif token.type == TokenType.CHARLIT:
                self.used_terminals.add('char')
            elif token.type == TokenType.IDENT:
                self.used_terminals.add('id')
            elif token.type in [TokenType.PLUS, TokenType.MINUS, TokenType.MULT, TokenType.DIV,
                              TokenType.EQ, TokenType.NEQ, TokenType.LT, TokenType.GT, 
                              TokenType.LTE, TokenType.GTE]:
                self.used_terminals.add(token.value)
            elif token.type == TokenType.LPAREN:
                self.used_terminals.add('(')
            elif token.type == TokenType.RPAREN:
                self.used_terminals.add(')')
    
    def get_dynamic_grammar(self):
        grammar = {
            'Expression': ['Term Expression\''],
            'Expression\'': [],
            'Term': ['Factor Term\''],
            'Term\'': [],
            'Factor': []
        }
        
        has_add_sub = any(t.type in [TokenType.PLUS, TokenType.MINUS] for t in self.tokens)
        has_mul_div = any(t.type in [TokenType.MULT, TokenType.DIV] for t in self.tokens)
        
        if has_add_sub:
            grammar['Expression\''].extend(['+ Term Expression\'', '- Term Expression\''])
        
        if has_mul_div:
            grammar['Term\''].extend(['* Factor Term\'', '/ Factor Term\''])
        
        if grammar['Expression\'']:
            grammar['Expression\''].append('ε')
        else:
            grammar['Expression\''] = ['ε']
            
        if grammar['Term\'']:
            grammar['Term\''].append('ε')
        else:
            grammar['Term\''] = ['ε']
        
        factor_productions = []
        if any(t.type in [TokenType.LPAREN] for t in self.tokens):
            factor_productions.append('( Expression )')
        if any(t.type in [TokenType.INTEGER, TokenType.FLOATLIT] for t in self.tokens):
            factor_productions.append('number')
        if any(t.type in [TokenType.STRINGLIT] for t in self.tokens):
            factor_productions.append('string')
        if any(t.type in [TokenType.CHARLIT] for t in self.tokens):
            factor_productions.append('char')
        if any(t.type in [TokenType.IDENT] for t in self.tokens):
            factor_productions.append('id')
            
        grammar['Factor'] = factor_productions if factor_productions else ['number', 'id']
        
        return grammar, has_add_sub, has_mul_div
    
    def get_dynamic_first_sets(self):
        dynamic_grammar, has_add_sub, has_mul_div = self.get_dynamic_grammar()
        
        first_sets = {
            'Expression': [],
            'Expression\'': [],
            'Term': [],
            'Term\'': [],
            'Factor': []
        }
        
        for prod in dynamic_grammar['Factor']:
            if prod.startswith('('):
                first_sets['Factor'].append('(')
            elif prod in ['number', 'string', 'char', 'id']:
                first_sets['Factor'].append(prod)
        
        first_sets['Factor'] = sorted(list(set(first_sets['Factor'])))
        first_sets['Term'] = first_sets['Factor'].copy()
        first_sets['Expression'] = first_sets['Term'].copy()
        
        for prod in dynamic_grammar['Expression\'']:
            if prod.startswith('+'):
                first_sets['Expression\''].append('+')
            elif prod.startswith('-'):
                first_sets['Expression\''].append('-')
            elif prod == 'ε':
                first_sets['Expression\''].append('ε')
        
        first_sets['Expression\''] = sorted(list(set(first_sets['Expression\''])))
        
        for prod in dynamic_grammar['Term\'']:
            if prod.startswith('*'):
                first_sets['Term\''].append('*')
            elif prod.startswith('/'):
                first_sets['Term\''].append('/')
            elif prod == 'ε':
                first_sets['Term\''].append('ε')
        
        first_sets['Term\''] = sorted(list(set(first_sets['Term\''])))
            
        return first_sets
    
    def get_dynamic_follow_sets(self):
        dynamic_grammar, has_add_sub, has_mul_div = self.get_dynamic_grammar()
        
        follow_sets = {
            'Expression': ['$', ')'],
            'Expression\'': ['$', ')'],
            'Term': [],
            'Term\'': [],
            'Factor': []
        }
        
        term_follow = ['$', ')']
        if has_add_sub:
            term_follow.extend(['+', '-'])
        follow_sets['Term'] = sorted(term_follow)
        follow_sets['Term\''] = follow_sets['Term'].copy()
        
        factor_follow = ['$', ')']
        if has_add_sub:
            factor_follow.extend(['+', '-'])
        if has_mul_div:
            factor_follow.extend(['*', '/'])
        follow_sets['Factor'] = sorted(factor_follow)
        
        return follow_sets
    
    def display_grammar_analysis(self):
        print("\n" + "="*60)
        print("GRAMMAR ANALYSIS: LEFT RECURSION ELIMINATION & FIRST/FOLLOW SETS")
        print("="*60)
        
        self.analyze_actual_usage()
        dynamic_grammar, has_add_sub, has_mul_div = self.get_dynamic_grammar()
        dynamic_first = self.get_dynamic_first_sets()
        dynamic_follow = self.get_dynamic_follow_sets()
        
        original_grammar = {
            'Expression': [],
            'Term': [],
            'Factor': []
        }
        
        if has_add_sub:
            original_grammar['Expression'].extend(['Expression + Term', 'Expression - Term'])
        if has_mul_div:
            original_grammar['Term'].extend(['Term * Factor', 'Term / Factor'])
        
        original_grammar['Expression'].append('Term')
        original_grammar['Term'].append('Factor')
        
        factor_productions = []
        if any(t.type in [TokenType.LPAREN] for t in self.tokens):
            factor_productions.append('( Expression )')
        if any(t.type in [TokenType.INTEGER, TokenType.FLOATLIT] for t in self.tokens):
            factor_productions.append('number')
        if any(t.type in [TokenType.STRINGLIT] for t in self.tokens):
            factor_productions.append('string')
        if any(t.type in [TokenType.CHARLIT] for t in self.tokens):
            factor_productions.append('char')
        if any(t.type in [TokenType.IDENT] for t in self.tokens):
            factor_productions.append('id')
            
        original_grammar['Factor'] = factor_productions if factor_productions else ['number', 'id']
        
        print("\n1. ORIGINAL GRAMMAR (WITH LEFT RECURSION):")
        print("-" * 50)
        for non_terminal, productions in original_grammar.items():
            if productions:
                print(f"{non_terminal:12} → {' | '.join(productions)}")
        
        print("\n2. AFTER LEFT RECURSION ELIMINATION:")
        print("-" * 50)
        for non_terminal, productions in dynamic_grammar.items():
            if productions:
                print(f"{non_terminal:12} → {' | '.join(productions)}")
        
        print("\n3. FIRST SETS (BASED ON ACTUAL CODE):")
        print("-" * 50)
        for non_terminal, first_set in dynamic_first.items():
            if first_set:
                print(f"FIRST({non_terminal:12}) = {{{', '.join(first_set)}}}")
        
        print("\n4. FOLLOW SETS (BASED ON ACTUAL CODE):")
        print("-" * 50)
        for non_terminal, follow_set in dynamic_follow.items():
            if follow_set:
                print(f"FOLLOW({non_terminal:11}) = {{{', '.join(follow_set)}}}")
        
        print("\n5. ACTUAL TERMINALS USED IN SOURCE CODE:")
        print("-" * 50)
        used_terminals = sorted(list(self.used_terminals))
        print(f"Terminals found: {{{', '.join(used_terminals)}}}")
        
        print("\n6. EXPLANATION:")
        print("-" * 50)
        print("• Grammar analysis adapts to actual source code content")
        print("• Only productions/sets relevant to input are shown")
        print("• Left recursion eliminated using standard transformation")
        print("• ε represents empty string")
        print("• Dynamic analysis shows what the parser actually needs")
        print(f"• Detected operators: +-:{has_add_sub} */:{has_mul_div}")