# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_unittest.py

# 运行特定测试函数
pytest tests/test_pytest.py::test_add

# 运行unittest测试
python -m unittest tests.test_unittest