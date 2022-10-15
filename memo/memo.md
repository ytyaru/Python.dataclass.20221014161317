Pythonのdataclassを使ってみる

　C言語でいう構造体のこと。

<!-- more -->

# dataclass

　C言語でいう構造体のこと。

* [dataclasses][]
	* [dataclass][]
	* [field][]

[dataclasses]:https://docs.python.org/ja/3/library/dataclasses.html
[dataclass]:https://docs.python.org/ja/3/library/dataclasses.html#dataclasses.dataclass
[field]:https://docs.python.org/ja/3/library/dataclasses.html#dataclasses.field

　ORMを書くときに使う。SQLite3のようなRDBMSのレコードをPythonの型として表現する。

# コード例

## 必須

```python
#!/usr/bin/env python3
# coding: utf8
import dataclasses
from dataclasses import dataclass, field, _MISSING_TYPE
from decimal import Decimal
from datetime import datetime, date, time

@dataclass
class Record:
    id: int
    name: str
    birth: datetime 
    value: Decimal

if __name__ == '__main__':
    args = [1, 'A', datetime.now(), Decimal('0.1')]
    r1 = Record(*args)

    kwargs = {'id': 1, 'name': 'A', 'birth': datetime.now(), 'value': Decimal('0.1')}
    r2 = Record(**kwargs)
```

　`Record`クラスがそれ。呼出のところで4つの必須引数がある。

## 全オプション

　すべてのプロパティにデフォルト値を代入する。この場合、呼出のときに引数を与えずとも実行できる。

```python
@dataclass
class Record:
    id: int = 0
    name: str = ''
    birth: datetime = datetime.now()
    value: Decimal = Decimal('0.0')

if __name__ == '__main__':
    print(Record())
    print(Record(1, 'A'))
    print(Record(name='B', value=Decimal('9.9')))
```

```sh
Record(id=0, name='', birth=datetime.datetime(...), value=Decimal('0.0'))
Record(id=1, name='A', birth=datetime.datetime(...), value=Decimal('0.0'))
Record(id=0, name='B', birth=datetime.datetime(...), value=Decimal('9.9'))
```

## 一部だけオプション

　あるプロパティにデフォルト値をセットしたら、それ以降にあるプロパティにもデフォルト値をセットせねばならない。たとえば以下のようなことはできない。``

```python
@dataclass
class Record:
    id: int
    name: str
    birth: datetime = datetime.now()
    value: Decimal # TypeError: non-default argument 'value' follows default argument
```

　3番目の`birth`にデフォルト値をセットしたら、以降の`value`にもデフォルト値をセットせねばならない。さもなくば`TypeError`になる。

　これはPythonの関数における位置引数とオプション引数の仕様と同じである。デフォルト値がない前方のプロパティは必須位置引数となり、デフォルト値がある後方のプロパティはオプションとなる。

```python
def f(r1, r2, o3=0, o4=0): pass

f(1,2)
f(1,2,3)
f(1,2,3,4)
f(1,2,o4=4)
```

　しかし、この仕様のせいでSQLのcreate tableにおけるdefault制約をdefault値で再現できない。なぜならSQLのほうにはPython引数のような縛りが存在しないから。ではどうやってSQLの制約情報を与えるか。[field][]の`metadata`を使う。

# [field][]の`metadata`

```python
from dataclasses import dataclass, field, _MISSING_TYPE
@dataclass
class Record:
    id: int = field(metadata={'PK':True})
    name: str = field(metadata={'UK':True})
    birth: datetime = field(metadata={'DF':'CURRENT_TIMESTAMP'})
    value: Decimal
```

　[field][]の`metadata`はMappingProxyType。読取専用の辞書`dict`型である。それ以外の型はセットできない。`dict`型であれば自由にセットできる。

　SQLの制約をどう表現するか考えてみた。

key|type|value|意味(SQLキーワード)
---|----|-----|-------------------
`P`,`PK`|bool|`True`/`False`|`primary key`
`U`,`UK`|bool|`True`/`False`|`unique`
`F`,`FK`|str|`表名 列名`|`references t(c)`
`N`,`NL`|bool|`True`/`False`|`not null`を外す
`D`,`DF`|str|`デフォルト値`|`default デフォルト値`
`C`,`CK`|str|`条件式`|`check(条件式)`

## 複雑な制約

　列名に対して制約を指定する方法だと、複数の列名で指定する制約を定義できない。

　そこで`_`プロパティでそれらを定義する方法を思いついた。名前`_`はSQLの列名として使わないと思う。なのでそれを制約句を書く所として使うことにする。

### 複合キー

```sql
create table users(
  id integer not null,
  sid integer not null,
  constraint pk primary key (id, sid)
);
```

　`id`と`sid`の2列で一意と識別する。これをPythonのdatasetで表現するなら以下のような方法が考えられる。

```python
from dataclasses import dataclass, field, _MISSING_TYPE
@dataclass
class Record:
    id: int
    sid: int
    _: None = field(default=None, metadata={'PK':'id sid'})
```

　`_`のポイントは以下。

* 複数列制約プロパティの名は`_`とする
* `_`の型は`None`とする（別に何でもいいが不要なので）
	* 型アノテーションを書かないと`TypeError`になる
* `_`は最後につける（さもなくば後続もdefault値が必須になってしまう）
* `_`には`default`値をセットする（さもなくば生成時に値を与えねばならない）
* `_`の`default`値は`None`とする（別に何でもいいが不要なので）

　`UK`や`FK`も同じようにできるようにする。

```python
    _: int = field(metadata={'UK':'id sid'})
```
```sql
  constraint u unique(id, sid)
```
```python
    _: int = field(metadata={'FK':'id sid T'})
```
```sql
  constraint fk foreign key(id, sid) references T(id, sid))
```

### 複数列が関わるチェック制約

```sql
create table users(
  id integer not null,
  sid integer not null,
  constraint c1 check (id>=5 AND sid>=3)
);
```

　`id`と`sid`の2列を`AND`条件でチェックする。このように複数列もちいる場合、ひとつの列だけで定義できないため`constraint`句を用いる。

　`constraint`句をPythonのdatasetで定義するなら以下。

```python
from dataclasses import dataclass, field, _MISSING_TYPE
@dataclass
class Record:
    id: int
    sid: int
    _: int = field(metadata={'c1':'id>=5 and sid>=3'})
```

　`metadata`のキー名は`check`の`c`ではじめて適当に番号を振ったもの。`PK`,`UK`,`FK`の名前はそれぞれの句で使うため使用不可。それと重複しない名前なら何でもいい。

　ここまでなら何となくできそうに思えるが、SQL文はたくさんある。

# SQL文パターン

* `create table`
	* `名 型 制約`
	* `constraint 名 制約`
* `drop table`
* `select`
	* `[列名]`
	* `from`
		* `表名`
	* `where`
		* `[列名 演算子 値]`
		* `AND`/`OR`
		* `関数(引数)`
		* `副問合せ`
	* `group by`
		* `[列名]`
	* `order by`
		* `asc`/`desc`
		* `[列名]`
	* `join`
		* `[表L.列A 演算子 表R.列A]`
		* `AND`/`OR`
		* `関数(引数)`
		* `副問合せ`
* `insert`
	* `表名`
	* `[列名]`
	* `[値]`
* `update`
	* `表名`
	* `[列名]`
	* `[値]`
	* `where`
* `delete`
	* `from`
		* `表名`

　これらをすべてPythonで読みやすく書きやすいようラップすることができるか？　考えてみる。

```python
@dataclass
class Record:
    id: int

SqlBuilder.create_table(Record) #=> create table Record(id integer);
```

　`insert`文など値がいる文はpreperd statementを使う。数値はそのまま、文字列をシングルクォート、という差を吸収してくれる。また、BLOBはpreperdでやるしかない。`sqlite3.cursor.execute()`メソッドを使う。

```python
import sqlite3
con = sqlite3.connect('my.db')
cur = conn.cursor()
con.execute("insert into record values(?,?)", (1,'A'))
con.close()
```

　`con.execute`の引数2つを返すメソッドを作りたい。以下みたいに。

```python
con.execute(SqlBuilder.insert(Record(1,'A')))
```

　でも、他の文では明らかに情報不足。たとえば`update`文はある特定の行だけ更新するのが普通。そこで`where`句を使う。これを表現するならどうするか。

```python
con.execute(f"update record set id=?, name=? where id=?", (2,'A',1))
```

```python
con.execute(SqlBuilder.update(cols=Record(2,'A'), where=Record(id=1)))
```

　たしかに一見よさげ。でも、`age >= 18`みたいな演算子を含んだ条件式を表現したいときは？

```python
con.execute(f"update record set is_adult=? where id>=?", (1,18))
```

```python
con.execute(SqlBuilder.update(cols=Record(2,'A'), where=lambda r: 18 <= r.id))
```

　ラムダ式で表現できそう。でも、問題はそのラムダ式をどうやってSQL文に変えるか。頑張ればできるかもしれない。でも頑張りたくない。しかもこの記述ならSQLで書いたほうが短くわかりやすい。そうまでしてPython化する必要あるか？

　パフォーマンスを無視するなら、全件取得したあとでラムダ式の条件に一致するレコードだけに絞ることも考えられる。でもそれはやりたくない。膨大なDBから全件取得なんて悪夢でしかない。

　もういっそSQL文は生のテキストで書いてしまえばいいのでは？

　問題は何だったか思い出してみる。`select`したとき行と列がすべて配列であり、1行目2列目のname列を取り出すとき`rows[0][1]`と書かねばならないことだ。これを`rows[0]['name']`としたい。もっといえば`rows[0].name`で参照できるようにしたい。できれば以下のパターンすべてに対応したい。

```python
rows[0][0]
rows[0]['id']
rows[0].id
getattr(rows[0], 'id')
rows[0,0]
rows[0,'id']
```

　`rows[0].name`にしたいなら`namedtuple`を使う。

```sql
con.row_factory = sqlite3.Row
rows = con.executes("select id, name from users;")
Row = namedtuple('Row', rows.keys())
return [Row(*row) for rwo in rows]
```

　`sqlite3.cursor.row_factory`を使って型変換する方法もある。標準実装されている`sqlite3.Row`を使えば`rows[0]['name']`のように文字列キーで参照できるようになる。

```python
con.row_factory = sqlite3.Row
```

　動作確認したコードは以下。

```python
import sqlite3
from collections import namedtuple
con = sqlite3.connect(':memory:')
con.row_factory = sqlite3.Row
cur = con.cursor()
print(con.execute("create table users(id integer, name text);"))
print(con.execute("insert into users values(0, 'A');"))
print(con.execute("insert into users values(1, 'B');"))
print(con.execute("select count(*) from users;").fetchone().keys())
print(con.execute("select count(*) num from users;").fetchone().keys())
print(con.execute("select count(*) num from users;").fetchone()['num'])
print(con.execute("select count(*) num from users;").fetchall())
#rows = con.execute("select count(*) from users;").fetchall() # ValueError: Type names and field names must be valid identifiers: 'count(*)'
#rows = con.execute("select count(*) num from users;").fetchall()
rows = con.execute("select count(*) num from users where id>=?;", (0,)).fetchall()
print(rows[0].keys())
print(rows[0])
print(rows[0][0])
#print(rows[0]['name']) #IndexError: No item with that key
Row = namedtuple('Row', rows[0].keys())
print([Row(*row) for row in rows])
#con.commit()
con.close()
```

　このへんの知識を使ってどうにか薄いラッパーを作りたい。

# 所感

　結局dataclass使ってない。namedtupleで十分。

