
def rfic_info(*args, **kwargs):
    pstr = ""
    for item in args[:-1]:
        pstr += str(item) + " "
    pstr += str(args[-1])

    # 41红色  42绿色  43黄色  44蓝色  47白色
    color = kwargs.get('color', None)
    if color:
        kv = {
            'red': 41,
            'green': 42,
            'yellow': 43,
            'blue': 46
        }
        print('\033[1;30;%sm' % kv[color], end="")
    print(pstr)
    if color:
        print('\033[0m', end="")
    return pstr


def rfic_error(*args, **kwargs):
    pstr = ""
    for item in args[:-1]:
        pstr += str(item) + " "
    pstr += str(args[-1])

    # 41红色  42绿色  43黄色  44蓝色  47白色
    color = kwargs.get('color', "red")
    if color:
        kv = {
            'red': 41,
            'green': 42,
            'yellow': 43,
            'blue': 44
        }
        print('\033[1;33;%sm' % kv[color], end="")
    print(pstr)
    if color:
        print('\033[0m', end="")
    return pstr