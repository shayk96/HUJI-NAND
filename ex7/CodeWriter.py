import typing

from Parser import Parser

INC_AND_LOAD_SP = "@SP\nAM=M+1\nA=A-1\nM=D\n"

ADD_SUB = "@SP  //{comment}\nAM=M-1\nD=M\nA=A-1\nM=M{sign}D\n"

NEG_NOT = "@SP  //{comment}\nA=M-1\nM={sign}M\n"

EQ_GT_LT = "@SP  //{comment}\nAM=M-1\nD=M\n@SECPOS{counter}\nD;JGE\n@SECNEG{counter}\n0;JMP\n" \
           "(SECPOS{counter})\n@R13\nM=1\n@SP\nAM=M-1\nD=M\n@SAMESIGN{counter}\nD;JGE\n@NOTSAME{counter}\n0;JMP\n" \
           "(SECNEG{counter})\n@R13\nM=-1\n@SP\nAM=M-1\nD=M\n@SAMESIGN{counter}\nD;JLE\n@NOTSAME{counter}\n0;JMP\n" \
           "(SAMESIGN{counter})\n@SP\nA=M\nD=M\nA=A+1\nD=D-M\n@ISTRUE{counter}\nD;{jmp_type}\n@ISFALSE{counter}\n" \
           "0;JMP\n(NOTSAME{counter})\n@R13\nD=M\n@ISFALSE{counter}\nD;{jmp_type}\n@ISTRUE{counter}\n0;JMP\n" \
           "(ISTRUE{counter})\n@SP\nM=M+1\nA=M-1\nM=-1\n@END{counter}\n0;JMP\n" \
           "(ISFALSE{counter})\n@SP\nM=M+1\nA=M-1\nM=0\n(END{counter})\n"

AND_OR = "@SP  //{comment}\nAM=M-1\nD=M\nA=A-1\nM=M{sign}D\n"

SHIFT = "@SP  //{comment}\nA=M-1\nM=M{sign}\n"

PUSH_DIC_COMMANDS = "@{param1}  //{comment} {param2}\nD={register}\n@{param2}\nA=D+A\nD=M\n" + INC_AND_LOAD_SP

STATIC_PUSH = "@{filename}.{index}  //{comment}\nD=M\n" + INC_AND_LOAD_SP

CONSTANT_PUSH = "@{index}  //{comment} {index}\nD=A\n@SP\nM=M+1\nA=M-1\nM=D\n"

STATIC_POP = "@SP  //{comment} {filename}.{index}\nAM=M-1\nD=M\n@{filename}.{index}\nM=D\n"

POP_DIC_COMMANDS = "@{segment}  //{comment} {index}\nD={register}\n@{index}\nD=D+A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n" \
                   "@R13\nA=M\nM=D\n"

LABEL_COMMAND = "({label}) // C_LABEL\n"

GOTO_COMMAND = "@{label} // C_GOTO\n0;JMP\n"

IF_GOTO_COMMAND = "@SP //C_IF\nAM=M-1\nD=M\n@{label}\nD;JNE\n"

FUNCTION_COMMAND = "({function_name})  //C_FUNCTION\n@{num_vars}\nD=A\n@args_remaining{loop_counter}\nMD=D-1\n" \
                   "@ZEROARGS{loop_counter}\nD;JLE\n(LOOP{loop_counter})\n@SP\nAM=M+1\nA=A-1\nM=0\n" \
                   "@args_remaining{loop_counter}\nMD=M-1\n@LOOP{loop_counter}\nD;JGE\n(ZEROARGS{loop_counter})\n"

SET_ARG_LCL_CALLEE = "@{num_vars}\nD=A\n@5\nD=D+A\n@SP\nD=M-D\n@ARG\nM=D\n@SP\nD=M\n@LCL\nM=D\n"

CALL_COMMAND = "@{function_name}$retAddr{counter}  //C_CALL {function_name}\nD=A\n" + INC_AND_LOAD_SP + \
               "@LCL\nD=M\n" + INC_AND_LOAD_SP + \
               "@ARG\nD=M\n" + INC_AND_LOAD_SP + \
               "@THIS\nD=M\n" + INC_AND_LOAD_SP + \
               "@THAT\nD=M\n" + INC_AND_LOAD_SP + SET_ARG_LCL_CALLEE + \
               "@{function_name}\n0;JMP\n({function_name}$retAddr{counter})\n"

NULL = "null"

INIT_SP = "@256 //bootstrap \nD=A\n@SP\nM=D\n"

RESTORE_MEM_SEG = "@endFrame\nMD=M-1\nA=D\nD=M\n@{segment}\nM=D\n"

CALC_ENDFRAME_AND_RETADDER = "@LCL //C_RETURN\nD=M\n@endFrame\nM=D\n@5\nA=D-A\nD=M\n@retAdder\n" \
                             "M=D // inside return function\n"


def add_sub(comment: str, sign: str) -> str:
    return ADD_SUB.format(comment=comment, sign=sign)


def neg_not(comment: str, sign: str) -> str:
    return NEG_NOT.format(comment=comment, sign=sign)


def eq_gt_lt(comment: str, counter: int, jmp_type: str, ) -> str:
    return EQ_GT_LT.format(comment=comment, counter=counter, jmp_type=jmp_type)


def and_or(comment: str, sign: str) -> str:
    return AND_OR.format(comment=comment, sign=sign)


def shift(comment: str, sign: str) -> str:
    return SHIFT.format(comment=comment, sign=sign)


def write_push_from_dics(comment: str, param1: str, register: str, param2: str) -> str:
    return PUSH_DIC_COMMANDS.format(comment=comment, param1=param1, register=register, param2=param2)


def write_static_push(comment: str, filename: str, index: int) -> str:
    return STATIC_PUSH.format(comment=comment, filename=filename, index=index)


def write_constant_push(comment: str, index: int) -> str:
    return CONSTANT_PUSH.format(comment=comment, index=index)


def write_static_pop(comment: str, filename: str, index: int) -> str:
    return STATIC_POP.format(comment=comment, filename=filename, index=index)


def write_pop_from_dics(comment: str, param1: str, register: str, param2: str) -> str:
    return POP_DIC_COMMANDS.format(comment=comment, segment=param1, register=register, index=param2)


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    SEGMENTS_BASES = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
    SEGMENTS_ADDRESS = {"temp": "R5", "pointer": "R3"}

    comp_counter = 0
    loop_counter = 0  # per function
    call_counter = 0

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.__output_stream = output_stream
        self.__filename = None
        self.__func_name = NULL

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.__filename = filename

    def set_func_name(self, func_name: str) -> None:
        self.__func_name = func_name

    def writeInit(self) -> None:
        self.__output_stream.write(INIT_SP)
        self.write_call("Sys.init", "0", "")

    def label_format(self, label: str) -> str:
        return self.__func_name + "." + label

    def write_label(self, label: str, counter: str) -> None:
        self.__output_stream.write(LABEL_COMMAND.format(label=label, counter=counter))

    def write_goto(self, label: str) -> None:
        self.__output_stream.write(GOTO_COMMAND.format(label=label))

    def write_if(self, label: str, counter: str) -> None:
        self.__output_stream.write(IF_GOTO_COMMAND.format(label=label, counter=counter))

    def write_function(self, function_name: str, num_vars: str, loop_counter: str) -> None:
        self.__output_stream.write(
            FUNCTION_COMMAND.format(function_name=function_name, num_vars=num_vars, loop_counter=loop_counter))

    def write_call(self, function_name: str, num_vars: str, counter: str) -> None:
        self.__output_stream.write(CALL_COMMAND.format(function_name=function_name, num_vars=num_vars, counter=counter))

    def write_return(self):
        self.__output_stream.write(CALC_ENDFRAME_AND_RETADDER)
        self.write_push_pop("C_POP", "argument", 0)
        self.__output_stream.write("@ARG\nD=M+1\n@SP\nM=D\n" +
                                   RESTORE_MEM_SEG.format(segment="THAT") +
                                   RESTORE_MEM_SEG.format(segment="THIS") +
                                   RESTORE_MEM_SEG.format(segment="ARG") +
                                   RESTORE_MEM_SEG.format(segment="LCL") +
                                   "@retAdder\nA=M\n0;JMP\n")

    def write_line(self, infile: Parser) -> None:
        command = infile.command_type()
        if command == "C_RETURN":
            return self.write_return()
        arg1 = infile.arg1()
        if command == Parser.C_ARITHMETIC:
            return self.write_arithmetic(arg1)
        if command in ["C_PUSH", "C_POP"]:
            return self.write_push_pop(command, arg1, infile.arg2())
        if command == "C_LABEL":
            self.write_label(arg1, "")
        if command == "C_IF":
            self.write_if(arg1, "")
        if command == "C_FUNCTION":
            self.write_function(arg1, str(infile.arg2()), str(CodeWriter.loop_counter))
            CodeWriter.loop_counter += 1
        if command == "C_GOTO":
            self.write_goto(arg1)
        if command == "C_CALL":
            self.write_call(arg1, str(infile.arg2()), str(CodeWriter.call_counter))
            CodeWriter.call_counter += 1

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        if command in ["eq", "gt", "lt"]:
            CodeWriter.comp_counter += 1

        arithmetic_functions = {"add": add_sub("add", "+"),
                                "sub": add_sub("sub", "-"),
                                "neg": neg_not("neg", "-"),
                                "not": neg_not("not", "!"),
                                "eq": eq_gt_lt("eq", CodeWriter.comp_counter, "JEQ"),
                                "gt": eq_gt_lt("gt", CodeWriter.comp_counter, "JGT"),
                                "lt": eq_gt_lt("lt", CodeWriter.comp_counter, "JLT"),
                                "and": and_or("and", "&"),
                                "or": and_or("or", "|"),
                                "shiftleft": shift("shiftleft", "<<"),
                                "shiftright": shift("shiftright", ">>")}

        self.__output_stream.write(arithmetic_functions[command])

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        comment = command + " " + segment
        if command == "C_PUSH":
            if segment == "constant":
                line_to_write = write_constant_push(comment, index)
            if segment == "static":
                line_to_write = write_static_push(comment, self.__filename, index)
            if segment in CodeWriter.SEGMENTS_BASES:
                line_to_write = write_push_from_dics(comment, CodeWriter.SEGMENTS_BASES[segment], "M", str(index))
            if segment in CodeWriter.SEGMENTS_ADDRESS:
                line_to_write = write_push_from_dics(comment, str(index), "A", CodeWriter.SEGMENTS_ADDRESS[segment])
        if command == "C_POP":
            if segment == "static":
                line_to_write = write_static_pop(comment, self.__filename, index)
            if segment in CodeWriter.SEGMENTS_BASES:
                line_to_write = write_pop_from_dics(comment, CodeWriter.SEGMENTS_BASES[segment], "M", str(index))
            if segment in CodeWriter.SEGMENTS_ADDRESS:
                line_to_write = write_pop_from_dics(comment, str(index), "A", CodeWriter.SEGMENTS_ADDRESS[segment])
        self.__output_stream.write(line_to_write)

    def close(self) -> None:
        """Closes the output file."""
        self.__output_stream.close()
