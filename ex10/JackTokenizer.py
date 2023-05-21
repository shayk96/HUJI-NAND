"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import re
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """

    KEYWORDS = {"class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean",
                "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"}
    SYMBOLS = {"{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~", "#", "^"}
    DELIMITERS = r'([\(\)\[\]\{\}\,\;\.\=\+\-\*\/\&\|\~\#\^\<\>\s]|(?:"[^"]*"))'
    comments_pattern_regex = re.compile(r"(?P<string>\".*?\")|(?P<comment>//.*?\n|/\*\*?.*?\*/)|(?P<tab>\t)", re.DOTALL)

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.__input_file = input_stream.read()
        self.organize_input()
        self.__cur_token_index = -1
        self.__cur_token = "none"
        self.__num_braces = 0

    def organize_input(self) -> None:
        """ removes comments and tabs from the input"""

        def _rep(matched_obj) -> str:
            if matched_obj.group("comment"):
                return ""
            if matched_obj.group("tab"):
                return " "
            else:
                return matched_obj.group("string")

        self.__input_file = JackTokenizer.comments_pattern_regex.sub(_rep, self.__input_file)
        self.__input_file = re.split(JackTokenizer.DELIMITERS, self.__input_file)
        self.__input_file = [x for x in self.__input_file if x not in [" ", "", "\n"]]

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if self.__cur_token_index == len(self.__input_file) - 1:
            return False
        return True

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true.
        Initially there is no current token.
        """
        self.__cur_token_index += 1
        self.__cur_token = self.__input_file[self.__cur_token_index]

    def next_token(self) -> str:
        """advances the current token to the next token """
        next_index = self.__cur_token_index + 1
        next_token = self.__input_file[next_index]
        return next_token

    def get_token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.__cur_token in JackTokenizer.KEYWORDS:
            return "keyword"
        if self.__cur_token in JackTokenizer.SYMBOLS:
            return "symbol"
        if self.__cur_token[0] == '"':
            return "stringConstant"
        if self.__cur_token.isnumeric():
            return "integerConstant"
        else:
            return "identifier"

    def get_token(self):
        """ returns the current token"""
        if self.__cur_token in JackTokenizer.KEYWORDS:
            return self.keyword()
        if self.__cur_token in JackTokenizer.SYMBOLS:
            return self.symbol()
        if self.__cur_token[0] == '"':
            return self.string_val()
        if self.__cur_token.isnumeric():
            return self.int_val()
        else:
            return self.identifier()

    def find_closing_brace(self) -> int:
        """ finds the brace that closes the current expression"""
        left_braces = 1
        right_braces = 0
        for token_index in range(self.__cur_token_index, len(self.__input_file)):
            if self.__input_file[token_index] == "(":
                left_braces += 1
            if self.__input_file[token_index] == ")":
                right_braces += 1
            if left_braces == right_braces:
                return token_index

    def get_cur_index(self) -> int:
        """returns the current token index in the list"""
        return self.__cur_token_index

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO",
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.__cur_token

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        return self.__cur_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        return self.__cur_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        return int(self.__cur_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        return self.__cur_token[1:-1]
