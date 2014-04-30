#! /usr/bin/env python
#-*- coding: utf-8 -*-
from unittest import TestCase

class JumonTest(TestCase):
    def test_it(self):
        pass


class TransparentOptionParserTest(TestCase):
    def test_transparent_help(self):
        from jumon import TransparentOptionParser
        input_args = ['--help', '-h', 'a', 'B'] # all ignore
        parser = TransparentOptionParser()
        opts, args = parser.parse_args(input_args)
        for ii in range(len(input_args)):
            self.assertEqual(args[ii], input_args[ii])

class TransparentArgumentParserTest(TestCase):
    def test_transparent_help(self):
        from jumon import TransparentArgumentParser
        input_args = ['--help', '-h', 'a', 'B'] # all ignore
        parser = TransparentArgumentParser()
        parser.parse_args(input_args)
        args = parser.get_unrecognizes()
        for ii in range(len(input_args)):
            self.assertEqual(args[ii], input_args[ii])
