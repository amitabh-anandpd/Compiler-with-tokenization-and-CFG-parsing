##################### BOILERPLATE BEGINS ############################

# Token types enumeration
##################### YOU CAN CHANGE THE ENUMERATION IF YOU WANT #######################
class TokenType:
    IDENTIFIER = "IDENTIFIER"
    KEYWORD = "KEYWORD"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    SYMBOL = "SYMBOL"

# Token hierarchy dictionary
token_hierarchy = {
    "if": TokenType.KEYWORD,
    "else": TokenType.KEYWORD,
    "print": TokenType.KEYWORD
}


# helper function to check if it is a valid identifier
def is_valid_identifier(lexeme):
    if not lexeme:
        return False

    # Check if the first character is an underscore or a letter
    if not (lexeme[0].isalpha() or lexeme[0] == '_'):
        return False

    # Check the rest of the characters (can be letters, digits, or underscores)
    for char in lexeme[1:]:
        if not (char.isalnum() or char == '_'):
            return False

    return True


# Tokenizer function
def tokenize(source_code):
    tokens = []
    position = 0

    while position < len(source_code):
        # Helper function to check if a character is alphanumeric
        def is_alphanumeric(char):
            return char.isalpha() or char.isdigit() or (char=='_')

        char = source_code[position]

        # Check for whitespace and skip it
        if char.isspace():
            position += 1
            continue

        # Identifier recognition
        if char.isalpha():
            lexeme = char
            position += 1
            while position < len(source_code) and is_alphanumeric(source_code[position]):
                lexeme += source_code[position]
                position += 1

            if lexeme in token_hierarchy:
                token_type = token_hierarchy[lexeme]
            else:
                # check if it is a valid identifier
                if is_valid_identifier(lexeme):
                    token_type = TokenType.IDENTIFIER
                else:
                    raise ValueError(f"Invalid identifier: {lexeme}")

        # Integer or Float recognition
        elif char.isdigit():
            lexeme = char
            position += 1

            is_float = False
            while position < len(source_code):
                next_char = source_code[position]
                # checking if it is a float, or a full-stop
                if next_char == '.':
                    if (position + 1 < len(source_code)):
                        next_next_char = source_code[position+1]
                        if next_next_char.isdigit():
                            is_float = True

                # checking for illegal identifier
                elif is_alphanumeric(next_char) and not next_char.isdigit():
                    while position < len(source_code) and is_alphanumeric(source_code[position]):
                        lexeme += source_code[position]
                        position += 1
                    if not is_valid_identifier(lexeme):
                        raise ValueError(f"Invalid identifier: {str(lexeme)}\nIdentifier can't start with digits")

                elif not next_char.isdigit():
                    break

                lexeme += next_char
                position += 1

            token_type = TokenType.FLOAT if is_float else TokenType.INTEGER

        # Symbol recognition
        else:
            lexeme = char
            position += 1
            token_type = TokenType.SYMBOL

        tokens.append((token_type, lexeme))

    return tokens

########################## BOILERPLATE ENDS ###########################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_pos = 0

    def parse(self):
        if not self.tokens:
            return
        while not self.is_at_end(): # statement -> (statement)(statement)
            self.statement()

    def statement(self):
        if self.match(TokenType.KEYWORD, 'if'):
            self.if_statement()
        elif self.match(TokenType.KEYWORD, 'else'):
            raise SyntaxError("SyntaxError: 'else' occurs before 'if'")
        else:
            self.simple_statement()

    def if_statement(self):
        self.condition()
        self.simple_statement()
        if self.match(TokenType.KEYWORD, 'else'):
            self.simple_statement()

    def simple_statement(self):
        if self.match(TokenType.KEYWORD, 'else'):
            raise SyntaxError("SyntaxError: Missing condition after 'if' statement")
        while not self.is_at_end() and self.peek()[1] not in ('if', 'else'):
            self.advance()

    def condition(self):
        """Parses a condition: cond -> x [op x]"""
        self.expression() # First 'x'
        # Check for optional operator and second 'x'
        if self.peek() and self.peek()[0] == TokenType.SYMBOL and self.peek()[1] in ('<', '>', '='):
            self.advance()
            self.expression()

    def expression(self):
        if self.peek() and self.peek()[0] in (TokenType.IDENTIFIER, TokenType.INTEGER, TokenType.FLOAT):
            self.advance()
            
    def match(self, token_type, token_value=None):
        # consumes the token as well
        if self.is_at_end():
            return False
        token = self.peek()
        if token[0] != token_type:
            return False
        if token_value is not None and token[1] != token_value:
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

def checkGrammar(tokens):
    if not tokens:
        return "No tokens to parse."
    parser = Parser(tokens)
    return parser.parse()

# Test the tokenizer
if __name__ == "__main__":
    try:
        source_code = input("Enter a statement: ")
        tokens = tokenize(source_code)

        logs = checkGrammar(tokens)
        
        for token in tokens:
            print(f"Token Type: {token[0]}, Token Value: {token[1]}")
        
        print("Syntax check passed.")

    except (ValueError, SyntaxError) as e:
        print(f"Error: {e}")
