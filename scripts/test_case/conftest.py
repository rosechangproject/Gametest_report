import pytest

@pytest.fixture(scope="session")
def api_base_url():
    """提供 API 的基礎 URL"""
    # 可以從環境變數或設定檔讀取
    return "https://httpbin.org" # 使用 httpbin 作為範例
