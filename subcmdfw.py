#-*- coding: utf-8 -*-
import sys
import optparse

class TransparentOptionParser(optparse.OptionParser):
    # over ride on arguments from 'rargs' 'values' consuming.
    def _process_args(self, largs, rargs, values):
        """_process_args(largs : [string],
                         rargs : [string],
        values : Values)

        Process command-line arguments and populate 'values', consuming
        options and arguments from 'rargs'.  If 'allow_interspersed_args' is
        false, stop at the first non-option argument.  If true, accumulate any
        interspersed non-option arguments in 'largs'.
        """
        def _through_option(func, *args, **kwds):
            """new function"""
            try:
                func(*args, **kwds)
            except optparse.BadOptionError, err:
                largs.append(err.opt_str)

        while rargs:
            arg = rargs[0]
            # We handle bare "--" explicitly, and bare "-" is handled by the
            # standard arg handler since the short arg case ensures that the
            # len of the opt string is greater than 1.
            if arg == "--":
                del rargs[0]
                return
            elif arg[0:2] == "--":
                # process a single long option (possibly with value(s))
                self._process_long_opt(rargs, values)
            elif arg[:1] == "-" and len(arg) > 1:
                # process a cluster of short options (possibly with
                # value(s) for the last one only)
                _through_option(self._process_short_opts, rargs, values) # modified
            elif self.allow_interspersed_args:
                largs.append(arg)
                del rargs[0]
            else:
                return                  # stop now, leave this arg in rargs

        # Say this is the original argument list:
        # [arg0, arg1, ..., arg(i-1), arg(i), arg(i+1), ..., arg(N-1)]
        #                            ^
        # (we are about to process arg(i)).
        #
        # Then rargs is [arg(i), ..., arg(N-1)] and largs is a *subset* of
        # [arg0, ..., arg(i-1)] (any options and their arguments will have
        # been removed from largs).
        #
        # The while loop will usually consume 1 or more arguments per pass.
        # If it consumes 1 (eg. arg is an option that takes no arguments),
        # then after _process_arg() is done the situation is:
        #
        #   largs = subset of [arg0, ..., arg(i)]
        #   rargs = [arg(i+1), ..., arg(N-1)]
        #
        # If allow_interspersed_args is false, largs will always be
        # *empty* -- still a subset of [arg0, ..., arg(i-1)], but
        # not a very interesting subset!

    def parse_args(self, args=None, values=None):
        if args is not None:
            args = list(args)
        return optparse.OptionParser.parse_args(self, args, values)

def entry(prefix, argv=sys.argv[1:], parser=None):
    if not parser:
        parser = TransparentOptionParser()
    opts, args = parser.parse_args(argv)

    if prefix.endswith('.'):
        prefix = prefix.strip('.')
    
    subcmds = args
    prefixes = prefix.split('.')
    for ii in range(len(prefixes), 0, -1):
        modnames = prefixes + subcmds[:ii]
        doted_name = '.'.join(modnames)
        
        try:
            base_mod = __import__(doted_name)
        except ImportError:
            continue
        else:
            try:
                mod = base_mod
                for name in modnames[1:]:
                    mod = getattr(mod, name)
            except AttributeError:
                continue
            else:
                if mod.__name__ != prefix:
                    func = getattr(mod, 'main')
                    rc = func(args[ii:])
                    if rc is None:
                        rc = 0
                    sys.exit(rc)
                else: 
                    pass # command not found
    else:
        parser.error('Command Not Found: {0}'.format(' '.join(argv)))
                
                
        

                    
    
