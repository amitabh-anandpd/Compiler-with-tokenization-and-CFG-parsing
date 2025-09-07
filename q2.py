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
        # keywords (prioritized over identifiers)
        ('KEYWORD', r'\b(if|else|print)\b'),
        # numbers (float before integer)
        ('FLOAT', r'\-?\d+\.\d+'),
        ('INTEGER', r'\-?\d+'),
        # identifiers
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        # symbols & operators
        ('SYMBOL', r'[+\-*/^<>=;]'),
        # then we need line change and spacess
        ('NEWLINE', r'\n'),
        ('SKIP', r'[ \t]+'),
    ]
    
    # more efficient than the provided boilerplate
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
        self.if_count = 0

    def checkGrammar(self):
        if not self.tokens:
            return
        while not self.is_at_end(): # statement -> (statement)(statement)
            self.statement()

    def statement(self):
        if self.match('KEYWORD', 'if'):
            self.if_statement()
        elif self.match('KEYWORD', 'else'):
            raise SyntaxError("SyntaxError: 'else' occurs before 'if'")
        else:
            self.simple_statement()

    def if_statement(self):
        self.condition()
        self.simple_statement()
        if self.match('KEYWORD', 'else'):
            self.simple_statement()

    def simple_statement(self):
        if self.match('KEYWORD', 'else'):
            raise SyntaxError("SyntaxError: Missing condition after 'if' statement")
        while not self.is_at_end() and self.peek().value not in ('if', 'else'):
            self.advance()

    def condition(self):
        self.expression() # First 'x'
        # Check for optional operator and second 'x'
        if self.peek() and self.peek().type == 'SYMBOL' and self.peek().value in ('<', '>', '='):
            self.advance()
            self.expression()

    def expression(self):
        if self.peek() and self.peek().type in ('IDENTIFIER', 'INTEGER', 'FLOAT'):
            self.advance()
        else:
            raise SyntaxError("SyntaxError: Missing condition statement")
            
    def match(self, token_type, token_value=None):
        # consumes the token as well
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
        if not self.is_at_end():
            return self.tokens[self.current_pos]
        return None

    def advance(self):
        if not self.is_at_end():
            self.current_pos += 1
        return self.tokens[self.current_pos - 1]

    def is_at_end(self):
        return self.current_pos >= len(self.tokens)

def main():
    try:
        input_statement = input("Enter a statement: ")
        
        tokens = tokenize(input_statement)
        
        parser = Parser(tokens)
        parser.checkGrammar()
        
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