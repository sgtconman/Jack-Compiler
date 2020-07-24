import re

# module used by compiler for defining token class and turning Jack code into token list.

class token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

def tokenize(raw_code):

    #removes comments and newlines
    cleaned_code = re.sub('/\*.*?\*/','', raw_code, flags=re.DOTALL) #removes block comments denoted with /*  *\
    cleaned_code = re.sub('//.*','', cleaned_code) #removes in-line comments denoted with //
    cleaned_code = re.sub('\\n',' ', cleaned_code) #removes linux newlines
    cleaned_code = re.sub('\\r\\n',' ', cleaned_code) #removes windows newlines

    # creates regular expression objects to match Jack tokens
    symbol_pattern = re.compile('[\{\}\(\)\[\]\.\,\;\+\-\*\/\&\|\<\>\=\~]')
    string_pattern = re.compile('\".*?\"')
    var_pattern = re.compile('[a-zA-Z_][a-zA-Z0-9_]*')
    int_pattern = re.compile('[0-9]+')

    # used to determine in alphanumeric pattern is a keyword
    keyword_list = ['class' , 'constructor' , 'function' , 'method' , 'field' , 'static' , 'var' , 'int' ,
    'char' , 'boolean' , 'void' , 'true' , 'false' , 'null' , 'this' , 'let' , 'do' , 'if' , 'else' , 'while' , 'return']


    # initializes variables needed for tokenizing. i is char tracker
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
            buffer = buffer.replace('&', '&amp;')
            buffer = buffer.replace('<', '&lt;')
            buffer = buffer.replace('>', '&gt;')
            buffer = buffer.replace('\"', '&quot;')
            type = 'symbol'
            token_list.append(token(type, buffer))
            continue

        match = string_pattern.match(cleaned_code, i)
        if match:
            buffer = match.group()
            i = i + len(buffer)
            buffer = buffer.strip('"')
            type = 'stringConstant'
            token_list.append(token(type, buffer))
            continue

        match = var_pattern.match(cleaned_code, i)
        if match:
            buffer = match.group()
            i = i + len(buffer)
            if buffer in keyword_list:
                type = 'keyword'
            else:
                type = 'identifier'
            token_list.append(token(type, buffer))
            continue

        match = int_pattern.match(cleaned_code, i)
        if match:
            buffer = match.group()
            i = i + len(buffer)
            type = 'integerConstant'
            token_list.append(token(type, buffer))
            continue

        i += 1 # I do not fully understand why I need this line but without it sometimes loops infinitely in unexplainable ways

    return token_list
