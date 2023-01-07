# B站番剧点评爬虫

### 环境配置

1. 安装Python
2. pip install sqlalchemy
3. pip install requests

### 运行

获取全部番剧:  
```bash
$ python3 spider.py
```

输出为csv:
```bash
$ python3 tocsv.py
```

### 查询

启动pyshell:  
```bash
$ python3
```

```python
>>> from models import *
```

然后就可以查询了, 比如要查询标题含有"三体"的动画:

```python
>>> session.query(Anime).filter(Anime.title.like('%三体%')).all()
[国创 三体
...
国创 我的三体
...]
...
```

#### 项目中已有的result.db和result.csv是2023/1/7的数据, 不一定一直有效