# Compiler with Syntactic Analysis (`q2.py`)

The second part of the assignment involved creating a simple compiler responsible for performing lexical and syntactic analysis on a single line of source code.

## Implementation Details

1. **Lexical Analysis (Tokenizer):** The provided boilerplate code performs lexical analysis, or tokenization. It processes the input string and segments it into a sequence of discrete tokens, classified by type (e.g., `KEYWORD`, `IDENTIFIER`, `NUMBER`). The tokenizer adheres to a token hierarchy and includes error handling for lexically invalid formations, such as identifiers commencing with a digit.

2. **Syntactic Analysis (Parser):** Following tokenization, a parser performs syntactic analysis. A recursive descent parser was implemented to validate whether the token sequence adheres to the specified context-free grammar. The parser's structure mirrors the grammatical rules, with functions dedicated to parsing specific constructs like 'if' statements. It is designed to identify and report syntactical errors, such as an `else` clause that is not preceded by a corresponding `if` statement.