"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    statements_set = {"let", "if", "while", "do", "return"}
    keyword_constant = {"true": ["constant", 1], "false": ["constant", 0], "null": ["constant", 0],
                        "this": ["pointer", 0]}
    operators = {"+": "add", "-": "sub", "*": "call Math.multiply 2", "/": "call Math.divide 2", "&": "and", "|": "or",
                 ">": "gt", "<": "lt", "=": "eq"}
    unary_operators = {"-": "neg", "~": "not", "#": "shiftright", "^": "shiftleft"}

    XML_markup = {"<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;"}

    def __init__(self, input_stream: typing.TextIO, output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.__if_counter = -1
        self.__while_counter = -1
        self.__vm_writer = VMWriter(output_stream)
        self.__symbol_table = SymbolTable()
        self.__tokenizer = JackTokenizer(input_stream)
        self.__output = output_stream
        self.__classname = self.__tokenizer.get_class_name()

    def initialize_class(self):
        """prints the initialization if the class, returns next token"""
        self.__tokenizer.advance()
        while self.__tokenizer.has_more_tokens() and self.__tokenizer.get_token() != "{":
            self.__tokenizer.advance()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.initialize_class()
        while self.__tokenizer.has_more_tokens() and self.__tokenizer.get_token() != "}":
            if self.__tokenizer.get_token() in ["static", "field"]:
                self.compile_class_var_dec()
            elif self.__tokenizer.get_token() in ["constructor", "function", "method"]:
                self.compile_subroutine()
            self.__tokenizer.advance()

    def dick_func(self):
        """the function holds a dictionary that calls the corresponding function of the keyword. only keywords that
        needs a nwe scope are called """
        keyword = self.__tokenizer.get_token()
        func_dick = {"method": self.compile_subroutine, "function": self.compile_subroutine,
                     "constructor": self.compile_subroutine,
                     "let": self.compile_let, "do": self.compile_do, "if": self.compile_if,
                     "while": self.compile_while, "return": self.compile_return}
        return func_dick[keyword]()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        variable = []
        var_type = self.__tokenizer.get_token()
        self.__tokenizer.advance()
        while self.__tokenizer.get_token() != ";":
            if self.__tokenizer.get_token() != ',':
                variable.append(self.__tokenizer.get_token())
            if len(variable) == 2:
                self.__symbol_table.define(variable[1], variable[0], var_type)
                variable.pop()
            self.__tokenizer.advance()

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        subroutine_type = self.__tokenizer.get_token()
        self.__tokenizer.advance(2)
        subroutine_name = self.__tokenizer.get_token()
        while self.__tokenizer.get_token() != "}":
            if self.__tokenizer.get_token() == "(":  # parameter list
                self.__tokenizer.advance()
                self.compile_parameter_list(subroutine_type)
            if self.__tokenizer.get_token() == "{":  # subroutine body
                self.compile_subroutine_body(subroutine_type, subroutine_name)
                break
            self.__tokenizer.advance()
        self.__symbol_table.clear()

    def compile_subroutine_body(self, subroutine_type, subroutine_name) -> None:
        """compiles the body of the function"""
        self.__tokenizer.advance()
        while self.__tokenizer.get_token() != "}":
            if self.__tokenizer.get_token() in CompilationEngine.statements_set:
                self.write_function(subroutine_name, subroutine_type)
                self.compile_statements()
                break
            elif self.__tokenizer.get_token() == "var":
                self.compile_var_dec()
            self.__tokenizer.advance()

    def write_function(self, subroutine_name, subroutine_type):
        self.__vm_writer.write_function(self.__classname + "." + subroutine_name, self.__symbol_table.var_count("var"))
        if subroutine_type == "constructor":  # allocates memory for the size of the class in the constructor
            class_table_size = self.__symbol_table.var_count("field")
            self.__vm_writer.write_push("constant", class_table_size)
            self.__vm_writer.write_call("Memory.alloc", 1)
            self.__vm_writer.write_pop("pointer", 0)
        if subroutine_type == "method":
            self.__vm_writer.write_push("argument", 0)
            self.__vm_writer.write_pop("pointer", 0)

    def compile_parameter_list(self, subroutine_type: str) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        arguments = []
        if subroutine_type == "method":
            self.__symbol_table.define("this", self.__classname, "argument")
        while self.__tokenizer.get_token() != ')':
            if self.__tokenizer.get_token() != ',':
                arguments.append(self.__tokenizer.get_token())
            if len(arguments) == 2:
                self.__symbol_table.define(arguments[1], arguments[0], "argument")
                arguments.clear()
            self.__tokenizer.advance()

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        variable = []
        while self.__tokenizer.get_token() != ";":
            if self.__tokenizer.get_token() != ',':
                variable.append(self.__tokenizer.get_token())
            if len(variable) == 3:
                self.__symbol_table.define(variable[2], variable[1], "var")
                variable.pop()
            self.__tokenizer.advance()

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        while self.__tokenizer.get_token() in CompilationEngine.statements_set:
            self.dick_func()
            self.__tokenizer.advance()

    def subroutine_call(self):
        """token is one after the printed one"""
        num_of_arguments = 0
        function_class = self.__tokenizer.get_token()
        if self.__symbol_table.search_tables(self.__tokenizer.get_token()):  # calling from class object - xxx.run()
            token_kind = self.__symbol_table.kind_of(self.__tokenizer.get_token())
            token_index = self.__symbol_table.index_of(self.__tokenizer.get_token())
            function_class = self.__symbol_table.type_of(self.__tokenizer.get_token())
            self.__vm_writer.write_push(token_kind, token_index)
            num_of_arguments += 1
        function_name = function_class + self.__tokenizer.next_token() + self.__tokenizer.next_token(2)
        if self.__tokenizer.next_token() != ".":  # call an "in class" function
            self.__vm_writer.write_push("pointer", 0)
            num_of_arguments += 1
            function_name = self.__classname + "." + self.__tokenizer.get_token()
        elif self.__tokenizer.next_token(4) == "this":
            self.__tokenizer.erase_token(4)
            self.__vm_writer.write_push("pointer", 0)
            num_of_arguments += 1
        while self.__tokenizer.get_token() != ")":
            if self.__tokenizer.get_token() == "(":
                self.__tokenizer.advance()
                num_of_arguments += self.compile_expression_list()
                continue
            self.__tokenizer.advance()
        self.__vm_writer.write_call(function_name, num_of_arguments)

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.__tokenizer.advance()
        self.subroutine_call()
        self.__tokenizer.advance()
        self.__vm_writer.write_pop("temp", 0)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        assignment_type = self.__tokenizer.next_token(2)
        self.__tokenizer.advance()
        var_name = self.__tokenizer.get_token()
        if assignment_type == "=":
            self.__tokenizer.advance(2)
            self.compile_expression()
            self.__vm_writer.write_pop(self.__symbol_table.kind_of(var_name), self.__symbol_table.index_of(var_name))
        else:
            self.__vm_writer.write_push(self.__symbol_table.kind_of(var_name), self.__symbol_table.index_of(var_name))
            self.__tokenizer.advance(2)
            self.compile_expression()
            self.__vm_writer.write_arithmetic("add")
            self.__tokenizer.advance(2)
            self.compile_expression()
            self.__vm_writer.write_pop("temp", 0)
            self.__vm_writer.write_pop("pointer", 1)
            self.__vm_writer.write_push("temp", 0)
            self.__vm_writer.write_pop("that", 0)
        # self.__tokenizer.advance()

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.__while_counter += 1
        counter = self.__while_counter
        self.__vm_writer.write_label("WHILE_BEGIN", counter)
        self.expressions_statements_routine("WHILE_END", counter)
        self.__vm_writer.write_goto("WHILE_BEGIN", counter)
        self.__vm_writer.write_label("WHILE_END", counter)

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.__tokenizer.advance()
        if self.__tokenizer.get_token() != ";":
            self.compile_expression()
        else:
            self.__vm_writer.write_push("constant", 0)
        self.__vm_writer.write_return()

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.__if_counter += 1
        counter = self.__if_counter
        self.expressions_statements_routine("IF_FALSE", counter)
        self.__vm_writer.write_goto("IF_END", counter)
        self.__vm_writer.write_label("IF_FALSE", counter)
        if self.__tokenizer.next_token() == "else":
            self.__tokenizer.advance()
            self.expressions_statements_routine("PLACE_HOLDER", 5555555555)
        self.__vm_writer.write_label("IF_END", counter)

    def expressions_statements_routine(self, label: str, counter: int) -> None:
        """returns token == "}" """
        while self.__tokenizer.get_token() != "}":
            if self.__tokenizer.get_token() == "(":
                self.__tokenizer.advance()  # token == "(" + 1
                self.compile_expression()
                self.__vm_writer.write_arithmetic("not")
                self.__vm_writer.write_if(label, counter)
            elif self.__tokenizer.get_token() == "{":
                self.__tokenizer.advance()
                self.compile_statements()
                break
            self.__tokenizer.advance()

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        self.__tokenizer.advance()
        while self.__tokenizer.get_token() not in ["]", ")", ",", ";"]:
            if self.__tokenizer.get_token() in CompilationEngine.operators:
                operator = self.__tokenizer.get_token()
                self.__tokenizer.advance()
                self.compile_term()
                self.__vm_writer.write_arithmetic(CompilationEngine.operators[operator])
                self.__tokenizer.advance()

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        token_type = self.__tokenizer.get_token_type()
        token = self.__tokenizer.get_token()
        identifier = self.__symbol_table.search_tables(self.__tokenizer.get_token())
        assignment_type = self.__tokenizer.next_token()

        if token_type == "integerConstant":  # assignment of an int
            self.__vm_writer.write_push("constant", token)

        elif token in CompilationEngine.keyword_constant:  # assignment of this, true, false,null
            self.__vm_writer.write_push(CompilationEngine.keyword_constant[token][0],
                                        CompilationEngine.keyword_constant[token][1])
            if token == "true":
                self.__vm_writer.write_arithmetic("neg")

        elif token_type == "stringConstant":
            string_length = len(token)
            self.__vm_writer.write_push("constant", string_length)
            self.__vm_writer.write_call("String.new", 1)
            for i in token:
                self.__vm_writer.write_push("constant", ord(i))
                self.__vm_writer.write_call("String.appendChar", 2)

        elif assignment_type == "[":  # assignment of an array
            self.__vm_writer.write_push(self.__symbol_table.kind_of(token), self.__symbol_table.index_of(token))
            self.__tokenizer.advance(2)
            self.compile_expression()
            self.__vm_writer.write_arithmetic("add")
            self.__vm_writer.write_pop("pointer", 1)
            self.__vm_writer.write_push("that", 0)

        elif token == "(":  # assignment of expression
            self.__tokenizer.advance()
            self.compile_expression()

        elif token in CompilationEngine.unary_operators:  # assignment of unary operator
            self.__tokenizer.advance()
            self.compile_term()
            self.__vm_writer.write_arithmetic(CompilationEngine.unary_operators[token])

        elif self.__tokenizer.next_token() in {".", "("}:  # assignment of a function call
            self.subroutine_call()

        elif identifier is not None:  # assignment of a var
            self.__vm_writer.write_push(identifier[1], identifier[2])

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        expressions = 0
        last_brace_index = self.__tokenizer.find_closing_brace()
        while self.__tokenizer.get_cur_index() != last_brace_index:
            if self.__tokenizer.get_token() == ",":
                self.__tokenizer.advance()
                continue
            self.compile_expression()
            expressions += 1
        return expressions
