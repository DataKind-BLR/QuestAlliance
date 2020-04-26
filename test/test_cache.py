import requests

from lib.scraper_helper import SQLiteCache


def _test_cache_storage(storage_obj):
    # unknown key returns None
    assert storage_obj.get('one') is None

    _content_as_bytes = b"here's unicode: \xe2\x98\x83"
    _content_as_unicode = "here's unicode: \u2603"

    # set 'one'
    resp = requests.Response()
    resp.headers['x-num'] = 'one'
    resp.status_code = 200
    resp._content = _content_as_bytes
    storage_obj.set('one', resp)
    cached_resp = storage_obj.get('one')
    assert cached_resp.headers == {'x-num': 'one'}
    assert cached_resp.status_code == 200
    cached_resp.encoding = 'utf8'
    assert cached_resp.text == _content_as_unicode


def test_sqlite_cache():
    sc = SQLiteCache('cache.sqlite3')
    sc.clear()
    _test_cache_storage(sc)
    sc.clear()
