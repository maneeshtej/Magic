from lexer import Lexer
from parser import Parser


with open ('first.magic', 'r') as file:
    content = file.read()
    # print(content)

    # Run Lexer
    lexer = Lexer(content)
    tokens = lexer.tokenize()
    # print(tokens)

    # Run Parser
    parser = Parser(tokens)
    parser.parse()

