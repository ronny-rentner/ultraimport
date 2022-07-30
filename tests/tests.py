import unittest, subprocess, sys, os

# So we can find ultraimport without installing it
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
        file_path = 'none_existant_random_file.py'
        with self.assertRaises(ultraimport.Error) as cm:
            ultraimport(file_path)
        message = str(cm.exception)
        self.assertIn(file_path, message)
        self.assertIn('File does not exist', message)
        self.assertTrue(hasattr(cm.exception, 'file_path'))
        self.assertTrue(hasattr(cm.exception, 'file_path_resolved'))

    def test_file_not_found_with_suggestion(self):
        # Missing file ending .py
        file_path = "examples/working/myprogram/run"
        # This file_path will be suggested
        file_path2 = "examples/working/myprogram/run.py"
        with self.assertRaises(ultraimport.Error) as cm:
            ultraimport(file_path)
        message = str(cm.exception)
        self.assertIn(file_path2, message)
        self.assertIn('Did you mean to import', message)

    def test_syntax_error(self):
        with self.assertRaises(NameError):
            ultraimport('__dir__/../examples/broken/syntax_error.py')

    def test_example_myprogram(self):
        file_path = "examples/working/myprogram/run.py"
        ret = self.exec(file_path)
        self.assertEqual(ret.returncode, 0, f'Running {file_path} did return with an error: {ret}')
        self.assertEqual(ret.stdout, b"""I did something\ncache store: I did something\ncache store: Something\n""")

    def test_lazy_load(self):
        pass

    @unittest.skipUnless(False, 'temporarily deactivate')
    @unittest.skipUnless(sys.version_info >= (3, 9), "requires Python >= 3.9")
    def test_example_mypackage(self):
        file_path = "examples/working/mypackage/run.py"
        ret = self.exec(file_path)
        self.assertEqual(ret.returncode, 0, f'Running {file_path} did return with an error: {ret}')
        self.assertEqual(ret.stdout, b"submodule start  submodule\n"
            b"hello from xmodule.py\n"
            b"hello from siblingmodule.py\n"
            b"mymodule.py start\n"
            b"mymodule.py end\n"
            b"Running myotherfunction() from myothermodule: hello from submodule.py\n"
            b"submodule end\n")

    def test_example_dependency_injection(self):
        file_path = "examples/working/dependency-injection/run.py"
        ret = self.exec(file_path)
        self.assertEqual(ret.returncode, 0, f'Running {file_path} did return with an error: {ret}')
        self.assertEqual(ret.stdout, b"injected logger: worker.py is doing some work\n")

if __name__ == '__main__':
    unittest.main()
