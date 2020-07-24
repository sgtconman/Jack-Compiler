from vm_write import vm_writer
from symbols import symbol_table
import tokenizer

# class that defines the recursive parsing tree
class comp_engine:

    def __init__(self,t_list, class_name):
        self.class_name = class_name
        self.t_list = t_list
        self.t_count = 0 # tracks current token location
        self.vm_code = vm_writer() #constructs vm code list
        self.symb_table = symbol_table() #constructs new symbol table
        self.label_count = 0 #tracks number of labels for the unique label generator

    def consume_token(self):
        self.t_count += 1

    def current_token(self):
        return self.t_list[self.t_count].value

    def label_generator(self):
        label = '$$flow_label$$' + str(self.label_count)
        self.label_count += 1
        return label

    def new_class(self):
        # structured: 'class' className '{' classVarDec* subrountineDec* '}'

        self.consume_token() # class
        self.consume_token() # className
        self.consume_token() # {

        while self.current_token() in ['static', 'field']:
            self.classVarDec() # classVarDec
        while self.current_token() in ['constructor', 'function', 'method']:
            self.subroutineDec() #subroutineDec method


    def classVarDec(self):
        # structured: 'static'|'field' type varName (',' varName)* ';'

        var_kind = self.current_token() # static|field
        self.consume_token() # static|field
        var_type = self.current_token() #type
        self.consume_token() # type
        var_name = self.current_token() #varName
        self.consume_token() # varName
        self.symb_table.define(var_name, var_type, var_kind)

        while self.t_list[self.t_count].value == ',': # checks for additional variable declarations
            self.consume_token() # ,
            var_name = self.current_token() #varName
            self.consume_token() # varName
            self.symb_table.define(var_name, var_type, var_kind)
        self.consume_token() # ;


    def subroutineDec(self):
        # structured: 'constructor'|'function'|'method' 'void'|type subroutineName '(' parameterList ')' subroutineBody

        self.symb_table.start_subroutine() #resets subroutine level symbol table

        if self.current_token() == 'constructor':
            self.consume_token() # constructor
            self.consume_token() # type
            f_name = self.current_token() # subroutineName
            self.vm_code.write_function(f_name, self.class_name, 0)
            self.consume_token() # subroutineName

            field_count = self.symb_table.varcount('field')
            self.vm_code.write_push('constant', field_count) # indicates amount of memory needed for object
            self.vm_code.write_call('Memory.alloc', 1) #uses OS to allocate needed memory block
            self.vm_code.write_pop('pointer', 0) # pops memory address into THIS pointer

            self.consume_token() # (
            self.parameterList() #parameterList method
            self.consume_token() # )
            method_check = False
            self.subroutineBody(f_name, method_check) #subroutineBody method

            self.vm_code.write_return() # return

        elif self.current_token() in ['function', 'method']:
            if self.current_token() == 'method':
                method_check = True
                self.symb_table.define('this', 'object', 'arg') #adds THIS as arg 0 to symbol table
            else:
                method_check = False
            self.consume_token() # function | method
            void_check = False
            if self.current_token() == 'void':
                void_check = True
            self.consume_token() # 'void'|type

            f_name = self.current_token() # subroutineName
            self.consume_token() # subroutineName
            self.consume_token() # (
            self.parameterList() #parameterList method
            self.consume_token() # )
            self.subroutineBody(f_name, method_check) #subroutineBody method

            if void_check == True:
                self.vm_code.write_push('constant', 0)
            self.vm_code.write_return() # writes return statement here, as it comes after pushing dummy value for void return
        elif self.current_token() == 'method':
            return


    def parameterList(self):
        # structured: ((type VarName) (',' type varName)*)?

        # checks for first parameter
        if self.current_token() != ')':
            var_type = self.current_token() #type
            self.consume_token() # type
            var_name = self.current_token() #varName
            self.consume_token() # varName
            self.symb_table.define(var_name, var_type, 'arg')

        # checks for any additional parameters
        while self.t_list[self.t_count].value == ',':
            self.consume_token() # ,
            var_type = self.current_token() #type
            self.consume_token() # type
            var_name = self.current_token() #varName
            self.consume_token() # varName
            self.symb_table.define(var_name, var_type, 'arg')


    def subroutineBody(self, f_name, method_check):
        # structured: '{' varDec* statements '}'
        self.consume_token() # {

        #checks for all variable declarations
        while self.current_token() == 'var':
            self.varDec() # varDec method

        if f_name != 'new': #writes function VM code if subroutine is not a constructor
            local_count = self.symb_table.varcount('local') #counts the number of local variables declared
            self.vm_code.write_function(f_name, self.class_name, local_count)
        if method_check == True: #if method subroutine, then sets THIS pointer to current object
            self.vm_code.write_push('argument', 0)
            self.vm_code.write_pop('pointer', 0)

        self.statements() # statements method
        self.consume_token() # }


    def varDec(self):
        # structured: 'var' type varName (',' varName)*';'

        self.consume_token() # var
        var_type = self.current_token() #type
        self.consume_token() # type
        var_name = self.current_token() #varName
        self.consume_token() # varName
        self.symb_table.define(var_name, var_type, 'var')

        # checks for any additional variable declarations in same line
        while self.current_token() == ',':
            self.consume_token() # ,
            var_name = self.current_token() #varName
            self.consume_token() # varName
            self.symb_table.define(var_name, var_type, 'var')
        self.consume_token() # ;


    def statements(self):
        # structured: (letStatement|ifStatement|whileStatement|doStatement|returnStatement)*

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


    def letStatement(self):
        # structured: 'let' varName ('['expression']')? '=' expression ';'

        self.consume_token() # let
        var_name = self.current_token() #stores variable name
        self.consume_token() # varName

        #checks if variable is an array
        if self.t_list[self.t_count].value == '[':
            array_check = True

            self.consume_token() # [
            self.expression() # expression method
            self.consume_token() # ]

            var_kind = self.symb_table.kindof(var_name)
            var_index = self.symb_table.indexof(var_name)
            self.vm_code.write_push(var_kind, var_index) # pushes base address of the array

            self.vm_code.write_arithmetic('add') # adds expression calculation to base array value to get target cell address

        else:
            array_check = False

        self.consume_token() # =
        self.expression() # expression method
        self.consume_token() # ;

        if array_check == True:
            self.vm_code.write_pop('temp', 2) # stores expression value
            self.vm_code.write_pop('pointer', 1) # sets THAT pointer to target cell address
            self.vm_code.write_push('temp', 2) # pushes stored expression calc
            self.vm_code.write_pop('that', 0) # writes final value to target cell address
        else:
            # writes expression to variable in stack
            var_kind = self.symb_table.kindof(var_name)
            var_index = self.symb_table.indexof(var_name)
            self.vm_code.write_pop(var_kind, var_index)


    def ifStatement(self):
        # structured: 'if' '('expression')' '{'statements'}' ('else' '{'statements'}')?

        self.consume_token() # if
        self.consume_token() # (
        self.expression() # expression method
        self.consume_token() # )
        self.vm_code.write_arithmetic('not') # inverses the expression for easier flow control

        else_label = self.label_generator()
        self.vm_code.write_if(else_label) # goes to break label if while condition not satisfied

        self.consume_token() # {
        self.statements() # statements method
        self.consume_token() # }

        notelse_label = self.label_generator()
        self.vm_code.write_goto(notelse_label) # goes to break label if while condition not satisfied

        self.vm_code.write_label(else_label) #adds else label for flow even if no else statement
        #checks for else statement
        if self.t_list[self.t_count].value == 'else':
            self.consume_token() # else
            self.consume_token() # {
            self.statements() # statements method
            self.consume_token() # }

        self.vm_code.write_label(notelse_label)

    def whileStatement(self):
        # structured: 'while' '('expression')' '{'statements'}'

        self.consume_token() # while
        while_label = self.label_generator()
        self.vm_code.write_label(while_label)

        self.consume_token() # (
        self.expression() # expression method
        self.consume_token() # )
        self.vm_code.write_arithmetic('not') # inverses the expression for easier flow control

        break_label = self.label_generator()
        self.vm_code.write_if(break_label) # goes to break label if while condition not satisfied

        self.consume_token() # {
        self.statements() # statements method
        self.consume_token() # }

        self.vm_code.write_goto(while_label) # loops back up to while_label to restart loop
        self.vm_code.write_label(break_label)


    def doStatement(self):
        # structured: 'do' subroutineName '('expressionList')'| (className|varName)'.' subroutineName '('expressionList')' ';'

        self.consume_token() # do

        self.subroutineCall()

        self.consume_token() # ;
        self.vm_code.write_pop('temp', 0) # pops dummy return value from void functions/methods


    def subroutineCall(self):
        #checks if subroutine is a method or a function
        method_check = False
        call_name = self.current_token() #stores first part of subroutine name
        self.consume_token() # subroutineName|(className|varName)

        #checks if subroutine call is calling method/function from another class/variable or function from current class. If neither, it is calling method from current class
        if self.t_list[self.t_count].value == '.':
            self.consume_token() # .

            if self.symb_table.kindof(call_name) != 'NONE':
                method_check = True
                obj_kind = self.symb_table.kindof(call_name)
                obj_index = self.symb_table.indexof(call_name)
                obj_class = self.symb_table.typeof(call_name)
                self.vm_code.write_push(obj_kind, obj_index) #pushes obj pointer from object variable to the stack for arg 0
                call_name = obj_class #changes call_name from variable name to class name to perform call

            call_name = call_name + '.' + self.current_token()  # puts subroutine name into VM function format
            self.consume_token() # subroutineName

        else:    # if no . then calling method from current class
            call_name = self.class_name + '.' + call_name # puts subroutine name into VM function format
            method_check = True
            self.vm_code.write_push('pointer', 0) # pushes current object point as calling method from current class

        self.consume_token() # (
        arg_count = self.expressionList() # expressionList method
        if method_check == True:
            arg_count += 1 #allocates space for object argument if callee is a method
        self.consume_token() # )
        self.vm_code.write_call(call_name, arg_count)

    def returnStatement(self):
        # structured: 'return' expression? ';'

        self.consume_token() # return

        # checks if there is a return value
        if self.t_list[self.t_count].value != ';':
            self.expression() #expression method

        self.consume_token() # ;


    def expressionList(self):
        # structured: (expression (',' expression)* )?

        arg_count = 0

        # checks for first expression
        if self.t_list[self.t_count].value != ')':
            self.expression() #expression method
            arg_count += 1

        # checks for any additional expressions
        while self.t_list[self.t_count].value != ')':
            self.consume_token() # ,
            self.expression() #expression method
            arg_count += 1

        return arg_count

    def expression(self):
        # structured: (term (op term)*

        self.term() # term method

        #checks for any operations followed by additional terms
        while self.current_token() in ['+','-','*','/','&amp;','|','&lt;','&gt;','=']:
            operator = self.current_token() # op
            self.consume_token() # op
            self.term() # term method
            op_code = op_dict[operator]
            self.vm_code.write_arithmetic(op_code)


    def term(self):
        # structured: integerConstant|stringConstant|keywordConstant|varName|varName'['expression']'|subroutineCall|'('expression')'|unaryOp term

        # checks if term is positive integer
        if str.isdigit(self.current_token()):
            if int(self.current_token()) >= 0:
                self.vm_code.write_push('constant', self.current_token())
                self.consume_token()
        #self.consume_token() # first token of the term

        # checks if term is true/false. False represented as 0 and True as -1
        elif self.current_token() in ['true', 'false']:
            self.vm_code.write_push('constant', 0)
            if self.current_token() == 'true':
                self.vm_code.write_arithmetic('not')
            self.consume_token() #true/false term

        elif self.current_token() == 'null':
            self.vm_code.write_push('constant', 0) #null is equivalent to False
            self.consume_token()

        # checks if token is THIS and, if so, pushes pointer of current object
        elif self.current_token() == 'this':
            self.vm_code.write_push('pointer', 0)
            self.consume_token()

        # checks if token is a string and, if so, creates a new string object
        elif (self.t_list[self.t_count].type == 'stringConstant'):
            string = self.current_token()
            str_len = len(string)
            self.vm_code.write_push('constant', str_len)
            self.vm_code.write_call('String.new', 1) #uses OS string function to allocate string object
            for c in string:
                self.vm_code.write_push('constant', ord(c)) # pushes ascii code of char for append method arg
                self.vm_code.write_call('String.appendChar', 2) #appends char to string

            self.consume_token() # string token

        # checks if term is a varName and then what kind of variable term
        elif (self.t_list[self.t_count].type == 'identifier'):
            if self.t_list[self.t_count + 1].value in ['(','.']: # checks if subroutine
                self.subroutineCall()

            elif self.t_list[self.t_count + 1].value == '[': # checks if array
                var_name = self.current_token() #stores variable name

                self.consume_token() #varName

                self.consume_token() # [
                self.expression() # expression method
                self.consume_token() # ]

                var_kind = self.symb_table.kindof(var_name)
                var_index = self.symb_table.indexof(var_name)
                self.vm_code.write_push(var_kind, var_index) # pushes base address of the array
                self.vm_code.write_arithmetic('add') # adds expression calculation to base array value to get target cell address

                self.vm_code.write_pop('pointer', 1) #sets THAT pointer to target cell address
                self.vm_code.write_push('that', 0) # pushes target cell value onto stack

            else: #if neither of the above, then term is just varName
                var_name = self.current_token() #stores variable name
                var_kind = self.symb_table.kindof(var_name)
                var_index = self.symb_table.indexof(var_name)
                self.vm_code.write_push(var_kind, var_index)
                self.consume_token() # varName

        # checks is term is an (expression)
        elif self.current_token() == '(':
            self.consume_token() # (
            self.expression() # expression method
            self.consume_token() # )

        # checks is term is an unaryOp
        elif self.current_token() in ['-','~']:
            unary_code = unary_dict[self.current_token()]
            self.consume_token() # unaryOp
            self.term() # term method
            self.vm_code.write_arithmetic(unary_code)


#used to translate operators into VM language
op_dict = {
    '+' : 'add',
    '-' : 'sub',
    '*' : 'call Math.multiply 2', #uses OS to do multiplication and division
    '/' : 'call Math.divide 2',
    '&amp;' : 'and',
    '|' : 'or',
    '&lt;' : 'lt',
    '&gt;' : 'gt',
    '=' : 'eq'
}

#used to translate unary operators into VM language
unary_dict = {
    '-' : 'neg',
    '~' : 'not',
}