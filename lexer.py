



import re

TOKEN_TYPES = {
    "ITEM": r"\bitem\b",               # item keyword
    "PRINT": r"\bprint\b",             # print keyword
    "INPUT": r"\binput\b",             # input keyword
    "LOOP": r"\bloop\b",               # loop keyword
    "WHILE": r"\bwhile\b",             # while keyword (for loop conditions)
    "IF": r"\bif\b",                   # if condition
    "ELSE": r"\belse\b",               # else condition
    "ELIF": r"\belif\b",               # else if condition
    "TIMES": r"\btimes\b",             # Match "times" (without colon)
    "IDENTIFIER": r"[a-zA-Z_]\w*",     # Variable names (x, var1, my_var)
    "NUMBER": r"\d+",                  # Numbers (10, 20)
    "EQUALS": r"=",                    # Assignment operator =
    "STRING": r'"[^"]*"',              # Strings like "hello world"
    "COMPARISON": r"[<>!=]=?|==",      # Comparison operators (<, >, ==, !=, >=, <=)
    "COLON": r":",                     # Explicitly match ":"
    "COMMA": r",",                     # Comma
    "NEWLINE": r"\n",                  # New lines
    "WHITESPACE": r"[ ]+",             # Spaces (no tabs)
    "AND": r"\band\b",
    "OR": r"\bor\b",
}

class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.position = 0
        self.indent_stack = [0]  # Track indentation levels

    def tokenize(self):
        lines = self.code.split("\n")  # Split into lines
        for line in lines:
            self.process_line(line)
        
        # At the end of the file, close all remaining indents
        while len(self.indent_stack) > 1:
            self.tokens.append(("DEDENT", ""))
            self.indent_stack.pop()

        return self.tokens

    def process_line(self, line):
        """Handles indentation and tokenization for each line."""
        if not line.strip():  # Ignore empty lines
            return
        
        match = re.match(r"([ ]*)(.*)", line)  # Capture leading spaces and the rest
        spaces, content = match.groups()
        indent_level = len(spaces)  # Count spaces

        # Handle indentation changes
        if indent_level > self.indent_stack[-1]:
            self.tokens.append(("INDENT", ""))
            self.indent_stack.append(indent_level)
        elif indent_level < self.indent_stack[-1]:
            while self.indent_stack and indent_level < self.indent_stack[-1]:
                self.tokens.append(("DEDENT", ""))
                self.indent_stack.pop()

        # Tokenize the rest of the line
        self.tokenize_content(content)

    def tokenize_content(self, content):
        """Tokenize the non-whitespace content of a line."""
        position = 0
        while position < len(content):
            match = None
            for token_type, pattern in TOKEN_TYPES.items():
                regex = re.compile(pattern)
                match = regex.match(content, position)
                if match:
                    if token_type not in ["WHITESPACE"]:  # Ignore spaces inside lines
                        self.tokens.append((token_type, match.group()))
                    position = match.end()
                    break
            
            if not match:
                raise SyntaxError(f"Unexpected character at {position}: {content[position]}")

        self.tokens.append(("NEWLINE", "\\n"))  # Add a newline token









       



