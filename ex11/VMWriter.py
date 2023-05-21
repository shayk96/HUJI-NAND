"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class VMWriter:
    """
    Writes VM commands into a file. Encapsulates the VM command syntax.
    """

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Creates a new file and prepares it for writing VM commands."""
        self.__out = output_stream

    def write_push(self, segment: str, index: int) -> None:
        """Writes a VM push command.

        Args:
            segment (str): the segment to push to, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"
            index (int): the index to push to.
        """
        if segment == "field":
            segment = "this"
        if segment == "var":
            segment = "local"
        self.__out.write("push " + segment + " " + str(index) + "\n")

    def write_pop(self, segment: str, index: int) -> None:
        """Writes a VM pop command.

        Args:
            segment (str): the segment to pop from, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP".
            index (int): the index to pop from.
        """
        if segment == "var":
            segment = "local"
        if segment == "field":
            segment = "this"
        self.__out.write("pop " + segment + " " + str(index) + "\n")

    def write_arithmetic(self, command: str) -> None:
        """Writes a VM arithmetic command.

        Args:
            command (str): the command to write, can be "add", "sub", "neg",
            "eq", "gt", "lt", "and", "or", "not".
        """
        self.__out.write(command + "\n")

    def write_label(self, label_name: str, counter: int) -> None:
        """Writes a VM label command.

        Args:
            counter: The index of the label command
            label_name (str): the label to write.
        """
        self.__out.write("label " + label_name + str(counter) + "\n")

    def write_goto(self, label: str, counter: int) -> None:
        """Writes a VM goto command.

        Args:
            counter: The index of the label command
            label (str): the label to go to.
        """
        self.__out.write("goto " + label + str(counter) + "\n")

    def write_if(self, label: str, counter: int) -> None:
        """Writes a VM if-goto command.

        Args:
            counter: The index of the label command
            label (str): the label to go to.
        """
        self.__out.write("if-goto " + label + str(counter) + "\n")

    def write_call(self, name: str, n_args: int) -> None:
        """Writes a VM call command.

        Args:
            name (str): the name of the function to call.
            n_args (int): the number of arguments the function receives.
        """
        self.__out.write("call " + name + " " + str(n_args) + "\n")

    def write_function(self, name: str, n_locals: int) -> None:
        """Writes a VM function command.

        Args:
            name (str): the name of the function.
            n_locals (int): the number of local variables the function uses.
        """
        self.__out.write("function " + name + " " + str(n_locals) + "\n")

    def write_return(self) -> None:
        """Writes a VM return command."""
        self.__out.write("return" + "\n")
