from symbols import symbol_table

symb_table = symbol_table()
symb_table.define('test', 'string', 'var')

weed = symb_table.kindof('test')
weed = symb_table.varcount('local')
print(weed)
