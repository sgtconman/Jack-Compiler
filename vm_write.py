class vm_writer:
    def __init__(self):
        self.vm_code = []

    def write_push(self, segment, index):
        self.vm_code.append('push ' + segment + ' ' + index)

    def write_pop(self, segment, index):
        self.vm_code.append('pop ' + segment + ' ' + index)

    def write_arithmetic(self, command):
        self.vm_code.append('push ' + command)

    def write_label(self, string):
        self.vm_code.append('label ' + string)

    def write_goto(self, string):
        self.vm_code.append('goto ' + string)

    def write_if(self, string):
        self.vm_code.append('if-goto ' + string)

    def write_call(self, string, nArgs):
        self.vm_code.append('call ' + string + ' ' + nArgs)

    def write_function(self, f_name, class_name, nLocals):
        self.vm_code.append('label ' + class_name + '.' + f_name + ' ' + nLocals)

    def write_return(self):
        self.vm_code.append('return')