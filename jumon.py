#-*- coding: utf-8 -*-
"""The small framework for sub commands.
"""
__version__ = "1.0.0"
__all__ = ['TransparentOptionParser',
           'entry',
           ]

__copyright__ = """
Copyright (c) 2013 Takesxi Sximada. All rights reserved.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.


Diversion from optparse.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Copyright (c) 2001-2006 Gregory P. Ward.  All rights reserved.
Copyright (c) 2002-2006 Python Software Foundation.  All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

  * Neither the name of the author nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
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
                _through_option(self._process_short_opts, rargs, values) #modified
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
                    pass
    else:
        parser.error('Command Not Found: {0}'.format(' '.join(argv)))
