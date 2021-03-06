import unittest, subprocess, sys, os

sys.path.insert(0, '..')

import ultraimport

class ultraimportTests(unittest.TestCase):

    def setUp(self):
        pass

    def exec(self, filepath):
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.dirname(__file__) + os.path.sep + '../'
        ret = subprocess.run([sys.executable, filepath],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        ret.stdout = ret.stdout.replace(b'\r\n', b'\n');
        return ret

    def test_file_not_found(self):
        with self.assertRaises(ImportError):
            ultraimport('none_existant_random_file.py')

    def test_syntax_error(self):
        with self.assertRaises(NameError):
            ultraimport('__dir__/../examples/broken/syntax_error.py')

    def test_example_myprogram(self):
        filename = "examples/working/myprogram/run.py"
        ret = self.exec(filename)
        self.assertEqual(ret.returncode, 0, f'Running {filename} did return with an error: {ret}')
        self.assertEqual(ret.stdout, b"""I did something\ncache store: I did something\ncache store: Something\n""")

    @unittest.skipUnless(sys.version_info >= (3, 9), "requires Python >= 3.9")
    def test_example_mypackage(self):
        filename = "examples/working/mypackage/run.py"
        ret = self.exec(filename)
        self.assertEqual(ret.returncode, 0, f'Running {filename} did return with an error: {ret}')
        self.assertEqual(ret.stdout, b"submodule start  submodule\n"
            b"hello from xmodule.py\n"
            b"hello from siblingmodule.py\n"
            b"mymodule.py start\n"
            b"mymodule.py end\n"
            b"Running myotherfunction() from myothermodule: hello from submodule.py\n"
            b"submodule end\n")

    def test_example_dependency_injection(self):
        filename = "examples/working/dependency-injection/run.py"
        ret = self.exec(filename)
        self.assertEqual(ret.returncode, 0, f'Running {filename} did return with an error: {ret}')
        self.assertEqual(ret.stdout, b"injected logger: worker.py is doing some work\n")

if __name__ == '__main__':
    unittest.main()
