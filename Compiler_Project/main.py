from lex import Lexer
from grammar_analyzer import GrammarAnalyzer
from parser import Parser, ast_to_string
from semantic import SemanticAnalyzer
from tac_generator import TACGenerator
from optimizer import Optimizer
from code_generator import CodeGenerator

class Compiler:
    def __init__(self):
        pass
    
    def compile(self, source: str, source_name: str = "input"):
        print(f"COMPILING: {source_name}")
        print("=" * 60)
        print("SOURCE CODE:")
        print("-" * 30)
        print(source)
        print("-" * 30)
        
        try:
            # Phase 1: Lexical Analysis
            print("\n1. LEXICAL ANALYSIS (SCANNING):")
            print("-" * 50)
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            print(f"Generated {len(tokens)} tokens")
            print("First 10 tokens:")
            for i, token in enumerate(tokens[:10]):
                print(f"  {i:2d}: {token}")
            if len(tokens) > 10:
                print(f"  ... and {len(tokens) - 10} more tokens")
            
            # Grammar Analysis
            grammar_analyzer = GrammarAnalyzer(tokens)
            grammar_analyzer.display_grammar_analysis()
            
            # Phase 2: Syntax Analysis
            print("\n2. SYNTAX ANALYSIS (PARSING):")
            print("-" * 50)
            parser = Parser(tokens)
            ast = parser.parse()
            print("✓ AST generated successfully")
            print("\nGenerated Abstract Syntax Tree:")
            print(ast_to_string(ast))
            
            # Phase 3: Semantic Analysis
            print("\n3. SEMANTIC ANALYSIS:")
            print("-" * 50)
            semantic_analyzer = SemanticAnalyzer()
            semantic_success = semantic_analyzer.analyze(ast)
            
            if semantic_success:
                print("✓ Semantic analysis passed")
                print("✓ Type checking completed")
                print("✓ Symbol table validated")
            else:
                print("✗ Semantic errors found:")
                for error in semantic_analyzer.errors:
                    print(f"  - {error}")
                print("Continuing with compilation despite semantic errors...")
            
            print(f"\nSymbol Table: {semantic_analyzer.symbol_table.get_all_symbols()}")
            
            # Phase 4: Intermediate Code Generation
            print("\n4. INTERMEDIATE CODE GENERATION:")
            print("-" * 50)
            tac_generator = TACGenerator()
            tac_code = tac_generator.generate(ast)
            print(f"Generated {len(tac_code)} Three-Address Code instructions:")
            for i, tac in enumerate(tac_code):
                print(f"  {i:2d}: {tac}")
            
            # Phase 5: Code Optimization
            print("\n5. CODE OPTIMIZATION:")
            print("-" * 50)
            optimizer = Optimizer()
            optimized_tac = optimizer.optimize(tac_code)
            print(f"Optimized to {len(optimized_tac)} TAC instructions:")
            for i, tac in enumerate(optimized_tac):
                print(f"  {i:2d}: {tac}")
            
            # Phase 6: Target Code Generation
            print("\n6. TARGET CODE GENERATION:")
            print("-" * 50)
            code_generator = CodeGenerator()
            assembly = code_generator.generate(optimized_tac, tac_generator.symbol_table)
            
            # Phase 7: Output
            print("\n7. FINAL OUTPUT:")
            print("-" * 50)
            print("Generated Assembly Code:")
            print(assembly)
            
            print("\n" + "=" * 60)
            if semantic_success:
                print("🎉 COMPILATION COMPLETED SUCCESSFULLY!")
            else:
                print("⚠️  COMPILATION COMPLETED WITH WARNINGS!")
            print("=" * 60)
            
            return assembly
            
        except Exception as e:
            print(f"\n❌ COMPILATION FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def main():
    compiler = Compiler()
    
    # Only first 4 test cases
    test_codes = {
        "1": {
            "name": "Function-style code",
            "description": "Complete program with main function, conditionals, and loops",
            "code": """
int main() {
    int a = 8;
    int b = 3;
    int result;
    
    if (a > b) {
        result = (a - b) * 2;
    } else {
        result = (a + b) / 2;
    }
    
    int i = 0;
    while (i < 3) {
        result = result + i;
        i = i + 1;
    }
    
    return result;
}
"""
        },
        "2": {
            "name": "Simple arithmetic",
            "description": "Basic variable declarations and arithmetic operations",
            "code": """
int a = 10;
int b = 5;
int c = 2;
int result = (a + b) * c - a / b;
return result;
"""
        },
        "3": {
            "name": "String operations",
            "description": "String concatenation and manipulation",
            "code": """
string firstName = "John";
string lastName = "Doe";
string fullName = firstName + " " + lastName;
string greeting = "Hello, " + fullName + "!";
return 0;
"""
        },
        "4": {
            "name": "Float calculations",
            "description": "Floating-point arithmetic and mathematical operations",
            "code": """
float pi = 3.14159;
float radius = 7.5;
float diameter = radius * 2.0;
float circumference = 2.0 * pi * radius;
float area = pi * radius * radius;
return area;
"""
        }
    }
    
    while True:
        print("\n" + "="*70)
        print("COMPILER PROJECT - MODULAR STRUCTURE")
        print("="*70)
        print("Available test cases:")
        print("-" * 70)
        
        for key in sorted(test_codes.keys(), key=int):
            test = test_codes[key]
            print(f"{key}. {test['name']:25} - {test['description']}")
        
        print("\n5. Run all test cases")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice in test_codes:
            test = test_codes[choice]
            print(f"\n{'='*80}")
            print(f"TESTING: {test['name']}")
            print(f"DESCRIPTION: {test['description']}")
            print('='*80)
            compiler.compile(test["code"], test["name"])
            input("\nPress Enter to continue...")
        
        elif choice == "5":
            print("RUNNING ALL TEST CASES...")
            print("=" * 70)
            
            for key in sorted(test_codes.keys(), key=int):
                test = test_codes[key]
                print(f"\n{'='*80}")
                print(f"TEST {key}: {test['name']}")
                print(f"DESCRIPTION: {test['description']}")
                print('='*80)
                compiler.compile(test["code"], test["name"])
                
                if key != "4":  # Don't pause after the last test
                    input("\nPress Enter to continue to next test...")
            
            print("\nAll test cases completed!")
            input("Press Enter to return to main menu...")
        
        elif choice == "6":
            print("\nThank you for using the Compiler Project!")
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice! Please select 1-6.")
            input("Press Enter to continue...")

if __name__ == '__main__':
    main()
