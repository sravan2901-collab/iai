import pytest
import sys

if __name__ == "__main__":
    ret = pytest.main(["-v", "tests/test_auth.py"])
    sys.exit(ret)
