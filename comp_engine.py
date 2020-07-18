from vw_write import vm_writer

# class for storing all tokens from code. Stored in this module to prevent issues with circular imports
class token:
    def __init__(self, type, value, xml_out):
        self.xml_out = xml_out
        self.type = type
        self.value = value

# class that defines the recursive parsing tree
class comp_engine:
    def __init__(self,t_list, class_name):
        self.class_name = class_name
        self.t_list = t_list
        self.parsed_list = []
        self.t_count = 0 # tracks current token location

    def add_token(self):
        self.parsed_list.append(self.t_list[self.t_count].xml_out)
        self.t_count += 1

    def new_class(self):
        vm_code = vm_writer() #contstructs vm code list

        # structured: 'class' className '{' classVarDec* subrountineDec* '}'
        self.parsed_list.append('<class>')
        self.add_token() # class
        self.add_token() # className
        self.add_token() # {

        while self.t_list[self.t_count].value in ['static', 'field']:
            self.classVarDec() # classVarDec method
        while self.t_list[self.t_count].value in ['constructor', 'function', 'method']:
            self.subroutineDec() #subroutineDec method

        self.parsed_list.append(self.t_list[self.t_count].xml_out) # }

        self.parsed_list.append('</class>')

    def classVarDec(self):
        # structured: 'static'|'field' type varName (',' varName)* ';'
        self.parsed_list.append('<classVarDec>')
        self.add_token() # static|field
        self.add_token() # type
        self.add_token() # varName

        while self.t_list[self.t_count].value == ',': # checks for additional variable declarations
            self.add_token() # ,
            self.add_token() # varName
        self.add_token() # ;

        self.parsed_list.append('</classVarDec>')

    def subroutineDec(self):
        # structured: 'constructor'|'function'|'method' 'void'|type subroutineName '(' parameterList ')' subroutineBody
        self.parsed_list.append('<subroutineDec>')

        self.add_token() # constructor|function|method
        self.add_token() # 'void'|type
        self.add_token() # subroutineName
        self.add_token() # (
        self.parameterList() #parameterList method
        self.add_token() # )
        self.subroutineBody() #subroutineBody method

        self.parsed_list.append('</subroutineDec>')

    def parameterList(self):
        # structured: ((type VarName) (',' type varName)*)?
        self.parsed_list.append('<ParameterList>')

        # checks for first parameter
        if self.t_list[self.t_count].value != ')':
            self.add_token() # type
            self.add_token() # varName

        # checks for any additional parameters
        while self.t_list[self.t_count].value == ',':
            self.add_token() # ,
            self.add_token() # type
            self.add_token() # varName

        self.parsed_list.append('</ParameterList>')

    def subroutineBody(self):
        # structured: '{' varDec* statements '}'
        self.parsed_list.append('<subroutineBody>')

        self.add_token() # {

        #checks for all variable declarations
        while self.t_list[self.t_count].value == 'var':
            self.varDec() # varDec method

        self.statements() # statements method
        self.add_token() # }

        self.parsed_list.append('</subroutineBody>')

    def varDec(self):
        # structured: 'var' type varName (',' varName)*';'
        self.parsed_list.append('<varDec>')

        self.add_token() # var
        self.add_token() # type
        self.add_token() # varName

        # checks for any additional variable declarations in same line
        while self.t_list[self.t_count].value == ',':
            self.add_token() # ,
            self.add_token() # varName
        self.add_token() # ;

        self.parsed_list.append('</varDec>')

    def statements(self):
        # structured: (letStatement|ifStatement|whileStatement|doStatement|returnStatement)*
        self.parsed_list.append('<statements>')

        # checks for any additional statements
        while self.t_list[self.t_count].value in ['let','if','while','do','return']:
            if self.t_list[self.t_count].value == 'let':
                self.letStatement() # letStatement method
                continue
            if self.t_list[self.t_count].value == 'if':
                self.ifStatement() # ifStatement method
                continue
            if self.t_list[self.t_count].value == 'while':
                self.whileStatement() # whileStatement method
                continue
            if self.t_list[self.t_count].value == 'do':
                self.doStatement() # doStatement method
                continue
            if self.t_list[self.t_count].value == 'return':
                self.returnStatement() # returnStatement method
                continue

        self.parsed_list.append('</statements>')

    def letStatement(self):
        # structured: 'let' varName ('['expression']')? '=' expression ';'
        self.parsed_list.append('<letStatement>')

        self.add_token() # let
        self.add_token() # varName

        #checks if variable is an array
        if self.t_list[self.t_count].value == '[':
            self.add_token() # [
            self.expression() # expression method
            self.add_token() # ]

        self.add_token() # =
        self.expression() # expression method
        self.add_token() # ;

        self.parsed_list.append('</letStatement>')

    def ifStatement(self):
        # structured: 'if' '('expression')' '{'statements'}' ('else' '{'statements'}')?
        self.parsed_list.append('<ifStatement>')

        self.add_token() # if
        self.add_token() # (
        self.expression() # expression method
        self.add_token() # )
        self.add_token() # {
        self.statements() # statements method
        self.add_token() # }

        #checks for else statement
        if self.t_list[self.t_count].value == 'else':
            self.add_token() # else
            self.add_token() # {
            self.statements() # statements method
            self.add_token() # }

        self.parsed_list.append('</ifStatement>')

    def whileStatement(self):
        # structured: 'while' '('expression')' '{'statements'}'
        self.parsed_list.append('<whileStatement>')

        self.add_token() # while
        self.add_token() # (
        self.expression() # expression method
        self.add_token() # )
        self.add_token() # {
        self.statements() # statements method
        self.add_token() # }

        self.parsed_list.append('</whileStatement>')

    def doStatement(self):
        # structured: 'do' subroutineName '('expressionList')'| (className|varName)'.' subroutineName '('expressionList')' ';'
        self.parsed_list.append('<doStatement>')

        self.add_token() # do
        self.add_token() # subroutineName|(className|varName)

        #checks if subroutine call is calling method from another class/variable
        if self.t_list[self.t_count].value == '.':
            self.add_token() # .
            self.add_token() # subroutineName

        self.add_token() # (
        self.expressionList() # expressionList method
        self.add_token() # )
        self.add_token() # ;

        self.parsed_list.append('</doStatement>')

    def returnStatement(self):
        # structured: 'return' expression? ';'
        self.parsed_list.append('<returnStatement>')

        self.add_token() # return

        # checks if there is a return value
        if self.t_list[self.t_count].value != ';':
            self.expression() #expression method

        self.add_token() # ;

        self.parsed_list.append('</returnStatement>')

    def expressionList(self):
        # structured: (expression (',' expression)* )?
        self.parsed_list.append('<expressionList>')

        # checks for first expression
        if self.t_list[self.t_count].value != ')':
            self.expression() #expression method

        # checks for any additional expressions
        while self.t_list[self.t_count].value != ')':
            self.add_token() # ,
            self.expression() #expression method

        self.parsed_list.append('</expressionList>')

    def expression(self):
        # structured: (term (op term)*
        self.parsed_list.append('<expression>')

        self.term() # term method

        #checks for any operations followed by additional terms
        while self.t_list[self.t_count].value in ['+','-','*','/','&amp;','|','&lt;','&gt;','=']:
            self.add_token() # op
            self.term() # term method

        self.parsed_list.append('</expression>')

    def term(self):
        # structured: integerConstant|stringConstant|keywordConstant|varName|varName'['expression']'|subroutineCall|'('expression')'|unaryOp term
        self.parsed_list.append('<term>')

        self.add_token() # first token of the term

        #checks if term is a subroutineCall
        if (self.t_list[self.t_count - 1].type == 'identifier') and (self.t_list[self.t_count].value in ['(','.']):

            #checks if subroutine call is calling method from another class/variable
            if self.t_list[self.t_count].value == '.':
                self.add_token() # .
                self.add_token() # subroutineName

            self.add_token() # (
            self.expressionList() # expressionList method
            self.add_token() # )

        #checks if term is array value
        elif self.t_list[self.t_count].value == '[':
            self.add_token() # [
            self.expression() # expression method
            self.add_token() # ]

        # checks is term is an (expression)
        elif self.t_list[self.t_count - 1].value == '(':
            self.expression() # expression method
            self.add_token() # )

        # checks is term is an unaryOp
        elif self.t_list[self.t_count - 1].value in ['-','~']:
            self.term() # term method

        self.parsed_list.append('</term>')