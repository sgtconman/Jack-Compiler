import sys
import os
import glob
import re


symbol_list = ['{' , '}' , '(' , ')' , '[' , ']' , '. ' , ', ' , '; ' , '+' , '-' , '*' ,
'/' , '&' , '|' , '<' , '>' , '=' , '~’']

keyword_list = ['class' , 'constructor' , 'function' , 'method' , 'field' , 'static' , 'var' , 'int' ,
'char' , 'boolean' , 'void' , 'true' , 'false' , 'null' , 'this' , 'let' , 'do' , 'if' , 'else' , 'while' , 'return']

# class for storing all tokens from code
class token:
    def __init__(self,type, value, xml_out):
        self.xml_out = xml_out
        self.type = type
        self.value = value


def main():

    if len(sys.argv) != 2:
        sys.exit("input 1 argument: [program].jack or Jack file directory")

    #determines if command line input is file or directory and puts .jack file names in a list
    jack_files = []
    if os.path.isdir(sys.argv[1]):
        dir_path = sys.argv[1]
        jack_files = glob.glob(dir_path + "/*.jack")
    else:
        jack_files.append(sys.argv[1])

    for file in jack_files:

        jack_file = open(file, 'r')
        jack_code = jack_file.read()
        jack_file.close()

        # cleans code and writes each token into list of token objects
        token_list = tokenizer(jack_code)

        # temp code to print tokens xml file
        token_code = []
        token_code.append('<tokens>\n')
        for t in token_list:
            token_code.append(t.xml_out + '\n')
        token_code.append('</tokens>\n')

        # creates .xml output file and opens for writing
        xml_file_name = file.strip(".jack") + ".xml"
        xml_file = open(xml_file_name, 'w')

        # writes translated code to output file
        xml_file.writelines(token_code)
        xml_file.close()


def tokenizer(raw_code):

    #removes comments and newlines
    cleaned_code = re.sub('/\*.*?\*/','', raw_code, flags=re.DOTALL) #removes block comments denoted with /*  *\
    cleaned_code = re.sub('//.*','', cleaned_code) #removes in-line comments denoted with //
    cleaned_code = re.sub('\\n',' ', cleaned_code) #removes newlines

    # creates regular expression objects to mathc Jack tokens
    symbol_pattern = re.compile('[\{\}\(\)\[\]\.\,\;\+\-\*\/\&\|\<\>\=\~]')
    string_pattern = re.compile('\".*?\"')
    var_pattern = re.compile('[a-zA-Z_][a-zA-Z0-9_]*')
    int_pattern = re.compile('[0-9]')

    # initializes variables needed for tokenizing
    token_list = []
    type = ''
    buffer = ''
    match = ''
    i = 0

    # loops through each character of code attempting to match to one of the token patterns
    # when token is found, creates new token object and advances character count(i) by number of characters in token
    while i < len(cleaned_code):

        if cleaned_code[i] == ' ':
            i += 1
            continue

        match = symbol_pattern.match(cleaned_code, i)
        if match:
            buffer = match.group()
            i = i + len(buffer)

            # below specific symbols need to be replaced per Jack specification
            buffer = buffer.replace('<', '&lt;')
            buffer = buffer.replace('>', '&gt;')
            buffer = buffer.replace('\"', '&quot;')
            buffer = buffer.replace('<&', '&amp;')

            type = 'symbol'
            xml_temp = "<" + type + "> " + buffer + " </" + type + ">"
            token_list.append(token(type, buffer, xml_temp))
            continue

        match = string_pattern.match(cleaned_code, i)
        if match:
            buffer = match.group()
            i = i + len(buffer)
            buffer = buffer.strip('"')
            type = 'stringConstant'
            xml_temp = "<" + type + "> " + buffer + " </" + type + ">"
            token_list.append(token(type, buffer, xml_temp))
            continue

        match = var_pattern.match(cleaned_code, i)
        if match:
            buffer = match.group()
            i = i + len(buffer)
            if buffer in keyword_list:
                type = 'keyword'
            else:
                type = 'identifier'

            xml_temp = "<" + type + "> " + buffer + " </" + type + ">"
            token_list.append(token(type, buffer, xml_temp))
            continue

        match = int_pattern.match(cleaned_code, i)
        if match:
            buffer = match.group()
            i = i + len(buffer)
            type = 'integerConstant'
            xml_temp = "<" + type + "> " + buffer + " </" + type + ">"
            token_list.append(token(type, buffer, xml_temp))
            continue

        i += 1 # I do not fully understand why I need this line but without it sometimes loops infinitely in unexplainable ways

    return token_list

main()