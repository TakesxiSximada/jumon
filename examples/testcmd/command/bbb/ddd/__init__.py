#-*- coding: utf-8 -*-
import jumon

def a_func(argv):
    print 'a_func', argv

def b_func(argv):
    print 'b_func', argv

def c_func(argv):
    print 'c_func', argv

CMD = {'a': a_func,
       'b': b_func,
       'c': c_func,
       }

def main(argv):
    parser = jumon.TransparentOptionParser()
    parser.add_option('--common-option', default=False, action='store_true')
    opts, args = parser.parse_args(argv)

    try:
        cmd = args[0]
    except IndexError as err:
        parser.error(err)

    sub_args = args[1:]

    try:
        func = CMD[cmd]
    except KeyError as err:
        parser.error(err)
    return func(sub_args)

