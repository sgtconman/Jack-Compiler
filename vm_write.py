#simple module used by comp_engine to write and store vm_code for each class

class vm_writer:
    def __init__(self):
        self.code_list = []

    def write_push(self, segment, index):
        self.code_list.append('push ' + segment + ' ' + str(index) )

    def write_pop(self, segment, index):
        self.code_list.append('pop ' + segment + ' ' + str(index) )

    def write_arithmetic(self, command):
        self.code_list.append(command)

    def write_label(self, string):
        self.code_list.append('label ' + string)

    def write_goto(self, string):
        self.code_list.append('goto ' + string)

    def write_if(self, string):
        self.code_list.append('if-goto ' + string)

    def write_call(self, string, nArgs):
        self.code_list.append('call ' + string + ' ' + str(nArgs) )

    def write_function(self, f_name, class_name, nLocals):
        self.code_list.append('function ' + class_name + '.' + f_name + ' ' + str(nLocals) )

    def write_return(self):
        self.code_list.append('return')