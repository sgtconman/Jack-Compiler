import sys
import os
import glob
from comp_engine import *
from tokenizer import tokenize

def main():

    #checks for valid input and adds Jack filenames to list
    jack_files = initializer(sys.argv)

    for file in jack_files:

        jack_file = open(file, 'r')
        jack_code = jack_file.read()
        jack_file.close()

        # cleans code and writes each token into list of token objects (as defined in the tokenizer module`)
        token_list = tokenize(jack_code)

        #creates comp_engine object (as defined in the comp_engine module). This does lions share of turning tokens into compiled VM code
        class_path = file.strip('.jack')
        class_name = class_path.split('/')[-1]
        engine = comp_engine(token_list, class_name)
        engine.new_class()

        vm_code = engine.vm_code.code_list
        for i in range(len(vm_code)):
            vm_code[i] = vm_code[i] + '\n'

        # creates .vm output file and opens for writing
        vm_file_name = class_path + ".vm"
        vm_file = open(vm_file_name, 'w')

        # writes translated code to vm output file
        vm_file.writelines(vm_code)
        vm_file.close()
        print('Compilation Successful')

def initializer(cmd_args):

    if len(cmd_args) != 2:
        sys.exit("input 1 argument: [program].jack or Jack file directory")

    #determines if command line input is file or directory and puts .jack file names in a list
    jack_files = []
    if os.path.isdir(sys.argv[1]):
        dir_path = sys.argv[1]
        jack_files = glob.glob(dir_path + "/*.jack")
    else:
        jack_files.append(sys.argv[1])

    return jack_files


main()