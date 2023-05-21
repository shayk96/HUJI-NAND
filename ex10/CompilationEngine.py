"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

from JackTokenizer import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    statements_set = {"let", "if", "while", "do", "return"}
    keyword_constant = {"true", "false", "null", "this"}
    operators = {"+", "-", "*", "/", "&", "|", ">", "<", "="}
    UNARY_OPERATORS = {"-", "~", "#", "^"}
    XML_markup = {"<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;"}

    def __init__(self, input_stream: typing.TextIO, output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.__tokenizer = JackTokenizer(input_stream)
        self.__output = output_stream

    def tokens_pattern(self, flag: bool = False) -> None:
        """prints the correct pattern to the XML file"""
        token_type = self.__tokenizer.get_token_type()
        token = self.__tokenizer.get_token()
        if flag and token == "this" and self.__tokenizer.next_token() == "=":
            token_type = "identifier"
        if token in CompilationEngine.XML_markup:
            token = CompilationEngine.XML_markup[token]
        self.__output.write("<" + token_type + "> " + str(token) + " </" + token_type + ">\n")

    def initialize_class(self) -> None:
        """prints the initialization if the class, returns next token"""
        self.__tokenizer.advance()
        while self.__tokenizer.has_more_tokens() and self.__tokenizer.get_token() != "{":
            self.tokens_pattern()
            self.__tokenizer.advance()
        self.tokens_pattern()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.__output.write("<class>\n")
        self.initialize_class()
        while self.__tokenizer.has_more_tokens() and self.__tokenizer.get_token() != "}":
            if self.__tokenizer.get_token() in ["static", "field"]:
                self.compile_class_var_dec()
            elif self.__tokenizer.get_token() in ["constructor", "function", "method"]:
                self.compile_subroutine()
            self.__tokenizer.advance()

        self.tokens_pattern()  # prints "}"
        self.__output.write("</class>\n")

    def dick_func(self):
        """the function holds a dictionary that calls the corresponding function of the keyword. only keywords that
        needs a new scope are called """
        keyword = self.__tokenizer.get_token()
        func_dick = {"method": self.compile_subroutine, "function": self.compile_subroutine,
                     "constructor": self.compile_subroutine,
                     "let": self.compile_let, "do": self.compile_do, "if": self.compile_if,
                     "while": self.compile_while, "return": self.compile_return}
        return func_dick[keyword]()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.__output.write("<classVarDec>\n")
        while self.__tokenizer.get_token() != ";":
            self.tokens_pattern()
            self.__tokenizer.advance()
        self.tokens_pattern()
        self.__output.write("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        self.__output.write("<subroutineDec>\n")  # token == function/method/constructor
        while self.__tokenizer.get_token() != "}":
            if self.__tokenizer.get_token() == "(":  # parameter list
                self.tokens_pattern()  # print "("
                self.__tokenizer.advance()
                self.compile_parameter_list()
                self.tokens_pattern()  # print ")"
            if self.__tokenizer.get_token() == "{":  # subroutine body
                self.compile_subroutine_body()
                break
            if self.__tokenizer.get_token() != ")":  # already printed in the first if
                self.tokens_pattern()
            self.__tokenizer.advance()
        self.__output.write("</subroutineDec>\n")

    def compile_subroutine_body(self) -> None:
        """compiles the body of the function"""
        self.__output.write("<subroutineBody>\n")  # token == {
        self.tokens_pattern()
        self.__tokenizer.advance()
        while self.__tokenizer.get_token() != "}":
            if self.__tokenizer.get_token() in CompilationEngine.statements_set:
                self.compile_statements()
                break
            elif self.__tokenizer.get_token() == "var":
                self.compile_var_dec()
            self.__tokenizer.advance()
        self.tokens_pattern()  # prints "}"
        self.__output.write("</subroutineBody>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        self.__output.write("<parameterList>\n")
        while self.__tokenizer.get_token() != ')':
            self.tokens_pattern()
            self.__tokenizer.advance()
        self.__output.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.__output.write("<varDec>\n")
        while self.__tokenizer.get_token() != ";":
            self.tokens_pattern()
            self.__tokenizer.advance()
        self.tokens_pattern()
        self.__output.write("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        self.__output.write("<statements>\n")
        while self.__tokenizer.get_token() in CompilationEngine.statements_set:
            self.dick_func()
            self.__tokenizer.advance()
        self.__output.write("</statements>\n")

    def subroutine_call(self) -> None:
        """token is one after the printed one"""
        while self.__tokenizer.get_token() != ")":
            self.tokens_pattern()
            if self.__tokenizer.get_token() == "(":
                self.__tokenizer.advance()
                self.compile_expression_list()
                continue
            self.__tokenizer.advance()
        self.tokens_pattern()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.__output.write("<doStatement>\n")
        self.tokens_pattern()  # prints "do"
        self.__tokenizer.advance()
        self.subroutine_call()
        self.__tokenizer.advance()
        self.tokens_pattern()  # prints ";"
        self.__output.write("</doStatement>\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.__output.write("<letStatement>\n")
        while self.__tokenizer.get_token() != ";":
            self.tokens_pattern(True)
            if self.__tokenizer.get_token() in {"[", "="}:
                self.__tokenizer.advance()
                self.compile_expression()
                continue  # compile expression already advanced the token
            self.__tokenizer.advance()
        self.tokens_pattern()  # prints ";"
        self.__output.write("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.__output.write("<whileStatement>\n")
        self.expressions_statements_routine()
        self.tokens_pattern()
        self.__output.write("</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.__output.write("<returnStatement>\n")
        self.tokens_pattern()
        self.__tokenizer.advance()
        if self.__tokenizer.get_token() != ";":
            self.compile_expression()
        self.tokens_pattern()  # prints ";"
        self.__output.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.__output.write("<ifStatement>\n")
        self.expressions_statements_routine()
        if self.__tokenizer.next_token() == "else":
            self.tokens_pattern()  # prints "}"
            self.__tokenizer.advance()
            self.expressions_statements_routine()
        self.tokens_pattern()  # prints "}"
        self.__output.write("</ifStatement>\n")

    def expressions_statements_routine(self) -> None:
        """returns token == "}" """
        while self.__tokenizer.get_token() != "}":
            self.tokens_pattern()
            if self.__tokenizer.get_token() == "(":
                self.__tokenizer.advance()  # token == "(" + 1
                self.compile_expression()
                self.tokens_pattern()
            elif self.__tokenizer.get_token() == "{":
                self.__tokenizer.advance()
                self.compile_statements()
                break
            self.__tokenizer.advance()

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.__output.write("<expression>\n")
        while self.__tokenizer.get_token() not in ["]", ")", ",", ";"]:
            self.compile_term()
            self.__tokenizer.advance()
            if self.__tokenizer.get_token() in CompilationEngine.operators:
                self.tokens_pattern()
                self.__tokenizer.advance()
        self.__output.write("</expression>\n")

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
        self.__output.write("<term>\n")
        if self.__tokenizer.get_token_type() in ["keyword", "stringConstant", "integerConstant"]:
            self.tokens_pattern()
        elif self.__tokenizer.get_token() == "(":
            self.tokens_pattern()
            self.__tokenizer.advance()
            self.compile_expression()
            self.tokens_pattern()
        elif self.__tokenizer.get_token() in CompilationEngine.UNARY_OPERATORS:
            self.tokens_pattern()
            self.__tokenizer.advance()
            self.compile_term()
        else:  # checks one ahead
            if self.__tokenizer.next_token() == "[":
                self.tokens_pattern()
                self.__tokenizer.advance()
                self.tokens_pattern()
                self.__tokenizer.advance()
                self.compile_expression()
                self.tokens_pattern()
            elif self.__tokenizer.next_token() in [".", "("]:
                self.subroutine_call()
            else:
                self.tokens_pattern()
        self.__output.write("</term>\n")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.__output.write("<expressionList>\n")
        last_brace_index = self.__tokenizer.find_closing_brace()
        while self.__tokenizer.get_cur_index() != last_brace_index:
            if self.__tokenizer.get_token() == ",":
                self.tokens_pattern()
                self.__tokenizer.advance()
                continue
            self.compile_expression()
        self.__output.write("</expressionList>\n")
