"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing

from Code import Code
from Parser import Parser
from SymbolTable import SymbolTable

BREAK_LINE = "\n"
USAGE_ERROR = "Invalid usage, please use: Assembler <input path>"


def assemble_file(input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    table = SymbolTable()
    infile = Parser(input_file)
    lines = infile.get_lines()
    jmp_counter = 0
    for line in lines:
        if line[0] == Parser.L_BRACE:
            if not table.contains(line[1:-1]):
                table.add_entry(line[1:-1], jmp_counter)
                continue
        jmp_counter += 1

    while infile.has_more_commands():
        line_to_write = Code.write_line(infile, table)
        if line_to_write != Parser.EMPTY_STRING:
            output_file.write(line_to_write + BREAK_LINE)
        infile.advance()
    output_file.write(Code.write_line(infile, table))


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit(USAGE_ERROR)
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
