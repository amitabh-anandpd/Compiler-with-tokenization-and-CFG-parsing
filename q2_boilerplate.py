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
    """
    Implements a recursive descent parser for the given grammar.

    The grammar provided in the PDF is ambiguous. This parser follows the logical
    structure implied by the examples: an 'if' statement consists of a condition,
    a 'then' block (a simple statement), and an optional 'else' block.
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        # Pre-emptive check for 'else' without a preceding 'if'
        if_seen = False
        for token_type, token_value in tokens:
            if token_value == 'if':
                if_seen = True
            if token_value == 'else' and not if_seen:
                raise SyntaxError("'else' occurs before 'if'")


    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return (TokenType.EOF, '')

    def advance(self):
        self.pos += 1

    def parse(self):
        """Starts the parsing process."""
        while self.current_token()[0] != TokenType.EOF:
            self.statement()
        return "Parsing successful."

    def statement(self):
        """Parses a statement, which can be an if-statement or a simple one."""
        token_type, token_value = self.current_token()
        if token_type == TokenType.KEYWORD and token_value == 'if':
            self.if_statement()
        else:
            self.simple_statement() # Corresponds to 'y' in the grammar

    def if_statement(self):
        """Parses an if-statement: 'if' condition statement ('else' statement)?"""
        # Consume 'if'
        self.advance()

        # Parse condition
        self.condition()

        # Parse 'then' statement
        self.statement()

        # Check for optional 'else'
        token_type, token_value = self.current_token()
        if token_type == TokenType.KEYWORD and token_value == 'else':
            # Consume 'else'
            self.advance()
            # Parse 'else' statement
            self.statement()

    def condition(self):
        """Parses a condition: x (op x)?"""
        self.x() # Parse the first operand
        # Check for an operator
        token_type, token_value = self.current_token()
        if token_type == TokenType.SYMBOL and token_value in "+-*^<>|=":
            self.advance() # Consume operator
            self.x() # Parse the second operand

    def x(self):
        """Parses an 'x' which can be an identifier or a number."""
        token_type, _ = self.current_token()
        if token_type in [TokenType.IDENTIFIER, TokenType.INTEGER, TokenType.FLOAT, TokenType.SYMBOL]:
            self.advance()
        else:
            # It could also be another condition, creating recursion.
            # This part is ambiguous in the grammar, but for simplicity we assume
            # x is a terminal token for now based on examples.
            raise SyntaxError(f"Unexpected token in expression: {self.current_token()[1]}")

    def simple_statement(self):
        """
        Parses a 'y' statement. Consumes tokens until a keyword or EOF is found.
        This rule is based on the note that Σ_statement includes keywords,
        numbers, identifiers, but not operators inside a statement block like 'print'.
        """
        while True:
            token_type, token_value = self.current_token()
            if token_type == TokenType.EOF or (token_type == TokenType.KEYWORD and token_value in ['if', 'else']):
                break
            self.advance()


def checkGrammar(tokens):
    """
    Initializes the Parser and runs the syntactic analysis.
    Returns logs or raises errors.
    """
    if not tokens:
        return "No tokens to parse."
    parser = Parser(tokens)
    return parser.parse()


# Main execution block
if __name__ == "__main__":
    try:
        source_code = input("Enter a statement: ")
        # 1. Lexical Analysis
        tokens = tokenize(source_code)

        # Print tokens if lexical analysis is successful
        print("\n--- Tokens ---")
        for token in tokens:
            print(f"Token Type: {token[0]}, Token Value: {token[1]}")
        print("--------------\n")

        # 2. Syntactic Analysis
        logs = checkGrammar(tokens)
        print("Syntax check passed.")

    except (ValueError, SyntaxError) as e:
        print(f"Error: {e}")
