# Jack-Compiler
Compiles Jack source code into VM code using Python

Input: .jack code file from local directory or local directory containing .jack files
Outputs: .vm file for each .jack file input (one file for each jack class)

Jack code is an OOL, similar to a simplified Java. VM code is similar to Java bytecode. Compiler architecture based generally on Nand2Tetris book

Modules:

Compiler - main module that takes input in command line and writes the .vm files. Calls tokenizer and compile_engine

Tokenizer - transforms raw code into a list of tokens for feeding into the compile_engine

Compile_engine - heft of the program. takes token list and parses the syntax. Then uses vm_write to turn parsed code into VM code

Symbols - used by compile_engine to store and read variables and subroutine details

vm_write - simple module used by comp_engine to write and store vm_code for each class

