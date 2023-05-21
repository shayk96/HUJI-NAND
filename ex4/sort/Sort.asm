// This file is part of nand2tetris, as taught in The Hebrew University,
// and was written by Aviv Yaish, and is published under the Creative 
// Common Attribution-NonCommercial-ShareAlike 3.0 Unported License 
// https://creativecommons.org/licenses/by-nc-sa/3.0/

// An implementation of a sorting algorithm. 
// An array is given in R14 and R15, where R14 contains the start address of the 
// array, and R15 contains the length of the array. 
// You are not allowed to change R14, R15.
// The program should sort the array in-place and in descending order - 
// the largest number at the head of the array.
// You can assume that each array value x is between -16384 < x < 16384.
// You can assume that the address in R14 is at least >= 2048, and that 
// R14 + R15 <= 16383. 
// No other assumptions can be made about the length of the array.
// You can implement any sorting algorithm as long as its runtime complexity is 
// at most C*O(N^2), like bubble-sort. 


@i
M=0
(1_LOOP)
    @j
    M=0
    @R15 //arr len
    D=M
    @i
    D=D-M
    D=D-1
    @END
    D;JEQ
    (2_LOOP) // compares between adjacent values
        @j
        D=M
        @R14
        D=D+M
        @first_adr
        M=D
        @second_adr
        M=D+1
        A=M
        D=M
        @first_adr
        A=M
        D=D-M
        @SWAP
        D;JGT
    (BACK)
        @R15
        D=M
        @i
        D=D-M
        D=D-1
        D=D-1
        @j
        D=D-M
        M=M+1
        @2_LOOP // if not final value in the loop
        D;JGT
        @i
        M=M+1
        @1_LOOP // if passed all the values 
        0;JMP
(SWAP) // swaps
    @first_adr
    A=M
    D=M
    @second_adr
    A=M
    MD=D+M
    @first_adr
    A=M
    MD=D-M
    @second_adr
    A=M
    M=M-D
    @BACK // back to the second loop
    0;JMP
(END) // infint loop
    @END
    0;JMP