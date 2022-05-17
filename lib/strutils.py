


## ------------------------------------------------------------------------

### Returns ne version of `word` that fits in `length` digits
def truncate_align_word(word, length, align='left'):
    if align == 'right':
        op = '>'
    elif align == 'center':
        op = '^'
    else:
        op = '<'
        # align
    word = ('{:' + op + str(length) + '}').format(word)
    # truncate
    word = word[0:length]
    return word
