import unittest, subprocess, sys, os, tempfile, pathlib

# So we can find ultraimport without installing it
sys.path.insert(0, f"{os.path.dirname(__file__)}{os.sep}..{os.sep}..{os.sep}")

import ultraimport

class ultraimportTests(unittest.TestCase):

    def setUp(self):
        # TODO: Cleanup old __preprocessed__.py files and __pycache__ folder before test runs
        pass

    def exec(self, file_path):
        env = os.environ.copy()
        file_path = f"{os.path.dirname(__file__)}{os.sep}..{os.sep}{file_path}"
        env["PYTHONPATH"] = os.path.dirname(__file__) + os.path.sep + '../'
        ret = subprocess.run([sys.executable, file_path],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        ret.stdout = ret.stdout.replace(b'\r\n', b'\n');
        return ret

    def test_file_not_found(self):
        file_path = 'none_existant_random_file.py'
        with self.assertRaises(ultraimport.ResolveImportError) as cm:
            ultraimport(file_path)
        message = str(cm.exception)
        self.assertIn(file_path, message, 'file_path must be repeated in error message')
        self.assertIn('File does not exist', message)
        self.assertTrue(hasattr(cm.exception, 'file_path'))
        self.assertTrue(hasattr(cm.exception, 'file_path_resolved'))

    def test_file_not_found_with_suggestion(self):
        # Missing file ending .py
        file_path = f"__dir__{os.sep}..{os.sep}{os.path.normpath('examples/working/myprogram/run')}"
        # This file_path will be suggested
        file_path2 = os.path.normpath("examples/working/myprogram/run.py")
        with self.assertRaises(ultraimport.ResolveImportError) as cm:
            ultraimport(file_path)
        message = str(cm.exception)
        self.assertIn(file_path2, message)
        self.assertIn('Did you mean to import', message)

    def test_syntax_error(self):
        with self.assertRaises(NameError):
            ultraimport('__dir__/../examples/broken/syntax_error.py')

    def test_recurse_preprocessor_cache_path_prefix(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            code_file = f'{tmp_dir}{os.sep}code.py'
            with open(code_file, 'w') as f:
                print('x = 1', file=f)

            # No preprocessor cache
            code_module = ultraimport(code_file, recurse=True, use_cache=False, use_preprocessor_cache=False)
            pp_cache = pathlib.Path(f'{tmp_dir}{os.sep}code__preprocessed__.py')
            self.assertFalse(pp_cache.is_file(),
                f"Cached preprocessed file '{pp_cache}' should not exist when using `use_preprocessor_cache=False`")

            # Default preprocessor cache (in same directory)
            code_module = ultraimport(code_file, recurse=True, use_cache=False)
            pp_cache = pathlib.Path(f'{tmp_dir}{os.sep}code__preprocessed__.py')
            self.assertTrue(pp_cache.is_file(),
                f"Cached preprocessed file '{pp_cache}' should exist when using `use_preprocessor_cache=True`")

            # Preprocessor cache in subdirectory 'cache_folder'
            code_module = ultraimport(code_file, recurse=True, use_cache=False, cache_path_prefix='cache_folder')
            pp_cache = pathlib.Path(f'{tmp_dir}{os.sep}cache_folder{os.sep}code__preprocessed__.py')
            self.assertTrue(pp_cache.is_file(),
                f"Cached preprocessed file '{pp_cache}' should exist when using `use_preprocessor_cache=True`")

    # TODO
    #def test_lazy_load(self):
    #    pass

    @unittest.skipUnless(sys.version_info >= (3, 9), "requires Python >= 3.9")
    def test_example_mypackage(self):
        file_path = "examples/working/mypackage/run.py"
        ret = self.exec(file_path)
        self.assertEqual(ret.returncode, 0, f'Running {file_path} did return with an error: {ret}')
        self.assertEqual(ret.stdout, b"submodule start  submodule\n"
            b"hello from xmodule.py\n"
            b"somepackage.__init__ start\n"
            b"somepackage.__init__ end\n"
            b"hello from siblingmodule.py\n"
            b"mymodule.py start\n"
            b"mymodule.py end\n"
            b"Running myotherfunction() from myothermodule: hello from submodule.py\n"
            b"submodule end\n")

    def test_example_myprogram(self):
        file_path = "examples/working/myprogram/run.py"
        ret = self.exec(file_path)
        self.assertEqual(ret.returncode, 0, f'Running {file_path} did return with an error: {ret}')
        self.assertEqual(ret.stdout, b"""I did something\ncache store: I did something\n""")

    def test_example_dependency_injection(self):
        file_path = "examples/working/dependency-injection/run.py"
        ret = self.exec(file_path)
        self.assertEqual(ret.returncode, 0, f'Running {file_path} did return with an error: {ret}')
        self.assertEqual(ret.stdout, b"injected logger: worker.py is doing some work\n")

    def test_example_impossible_filename(self):
        file_path = "examples/working/impossible-filename/run.py"
        ret = self.exec(file_path)
        self.assertEqual(ret.returncode, 0, f'Running {file_path} did return with an error: {ret}')
        self.assertEqual(ret.stdout, b"Hello world\n")

    def test_example_dynamic_namespace(self):
        file_path = "examples/working/dynamic-namespace/run.py"
        ret = self.exec(file_path)
        self.assertEqual(ret.returncode, 0, f'Running {file_path} did return with an error: {ret}')
        self.assertIn(b"<module 'dynamic-namespace.utils'", ret.stdout)
        self.assertIn(b"<module 'dynamic-namespace.lib'", ret.stdout)


if __name__ == '__main__':
    unittest.main()
