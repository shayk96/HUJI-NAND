"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """
    COMMENT = "/"
    SPACE = " "
    EMPTY_STRING = ""
    ARITHMETIC_COMMANDS = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not", "shiftleft", "shiftright"]
    MEMORY_COMMANDS = {"push": "C_PUSH", "pop": "C_POP", "label": "C_LABEL", "goto": "C_GOTO", "if-goto": "C_IF",
                       "function": "C_FUNCTION", "return": "C_RETURN", "call": "C_CALL"}
    C_ARITHMETIC = "C_ARITHMETIC"
    COMMAND_TYPE = 0
    ARG_1 = 1
    ARG_2 = 2

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.__input_lines = input_file.read().splitlines()
        self.fixed_lines()
        self.__cur = -1
        self.__in = self.__input_lines[self.__cur]

    def fixed_lines(self) -> None:
        """ removes comments, empty spaces and indentations

        """
        fixed_lines = []
        for command in self.__input_lines:
            if command == Parser.EMPTY_STRING:
                continue
            if command[0] == Parser.COMMENT:
                continue
            if Parser.COMMENT in command:
                command = command[:command.find(Parser.COMMENT)]
            fixed_lines.append(command.split())  # list of lists
        self.__input_lines = fixed_lines

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        if self.__cur == len(self.__input_lines) - 1:
            return False
        return True

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true.
        Initially
        there is no current command.
        """
        self.__cur += 1
        self.__in = self.__input_lines[self.__cur]
        return

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        if self.__in[Parser.COMMAND_TYPE] in Parser.ARITHMETIC_COMMANDS:
            return Parser.C_ARITHMETIC
        return Parser.MEMORY_COMMANDS[self.__in[Parser.COMMAND_TYPE]]

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        if self.__in[Parser.COMMAND_TYPE] in Parser.ARITHMETIC_COMMANDS:
            return self.__in[Parser.COMMAND_TYPE]
        return self.__in[Parser.ARG_1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        return int(self.__in[Parser.ARG_2])
