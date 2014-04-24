#-*- coding: utf-8 -*-
"""The small framework for sub commands.
"""
__version__ = "1.1.8"
__all__ = ['TransparentOptionParser',
           'TransparentArgumentParser',
           'Shell',
           'Env',
           'entry',
           ]

__copyright__ = """
Copyright (c) 2013-2014 TakesxiSximada. All rights reserved.

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
import os
import re
import sys
import shlex
import optparse
import argparse
import subprocess
import enum

def escape(word):
    if ' ' in word:
        word = word.replace('"', '\\"')
        word = word.replace("'", "\\'")
        word = '"' + word + '"'
    return word

def escape_join(words):
    return ' '.join(map(escape, words))


class Env(enum.Enum):
    JUMON_SUDO = ''

    @classmethod
    def get(cls, env):
        try:
            return os.environ[env.name]
        except KeyError as err:
            return env.value

class Shell(object):

    @classmethod
    def call(cls, line, *args, **kwds):
        line, args, kwds = cls.switch_insert_sudo(line, *args, **kwds)
        print('')
        print('$ {}'.format(line))
        if not 'shell' in kwds:
            kwds['shell'] = True
        return subprocess.Popen(line, *args, **kwds)

    @classmethod
    def system(cls, line, *args, **kwds):
        line, args, kwds = cls.switch_insert_sudo(line, *args, **kwds)
        print('')
        print('$ {}'.format(line))
        return os.system(line)

    @classmethod
    def get_sudo_user(cls, sudo=None):
        if sudo is True:
            sudo = Env.get(Env.JUMON_SUDO)
        return sudo

    @classmethod
    def switch_insert_sudo(cls, line, sudo=None, *args, **kwds):
        sudo = cls.get_sudo_user(cls, sudo)
        if sudo:
            line = 'sudo -u {} {}'.format(sudo, line)
        return line, args, kwds

    @classmethod
    def sudo(cls, line, *args, **kwds):
        """
        duplicated
        """
        sudo_user = Env.get(Env.JUMON_SUDO)
        if sudo_user:
            line = 'sudo -u {} {}'.format(sudo_user, line)
        return cls.call(line, *args, **kwds)

    @classmethod
    def system_old(cls, line):
        """
        duplicated
        """
        print('')
        print('$ {}'.format(line))
        return os.system(line)


def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def mkdir(path, parents=False):
    """
    parents: no error if existing, make parent directories as needed
    """
    func = os.makedirs if parents else os.mkdir
    try:
        return func(path)
    except:
        if not parents:
            raise

def call(line, background=False, *args, **kwds):
    print('$ ' + line)
    cmd = shlex.split(line.strip())
    child = subprocess.Popen(cmd, shell=False, *args, **kwds)
    if not background:
        child.wait()
    return child


class TransparentOptionParser(optparse.OptionParser):
    def __new__(cls, *args, **kwds):
        if len(args) < 8 or not kwds.has_key('add_help_option'):
            kwds['add_help_option'] = None # default value orverride
        return super(type(cls), cls).__new__(cls, *args, **kwds)


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
                # self._process_long_opt(rargs, values)
                _through_option(self._process_long_opt, rargs, values) #modified

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


class TransparentArgumentParser(argparse.ArgumentParser):
    def __new__(cls, *args, **kwds):
        if len(args) < 12 or not kwds.has_key('add_help'):
            kwds['add_help'] = None # default value orverride
        return super(type(cls), cls).__new__(cls, *args, **kwds)

    def parse_args(self, *args, **kwds):
        args, _unrecognizes = self.parse_known_args(*args, **kwds)
        self._unrecognizes = _unrecognizes
        return args

    def get_unrecognizes(self):
        return self._unrecognizes

def get_debug_switch():
    """The debug switcher

    >>> import os, jumon
    >>> os.environ['JUMON_DEBUG'] = 'True'
    >>> jumon.get_debug_switch()
    True



    >>> os.environ['JUMON_DEBUG'] = ''
    >>> jumon.get_debug_switch()
    None


    >>> value = os.environ.pop('JUMON_DEBUG')
    >>> jumon.get_debug_switch()
    None
    """
    try:
        return os.environ['JUMON_DEBUG'] != ''
    except KeyError:
        pass

def entry(prefix, argv=sys.argv[1:], parser=None):
    _debug = get_debug_switch()
    if not parser:
        parser = TransparentOptionParser()
        parser.add_option('--command-list', dest='command_list', default=False, action='store_true')
    opts, args = parser.parse_args(argv)

    if opts.command_list:
        print('Sub commmands:')
        dotteds = prefix.split('.')
        base_name = dotteds[0]
        base_mod = __import__(base_name)

        rel_mod_names = dotteds[1:]
        mod = base_mod
        for name in rel_mod_names:
            mod = getattr(mod, name)

        regx_py = re.compile('.*\.py$', re.I)
        top_dir = os.path.abspath(os.path.dirname(mod.__file__))
        for root, dirs, files in os.walk(top_dir):
            for filename in files:
                if regx_py.match(filename):
                    if filename == '__init__.py':
                        path = root
                    else:
                        path = os.path.join(root, os.path.splitext(filename)[0])
                    path = path.replace(top_dir, '')
                    cmdline = path.split('/')
                    print(' '.join(cmdline))
        sys.exit(255)

    if prefix.endswith('.'):
        prefix = prefix.strip('.')
    subcmds = args
    prefixes = prefix.split('.')
    for ii in range(len(prefixes), 0, -1):
        modnames = prefixes + subcmds[:ii]
        doted_name = '.'.join(modnames)

        try:
            base_mod = __import__(doted_name)
        except (ImportError, ValueError) as err:
            if _debug:
                print err
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
