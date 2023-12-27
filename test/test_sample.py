# test_sample.py

from sample import add


# test_ で始まる関数を自動でテスト用の関数として認識し実行する。
def test_add():
    assert add(2, 3) == 5
    assert add(4, 5) == 9
    assert add(0, 0) == 0
    assert add(-1, 1) == 0
