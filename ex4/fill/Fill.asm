// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.


@8192
D=A
@R0 //max i
M=D
@R1 // state
M=0
@i
M=0

(K_LOOP)
    @KBD
    D=M
    @R1
    D=D-M
    @K_LOOP
    D;JEQ
    @B_LOOP
    D;JGT
    @W_LOOP
    D;JLT

(B_LOOP)
    @SCREEN
    D=A
    @i
    D=D+M
    A=D
    M=-1
    @i
    M=M+1
    D=M
    @R0
    D=M-D
    @B_LOOP
    D;JGT
    @R1
    M=1
    @i
    M=0
    @K_LOOP
    0;JMP

(W_LOOP)
    @SCREEN
    D=A
    @i
    D=D+M
    A=D
    M=0
    @i
    M=M+1
    D=M
    @R0
    D=M-D
    @W_LOOP
    D;JGT
    @R1
    M=1
    @i
    M=0
    @K_LOOP
    0;JMP 

