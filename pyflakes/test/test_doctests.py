import textwrap
from unittest2 import skip

from pyflakes.test.test_other import Test as TestOther
from pyflakes.test.test_imports import Test as TestImports
from pyflakes.test.test_undefined_names import Test as TestUndefinedNames

import pyflakes.messages as m


class Test(TestOther, TestImports, TestUndefinedNames):

    def doctestify(self, input):
        lines = []
        for line in textwrap.dedent(input).splitlines():
            if line.strip() == '':
                pass
            elif (line.startswith(' ') or
                  line.startswith('except:') or
                  line.startswith('except ') or
                  line.startswith('finally:') or
                  line.startswith('else:') or
                  line.startswith('elif ')):
                line = "... %s" % line
            else:
                line = ">>> %s" % line
            lines.append(line)
        doctestificator = textwrap.dedent('''\
            def doctest_something():
                """
                   %s
                """
            ''')
        return doctestificator % "\n       ".join(lines)

    def flakes(self, input, *args, **kw):
        return super(Test, self).flakes(self.doctestify(input),
                                        *args, **kw)

    def test_doubleNestingReportsClosestName(self):
        """
        Lines in doctest are a bit different so we can't use the test
        from TestUndefinedNames
        """
        exc = super(Test, self).flakes('''
        def doctest_stuff():
            """
                >>> def a():
                ...     x = 1
                ...     def b():
                ...         x = 2 # line 7 in the file
                ...         def c():
                ...             x
                ...             x = 3
                ...             return x
                ...         return x
                ...     return x

            """
        ''', m.UndefinedLocal).messages[0]
        self.assertEqual(exc.message_args, ('x', 7))

    def test_futureImport(self):
        """XXX This test can't work in a doctest"""

    def test_importBeforeDoctest(self):
        super(Test, self).flakes("""
        import foo

        def doctest_stuff():
            '''
                >>> foo
            '''
        """)

    @skip("todo")
    def test_importBeforeAndInDoctest(self):
        super(Test, self).flakes('''
        import foo

        def doctest_stuff():
            """
                >>> import foo
                >>> foo
            """

        foo
        ''', m.Redefined)

    def test_importInDoctestAndAfter(self):
        super(Test, self).flakes('''
        def doctest_stuff():
            """
                >>> import foo
                >>> foo
            """

        import foo
        foo()
        ''')

    def test_offsetInDoctests(self):
        exc = super(Test, self).flakes('''

        def doctest_stuff():
            """
                >>> x # line 5
            """

        ''', m.UndefinedName).messages[0]
        self.assertEqual(exc.lineno, 5)
        self.assertEqual(exc.col, 12)

    def test_offsetInLambdasInDoctests(self):
        exc = super(Test, self).flakes('''

        def doctest_stuff():
            """
                >>> lambda: x # line 5
            """

        ''', m.UndefinedName).messages[0]
        self.assertEqual(exc.lineno, 5)
        self.assertEqual(exc.col, 20)

    def test_offsetAfterDoctests(self):
        exc = super(Test, self).flakes('''

        def doctest_stuff():
            """
                >>> x = 5
            """

        x

        ''', m.UndefinedName).messages[0]
        self.assertEqual(exc.lineno, 8)
        self.assertEqual(exc.col, 0)

    def test_syntaxErrorInDoctest(self):
        exc = super(Test, self).flakes('''
        def doctest_stuff():
            """
                >>> from # line 4
            """
        ''', m.DoctestSyntaxError).messages[0]
        self.assertEqual(exc.lineno, 4)
        self.assertEqual(exc.col, 26)

    def test_indentationErrorInDoctest(self):
        exc = super(Test, self).flakes('''
        def doctest_stuff():
            """
                >>> if True:
                ... pass
            """
        ''', m.DoctestSyntaxError).messages[0]
        self.assertEqual(exc.lineno, 5)
        self.assertEqual(exc.col, 16)

    def test_doctestCanReferToFunction(self):
        super(Test, self).flakes("""
        def foo():
            '''
                >>> foo
            '''
        """)

    def test_doctestCanReferToClass(self):
        super(Test, self).flakes("""
        class Foo():
            '''
                >>> Foo
            '''
            def bar(self):
                '''
                    >>> Foo
                '''
        """)
