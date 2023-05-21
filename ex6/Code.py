"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

from Parser import Parser
from SymbolTable import SymbolTable


class Code:
    """Translates Hack assembly language mnemonics into binary codes."""

    BIT_LENGTH = 16
    ZERO = "0"

    DEST_DICK = {"null": "000", "M": "001", "D": "010", "MD": "011", "A": "100", "AM": "101", "AD": "110", "AMD": "111"}
    COMP_DICK = {"0": "1110101010", "1": "1110111111", "-1": "1110111010", "D": "1110001100", "A": "1110110000",
                 "!D": "1110001101",
                 "!A": "1110110001", "-D": "1110001111", "-A": "1110110011", "D+1": "1110011111", "A+1": "1110110111",
                 "D-1": "1110001110",
                 "A-1": "1110110010", "D+A": "1110000010", "D-A": "1110010011", "A-D": "1110000111",
                 "D&A": "1110000000",
                 "D|A": "1110010101", "M": "1111110000", "!M": "1111110001", "-M": "1111110011", "M+1": "1111110111",
                 "M-1": "1111110010",
                 "D+M": "1111000010", "D-M": "1111010011", "M-D": "1111000111", "D&M": "1111000000",
                 "D|M": "1111010101",
                 "D<<": "1010110000", "A<<": "1010100000", "M<<": "1011100000", "D>>": "1010010000",
                 "A>>": "1010000000",
                 "M>>": "1011000000"}
    JUMP_DICK = {"null": "000", "JGT": "001", "JEQ": "010", "JGE": "011", "JLT": "100", "JNE": "101", "JLE": "110",
                 "JMP": "111"}

    @staticmethod
    def dest(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a dest mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        return Code.DEST_DICK[mnemonic]

    @staticmethod
    def comp(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a comp mnemonic string.

        Returns:
            str: 7-bit long binary code of the given mnemonic.
        """
        return Code.COMP_DICK[mnemonic]

    @staticmethod
    def jump(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a jump mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        return Code.JUMP_DICK[mnemonic]

    @staticmethod
    def calc_binary(number: int) -> str:
        """
        Args:
            number (str): a number to convert to binary representation.

        Returns:
            str: 16-bit long binary code of the given number.
        """
        new_line = bin(int(number))[2:]
        zeros_to_add = Code.BIT_LENGTH - len(new_line)
        new_line = (Code.ZERO * zeros_to_add) + new_line
        return new_line

    @staticmethod
    def write_line(infile: Parser, table: SymbolTable) -> str:
        """
        Args:
            infile (Parser): a command file to transform to binary.
            table (SymbolTable) : a table containing all the symbols already encountered

        Returns:
            str: 16-bit long binary code of the given command.
        """
        command = infile.command_type()
        if command == Parser.L_COMMAND:
            return Parser.EMPTY_STRING
        if command == Parser.A_COMMAND:
            return Code.a_command(infile.symbol(), table)
        else:
            return Code.comp(infile.comp()) + Code.dest(infile.dest()) + Code.jump(infile.jump())

    @staticmethod
    def a_command(symbol: str, table: SymbolTable) -> str:
        """ adds the symbol to the symbol table if needed and returns the number in 16-bit binary
        Args:
            symbol (str): a number file to transform to binary.
            table (SymbolTable) : a table containing all the symbols already encountered

        Returns:
            str: 16-bit long binary code of the given number.
        """
        if symbol.isnumeric():
            return Code.calc_binary(int(symbol))
        if not table.contains(symbol):
            table.add_entry(symbol, table.get_counter())
            table.increase()
            return Code.calc_binary(table.get_address(symbol))
        else:
            return Code.calc_binary(table.get_address(symbol))
