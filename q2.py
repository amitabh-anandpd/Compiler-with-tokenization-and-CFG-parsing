import re
import sys

# tokenization

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token(type='{self.type}', value='{self.value}')"

def tokenize(source_code):
    token_specs = [
        ('INVALID',   r'\d+[a-zA-Z_][a-zA-Z0-9_]*'),
        # -- Keywords (prioritized over identifiers)
        ('KEYWORD', r'\b(if|else|print)\b'),
        # -- Numbers (Float before Integer to handle cases like 2.0)
        ('FLOAT', r'\-?\d+\.\d+'),
        ('INTEGER', r'\-?\d+'),
        # -- Identifiers
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        # -- Symbols / Operators
        ('SYMBOL', r'[+\-*/^<>=;]'),
        # misc
        ('NEWLINE', r'\n'),
        ('SKIP', r'[ \t]+'),
    ]
    
    # Combine all regex patterns into one
    token_regex = '|'.join('(?P<%s>%s)' % spec for spec in token_specs)
    tokens = []
    position = 0
    while position < len(source_code):
        remaining_string = source_code[position:]
        match = re.match(token_regex, remaining_string)
        if not match:
            invalid_char = source_code[position]
            raise ValueError(f"Error: Invalid character '{invalid_char}' at position {position}")
            
        token_type = match.lastgroup
        token_value = match.group(token_type)
        if token_type == 'INVALID':
            raise ValueError(f"ValueError: Invalid identifier: {token_value}\nIdentifier can't start with digits")
        
        if token_type != 'SKIP':
            tokens.append(Token(token_type, token_value))
        
        position = position + match.end()

    return tokens

# syntactic (parsing)

class Parser:
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
        input_statement = input("Enter a statement: ")
        
        tokens = tokenize(input_statement)
        
        parser = Parser(tokens)
        parser.parse()
        
        for token in tokens:
            print(f"Token Type: {token.type}, Token Value: {token.value}")
            
    except ValueError as ve:
        print(str(ve), file=sys.stderr)
        
    except SyntaxError as se:
        print(str(se), file=sys.stderr)
        
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()