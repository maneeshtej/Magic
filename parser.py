class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0  
        self.variables = {}  

    def peek(self, pos=None):
        """Look at a token at a given position without consuming it.
        Defaults to the current position (self.position) if no position is provided."""
        if pos is None:
            pos = self.position  
        return self.tokens[pos] if pos < len(self.tokens) else None


    def consume(self):
        """Consume and return the current token, or raise an error if there are no more tokens"""
        if self.position < len(self.tokens):
            token = self.tokens[self.position]
            self.position += 1
            return token
        raise SyntaxError("Unexpected end of input")


    def parse(self):
        # print("running parse")
        """Parse the tokens one by one"""
        while self.position < len(self.tokens):
            token_type, value = self.consume()

            if token_type == "NEWLINE": 
                continue
            if token_type == "ITEM":
                self.parse_variable_declaration()
            elif token_type == "PRINT":
                self.parse_print()
            elif token_type == "IDENTIFIER":
                self.parse_reassign(value)
            elif token_type == "INPUT":
                self.parse_input()
            elif token_type == "IF":
                self.parse_conditional()
            elif token_type == "LOOP":
                self.parse_loop()
            elif token_type == "INDENT":
                continue
            elif token_type == "DEDENT":
                self.position -= 1
                return
            else:
                raise SyntaxError(f"Unexpected token: {token_type} : {value}")
            
    def evaluate_expression(self):
        expression = ""
        result = 0
        if self.peek() and self.peek()[0] == "STRING":
            while self.peek() and self.peek()[0] != "NEWLINE":
                value_token, value = self.consume()
                if value_token not in ["PLUS", "MINUS"]:
                    if value_token == "NUMBER":
                        expression += str(value)
                    else:
                        expression += value[1:-1]
            result = expression.strip()
        else:
            while self.peek() and self.peek()[0] != "NEWLINE":
                value_token, value = self.consume()
                if value_token not in ["NUMBER", "IDENTIFIER", "PLUS", "MINUS"]:
                    raise SyntaxError(f"did not expect {value}, {value_token}")
            
                if value_token == "NUMBER":
                    expression += value
                elif value_token == "IDENTIFIER":
                    if value not in self.variables:
                        raise SyntaxError(f"variable not declared, {value}")
                    expression += str(self.variables[value])
                elif value_token in ["PLUS", "MINUS"]:
                    expression += value

            try:
                result = eval(expression, {"__builtins__": None}, {}) 
            except Exception as e:
                raise SyntaxError(f"Invalid expression: {expression}") from e

        return result



    def parse_variable_declaration(self):
        """Parses `item x = 5`, `item x = 2 + 4 + 5 - 3`, `item x = y + 3`"""
        var_token = self.consume()
        
        if var_token is None or var_token[0] != "IDENTIFIER":
            raise SyntaxError(f"Expected a variable name, got {var_token}")
        
        var_name = var_token[1]  # Get variable name

        # Check for assignment (`=`)
        if self.peek() and self.peek()[0] == "EQUALS":
            self.consume()  # Consume '='

            # Skip any newlines after '=' (if mistakenly placed)
            while self.peek() and self.peek()[0] == "NEWLINE":
                self.consume()

            value = self.evaluate_expression()

            self.variables[var_name] = int(value)
        else:
            self.variables[var_name] = None



    def parse_print(self):
        """Handles print statements like:
        - `print x`
        - `print "hello"`
        - `print x + 5`
        - `print x, y, "hello"`
        - `print x + " world"` (if x is a string)
        """
        values = []

        while self.peek() and self.peek()[0] != "NEWLINE":
            value = self.evaluate_expression()  # Use existing expression evaluator
            values.append(str(value))  # Convert everything to string for printing

            if self.peek() and self.peek()[0] == "COMMA":
                self.consume()  # Consume the comma
                if not self.peek() or self.peek()[0] == "NEWLINE":
                    raise SyntaxError("Unexpected ',' at end of print statement")
            elif self.peek() and self.peek()[0] != "NEWLINE":
                raise SyntaxError(f"Expected ',' or end of line, got {self.peek()[1]}")

        print(" ".join(values))  # Print all evaluated values
 

    
    def parse_reassign(self, var_name):
        """Handles reassignments like `x = 5`, `x = "hello"`, `x = y`, `x = y + 3`."""
        
        if var_name not in self.variables:
            raise SyntaxError(f"Variable '{var_name}' not declared before assignment.")
        
        # Ensure '=' is present
        if not self.peek() or self.peek()[0] != "EQUALS":
            raise SyntaxError(f"Expected '=' after {var_name}, got {self.peek()}")
        
        self.consume()  # Consume '='

        # Skip any unnecessary newlines
        while self.peek() and self.peek()[0] == "NEWLINE":
            self.consume()

        # Evaluate expression (this handles numbers, identifiers, and operators)
        value = self.evaluate_expression()

        # Store the evaluated value in the variable
        self.variables[var_name] = value



    def parse_input(self):
        
            """Handles input like: input x and assigns the correct type."""
            value_token = self.consume()

            if value_token is None or value_token[0] != "IDENTIFIER":
                raise SyntaxError(f"Expected identifier, got {value_token}")

            var_name = value_token[1]

            if var_name not in self.variables:
                raise SyntaxError(f"Variable '{var_name}' not declared before assignment.")
        
        
            user_input = input(f"Enter value for {var_name}: ").strip()

            if user_input.isdigit():
                value = int(user_input)
            else:
                try:
                    value = float(user_input)
                except ValueError:
                    value = user_input  

            self.variables[var_name] = value
        # print(f"updated variable {var_name} : {self.variables[var_name]}, type = {type(self.variables[var_name])}")

    def parse_conditional(self):
        """Parses and executes an `if` statement block"""
        value_token, value = self.consume()
        if value_token == "IDENTIFIER":
            if value not in self.variables:
                raise SyntaxError(f"Unexpected identifier, not defined: {value}")
            condition1 = self.variables[value]
        elif value_token == "NUMBER":
            condition1 = int(value)
        elif value_token == "STRING":
            condition1 = value
        else:
            raise SyntaxError(f"Expected identifier or number, got {value}, {value_token}")
        
        value_token, value = self.consume()
        if value_token != "COMPARISON":
            raise SyntaxError(f"Expected comparison, got {value}, {value_token}")
        comparison = value

        value_token, value = self.consume()
        if value_token == "IDENTIFIER":
            if value not in self.variables:
                raise SyntaxError(f"Unexpected identifier, not defined: {value}")
            condition2 = self.variables[value]
        elif value_token == "NUMBER":
            condition2 = int(value)
        elif value_token == "STRING":
            condition2 = value
        else:
            raise SyntaxError(f"Expected identifier or number, got {value}, {value_token}")
        
        value_token, value = self.consume()
        if value_token != "COLON":
            raise SyntaxError(f"Expected colon, got {value}, {value_token}")
        
        # print(type(condition1), type(condition2))

        condition_str = f"{repr(condition1)} {comparison} {repr(condition2)}"
        try:
            condition_result = eval(condition_str)
        except Exception as e:
            raise SyntaxError(f"Error evaluating condition: {e}")
        
        # print(condition_result, "195")

        
        value_token, value = self.consume()
        if value_token != "NEWLINE":
            raise SyntaxError("Please write the body in the next line after ':'")

       
        if condition_result:
            while self.peek() and self.peek()[0] != "DEDENT":
                self.parse()
        else:
            while self.peek() and self.peek()[0] != "DEDENT":
                self.consume()
            
        if self.peek() and self.peek()[0] == "DEDENT":
            self.consume()
            return

    def parse_loop(self):
        value_token, value = self.consume()
        if (value_token == "IDENTIFIER"):
            self.variables[value] = 0
            loop_var = value
            value_token, value = self.consume()
        else:
            self.variables["i"] = 0
            loop_var = "i"

        if value_token == "NUMBER":
            count = int(value)
        elif value_token == "IDENTIFIER":
            if value not in self.variables:
                raise SyntaxError(f"Variable {value} not declared")
            count = int(self.variables[value])

        value_token, value  = self.consume()
        if value_token not in ["TIMES"]:
            raise SyntaxError(f"expected 'times' got {value}, {value_token}")

        value_token, value = self.consume()
        if value_token != "COLON":
            raise SyntaxError(f"expected ':', got {value}, {value_token}")
        
        
        pos = self.position

        while count > 0:
            count -= 1
            self.position = pos
            while self.peek() and self.peek()[0] != "DEDENT":
                self.parse()
            self.variables[loop_var] += 1

        if self.peek() and self.peek()[0] == "DEDENT":
            del self.variables[loop_var]
            self.consume()

        # while self.peek():
        #     print(self.consume())
            
        
        # print(self.consume())
        return

        
        


        