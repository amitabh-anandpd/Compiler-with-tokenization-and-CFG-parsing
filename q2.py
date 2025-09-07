# q2.py
# Implementation for Question 2: Compiler with Tokenization and CFG Parsing

import re
import sys

# PART 1: TOKENIZATION (LEXICAL ANALYSIS)
# =================================================

class Token:
    """A simple class to hold token information."""
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token(type='{self.type}', value='{self.value}')"

def tokenize(source_code):
    """
    Performs lexical analysis on the source code string.
    
    Args:
        source_code (str): The single line of code to be tokenized.
        
    Returns:
        list[Token]: A list of tokens.
        
    Raises:
        ValueError: If an unrecognized pattern (lexical error) is found.
    """
    # Token specification using regular expressions.
    # The order is important to handle the keyword vs. identifier hierarchy.
    # Keywords are matched before general identifiers.
    token_specs = [
        # -- Keywords (prioritized over identifiers)
        ('KEYWORD', r'\b(if|else|print)\b'),
        # -- Numbers (Float before Integer to handle cases like 2.0)
        ('FLOAT', r'\-?\d+\.\d+'),
        ('INTEGER', r'\-?\d+'),
        # -- Identifiers
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        # -- Symbols / Operators
        ('SYMBOL', r'[+\-*/^<>=;]'),
        # -- Miscellaneous
        ('NEWLINE', r'\n'),
        ('SKIP', r'[ \t]+'),  # To ignore whitespace
    ]
    
    # Combine all regex patterns into one
    token_regex = '|'.join('(?P<%s>%s)' % spec for spec in token_specs)
    
    tokens = []
    position = 0
    while position < len(source_code):
        match = re.match(token_regex, source_code, position)
        
        if not match:
            # If no pattern matches, it's a lexical error
            invalid_char = source_code[position]
            raise ValueError(f"LexicalError: Invalid character '{invalid_char}' at position {position}")
            
        token_type = match.lastgroup
        token_value = match.group(token_type)
        
        if token_type == 'NEWLINE' or token_type == 'SKIP':
            # Ignore whitespace and newlines
            pass
        else:
            tokens.append(Token(token_type, token_value))

        position = match.end()
        
    # Check for identifiers starting with a digit, which regex might miss if not crafted perfectly
    for token in tokens:
        if token.type == 'IDENTIFIER' and token.value[0].isdigit():
            raise ValueError(f"ValueError: Invalid identifier: {token.value}\nIdentifier can't start with digits")

    return tokens

# PART 2: SYNTACTIC ANALYSIS (PARSING)
# =================================================

class Parser:
    """
    Performs syntactic analysis on a list of tokens based on the given CFG.
    This is a simple recursive descent parser.
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_pos = 0

    def parse(self):
        """Starts the parsing process."""
        if not self.tokens:
            return # An empty input is syntactically valid.
        self.statement()
        # After a full statement, we should be at the end of the token list.
        if not self.is_at_end():
            raise SyntaxError(f"SyntaxError: Unexpected token '{self.peek().value}' after a complete statement.")

    def statement(self):
        """Parses a statement rule: S -> if... | y"""
        if self.match('KEYWORD', 'if'):
            self.if_statement()
        elif self.match('KEYWORD', 'else'):
            # This is a specific error case mentioned in the assignment
            raise SyntaxError("SyntaxError: 'else' occurs before 'if'")
        else:
            self.simple_statement()

    def if_statement(self):
        """Parses an if statement: if (A) (statement) [else (statement)]"""
        # The 'if' token is already consumed by self.match()
        self.condition()
        self.statement()
        if self.match('KEYWORD', 'else'):
            self.statement()

    def simple_statement(self):
        """
        Parses a simple statement 'y', which is a sequence of non-structural tokens.
        We consume tokens until we hit a structural keyword or the end.
        """
        while not self.is_at_end() and self.peek().value not in ('if', 'else'):
            self.advance()

    def condition(self):
        """Parses a condition: cond -> x [op x]"""
        self.expression() # First 'x'
        # Check for optional operator and second 'x'
        if self.peek() and self.peek().type == 'SYMBOL' and self.peek().value in ('<', '>', '='):
            self.advance() # Consume operator
            self.expression() # Second 'x'

    def expression(self):
        """Parses an expression 'x', which can be a number, identifier, etc."""
        # This grammar allows a very simple expression: a single terminal.
        if self.peek() and self.peek().type in ('IDENTIFIER', 'INTEGER', 'FLOAT'):
            self.advance()
        else:
            # Handle potential expression chains like '2+xi'
            while self.peek() and self.peek().type in ('IDENTIFIER', 'INTEGER', 'FLOAT', 'SYMBOL'):
                # Avoid consuming operators that delimit a condition
                if self.peek().value in ('<', '>', '='):
                    break
                self.advance()
                if self.is_at_end():
                    break
            
    # --- Helper Methods ---
    def match(self, token_type, token_value=None):
        """
        Checks if the current token matches the expected type and value.
        If it matches, consumes the token and returns True.
        """
        if self.is_at_end():
            return False
        token = self.peek()
        if token.type != token_type:
            return False
        if token_value is not None and token.value != token_value:
            return False
        self.advance()
        return True

    def peek(self):
        """Returns the current token without consuming it."""
        if not self.is_at_end():
            return self.tokens[self.current_pos]
        return None

    def advance(self):
        """Consumes the current token and moves to the next."""
        if not self.is_at_end():
            self.current_pos += 1
        return self.tokens[self.current_pos - 1]

    def is_at_end(self):
        """Checks if we have run out of tokens to parse."""
        return self.current_pos >= len(self.tokens)

# MAIN EXECUTION BLOCK
# =================================================

def main():
    """Main function to run the compiler."""
    try:
        # [cite_start]Get input statement [cite: 165]
        input_statement = input("Enter a statement: ")
        
        # 1. Lexical Analysis
        tokens = tokenize(input_statement)
        
        # 2. Syntactic Analysis
        parser = Parser(tokens)
        parser.parse()
        
        # [cite_start]3. Output on Success [cite: 170]
        print("\n--- No Errors ---")
        for token in tokens:
            print(f"Token Type: {token.type}, Token Value: {token.value}")
            
    except ValueError as ve:
        # [cite_start]Catch Lexical Errors [cite: 174]
        print(f"\n--- Lexical Error ---", file=sys.stderr)
        print(str(ve), file=sys.stderr)
        
    except SyntaxError as se:
        # [cite_start]Catch Syntactic Errors [cite: 178]
        print(f"\n--- Syntactic Error ---", file=sys.stderr)
        print(str(se), file=sys.stderr)
        
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()