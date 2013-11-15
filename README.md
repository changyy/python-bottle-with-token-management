python-bottle-with-token-management
===================================

採用 Bottle 實作簡易的 API-based login service。

開發環境：Ubuntu 12.04

環境設置
========
```
$ apt-get install python-paste
```

運行
====
```
$ python app.py
Bottle v0.11.6 server starting up (using PasteServer())...
Listening on http://0.0.0.0:22005/
Hit Ctrl-C to quit.

serving on 0.0.0.0:22005 view at http://127.0.0.1:22005
```

登入
====
```
$ wget -qO- "http://localhost:22005/api/login?name=admin&password=admin"
{"status": true, "data": "9fab7541a28253f2e70c2b43caae58e6740781fd"}
```

驗證登入
========
```
$ wget -qO- "http://localhost:22005/api/status?name=admin&token=xxx"
{"status": false, "data": "need login"}

$ wget -qO- "http://localhost:22005/api/status?name=admin&token=9fab7541a28253f2e70c2b43caae58e6740781fd"
{"status": true}
```

登出
====
```
$ wget -qO- "http://localhost:22005/api/logout?name=admin&token=9fab7541a28253f2e70c2b43caae58e6740781fd"
{"status": true}
```

更改密碼
========
```
$ wget -qO- "http://localhost:22005/api/password?name=admin&token=9fab7541a28253f2e70c2b43caae58e6740781fd&password=hello"
{"status": true}
```

支援多個裝置採用的 token 會不一樣(在此依據 client User-agent 與 IP)，但同一裝置登入時可以沿用之前有效的 token
========

```
$ sqlite3 token.db "SELECT * FROM Admin"
|admin|aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d|{"token": {"5d3cf7f3a070d914b23fa197b263caa5831b909e": {"pattern": "48a5df88e6b16f7a8f49d3146744f8dae41fadb7", "expired": "2013-11-15T23:46:17.374856"}, "2e52d3eb834e09f30509fcf4837478f207e71f59": {"pattern": "651294308142d18b74de84a732c000e49a0b7442", "expired": "2013-11-15T23:46:02.716752"}, "9fab7541a28253f2e70c2b43caae58e6740781fd": {"pattern": "d82b1d6b570d161d7d7e487b987d91843c11d713", "expired": "2013-11-15T23:55:32.803806"}}}

$ sqlite3 token.db "SELECT * FROM Admin" | tail -c +49 | python -mjson.tool
{
    "token": {
        "2e52d3eb834e09f30509fcf4837478f207e71f59": {
            "expired": "2013-11-15T23:46:02.716752", 
            "pattern": "651294308142d18b74de84a732c000e49a0b7442"
        }, 
        "5d3cf7f3a070d914b23fa197b263caa5831b909e": {
            "expired": "2013-11-15T23:46:17.374856", 
            "pattern": "48a5df88e6b16f7a8f49d3146744f8dae41fadb7"
        }, 
        "9fab7541a28253f2e70c2b43caae58e6740781fd": {
            "expired": "2013-11-15T23:55:32.803806", 
            "pattern": "d82b1d6b570d161d7d7e487b987d91843c11d713"
        }
    }
}
```
