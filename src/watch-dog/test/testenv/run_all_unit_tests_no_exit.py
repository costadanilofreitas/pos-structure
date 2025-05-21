import unittest
import os


def main():
    loader = unittest.TestLoader()
    current_directory = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.abspath(os.path.join(current_directory, ".."))
    tests = loader.discover(start_dir=test_dir, top_level_dir=test_dir)
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == "__main__":
    main()
