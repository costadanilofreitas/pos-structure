import os
import pytest


def main():
    pytest.main([os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")])


if __name__ == "__main__":
    main()
