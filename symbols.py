# data structure for storing symbols in the symbol table
class symbol:
    def __init__(self, name, type, kind, index):
        self.name = name
        self.type = type
        self.kind = kind
        self.index = index

kind_dict = {
    'var' : 'local',
    'arg' : 'argument',
    'static' : 'static',
    'field' : 'field'
}

class symbol_table:
    def __init__(self):
        self.class_table = []
        self.subroutine_table = []

    # resets subroutine symbol table
    def start_subroutine(self, name):
        self.subroutine_table = []


    def define(self, name, type, kind):

        kind_count = 0
        kind = kind_dict[kind] #changes kind term to match VM syntax

        # adds indexed symbol to class table if class-level variable
        if kind in ['static', 'field']:
            if len(self.class_table) == 0:
                self.class_table.append(symbol(name, type, kind, kind_count))
            else:
                for symb in self.class_table:
                    if symb.kind == kind:
                        kind_count += 1
                self.class_table.append(symbol(name, type, kind, kind_count))

        # adds indexed symbol to subroutine table if subroutine-level variable
        if kind in ['argument', 'local']:
            if len(self.subroutine_table) == 0:
                self.subroutine_table.append(symbol(name, type, kind, kind_count))
            else:
                for symb in self.subroutine_table:
                    if symb.kind == kind:
                        kind_count += 1
                self.subroutine_table.append(symbol(name, type, kind, kind_count))


    # searches tables for given symbol and returns the index value
    def indexof(self, name):
        for symb in self.class_table:
            if symb.name == name:
                return symb.index
        for symb in self.subroutine_table:
            if symb.name == name:
                return symb.index


    # searches tables for given symbol and returns the kind. If symbol not found, returns NONE
    def kindof(self, name):
        for symb in self.class_table:
            if symb.name == name:
                return symb.kind
        for symb in self.subroutine_table:
            if symb.name == name:
                return symb.kind

        return 'NONE'


    # searches tables for given symbol and returns the type
    def typeof(self, name):
        for symb in self.class_table:
            if symb.name == name:
                return symb.type
        for symb in self.subroutine_table:
            if symb.name == name:
                return symb.type


    # searches tables for given symbol and returns the type
    def varcount(self, kind):

        kind_count = 0

        if kind in ['static', 'field']:
            for symb in self.class_table:
                    if symb.kind == kind:
                        kind_count += 1

        if kind in ['argument', 'local']:
            for symb in self.subroutine_table:
                    if symb.kind == kind:
                        kind_count += 1

        return kind_count