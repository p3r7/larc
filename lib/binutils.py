

## ------------------------------------------------------------------------
## CORE - BINARY

def hexp(v):
    padding = 8
    return '0x{0:0{1}X}'.format(v, padding)

def binp(v):
    return format(v, '#010b')

def is_bit_on(v, index):
    mask = 0b1 << index
    return (mask & v) > 0
