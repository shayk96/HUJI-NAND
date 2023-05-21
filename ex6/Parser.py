"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads and assembly language 
    command, parses it, and provides convenient access to the commands 
    components (fields and symbols). In addition, removes all white space and 
    comments.
    """
    EQUAL = "="
    EQUAL_INDEX = 0
    COMMA = ";"
    COMMA_INDEX = 1
    NO_EXIST = -1
    AT = "@"
    L_BRACE = "("
    COMMENT = "/"
    SPACE = " "
    EMPTY_STRING = ""
    A_COMMAND = "A_COMMAND"
    L_COMMAND = "L_COMMAND"
    C_COMMAND = "C_COMMAND"
    NULL = "null"

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is:
        self.__input_lines = input_file.read().splitlines()
        self.fixed_lines()
        self.__cur = 0
        self.__in = self.__input_lines[self.__cur]
        self.__c_sym = [Parser.NO_EXIST, Parser.NO_EXIST]

    def fixed_lines(self) -> None:
        """ removes comments, empty spaces and indentations

        """
        fixed_lines = []
        for command in self.__input_lines:
            command = command.replace(Parser.SPACE, Parser.EMPTY_STRING)
            if command == Parser.EMPTY_STRING:
                continue
            if command[0] == Parser.COMMENT:
                continue
            if Parser.COMMENT in command:
                command = command[:command.find(Parser.COMMENT)]
            fixed_lines.append(command)
        self.__input_lines = fixed_lines

    def get_lines(self):
        """ a getter for the lines

        Returns:
            a list of all the commands in the hack language without comments, empty spaces and indentations
        """
        return self.__input_lines

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        if self.__cur == len(self.__input_lines) - 1:
            return False
        return True

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        self.__cur += 1
        self.__in = self.__input_lines[self.__cur]
        return

    def compute_c_symbols(self) -> None:
        """finds the indexes of the (=) sign and the (;) sign

        """
        counter = 0
        while self.__in[counter] != Parser.EQUAL:
            counter += 1
            if counter == len(self.__in) - 1:
                counter = Parser.NO_EXIST
                break
        self.__c_sym[Parser.EQUAL_INDEX] = counter
        counter = 0
        while self.__in[counter] != Parser.COMMA:
            counter += 1
            if counter == len(self.__in) - 1:
                counter = Parser.NO_EXIST
                break
        self.__c_sym[Parser.COMMA_INDEX] = counter

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self.__in[0] == Parser.AT:
            return Parser.A_COMMAND
        if self.__in[0] == Parser.L_BRACE:
            return Parser.L_COMMAND
        else:
            self.compute_c_symbols()
            return Parser.C_COMMAND

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or
            "L_COMMAND".
        """
        if self.command_type() == Parser.A_COMMAND:
            return self.__in[1:]
        if self.command_type() == Parser.L_COMMAND:
            return self.__in[1:-1]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called
            only when commandType() is "C_COMMAND".
        """
        if self.__c_sym[Parser.EQUAL_INDEX] == Parser.NO_EXIST:
            return Parser.NULL
        return self.__in[:self.__c_sym[Parser.EQUAL_INDEX]]

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called
            only when commandType() is "C_COMMAND".
        """
        if self.__c_sym[Parser.EQUAL_INDEX] == Parser.NO_EXIST:
            return self.__in[:self.__c_sym[Parser.COMMA_INDEX]]
        if self.__c_sym[Parser.COMMA_INDEX] == Parser.NO_EXIST:
            return self.__in[self.__c_sym[Parser.EQUAL_INDEX] + 1:]
        return self.__in[self.__c_sym[Parser.EQUAL_INDEX] + 1:self.__c_sym[Parser.COMMA_INDEX]]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called
            only when commandType() is "C_COMMAND".
        """
        if self.__c_sym[Parser.COMMA_INDEX] == Parser.NO_EXIST:
            return Parser.NULL
        return self.__in[self.__c_sym[Parser.COMMA_INDEX] + 1:]
