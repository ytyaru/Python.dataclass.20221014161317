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

　ORMを書くときに使えそう。SQLite3のようなRDBMSのレコードをPythonの型として表現する。

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

　以下で中身が見れる。このうち`__annotations__`や`__dataclass_fields__`でメタデータが見れる。

```python
print(dir(Record))
```
```python
['__annotations__', '__class__', '__dataclass_fields__', '__dataclass_params__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__match_args__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__']
```
```python
print(Record.__annotations__)
```
```python
{'id': <class 'int'>, 'name': <class 'str'>, 'birth': <class 'datetime.datetime'>, 'value': <class 'decimal.Decimal'>}
```
```python
print(Record.__dataclass_fields__)
```
```python
{'id': Field(name='id',type=<class 'int'>,default=<dataclasses._MISSING_TYPE object at 0xb6a60b68>,default_factory=<dataclasses._MISSING_TYPE object at 0xb6a60b68>,init=True,repr=True,hash=None,compare=True,metadata=mappingproxy({}),kw_only=False,_field_type=_FIELD), 'name': Field(name='name',type=<class 'str'>,default=<dataclasses._MISSING_TYPE object at 0xb6a60b68>,default_factory=<dataclasses._MISSING_TYPE object at 0xb6a60b68>,init=True,repr=True,hash=None,compare=True,metadata=mappingproxy({}),kw_only=False,_field_type=_FIELD), 'birth': Field(name='birth',type=<class 'datetime.datetime'>,default=<dataclasses._MISSING_TYPE object at 0xb6a60b68>,default_factory=<dataclasses._MISSING_TYPE object at 0xb6a60b68>,init=True,repr=True,hash=None,compare=True,metadata=mappingproxy({}),kw_only=False,_field_type=_FIELD), 'value': Field(name='value',type=<class 'decimal.Decimal'>,default=<dataclasses._MISSING_TYPE object at 0xb6a60b68>,default_factory=<dataclasses._MISSING_TYPE object at 0xb6a60b68>,init=True,repr=True,hash=None,compare=True,metadata=mappingproxy({}),kw_only=False,_field_type=_FIELD)}
```

　このメタデータを使えばSQL文を作成することもできるのでは？

　というわけで、dataclassの挙動を確認してみる。

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

　キーワード引数にすれば指定したプロパティだけデフォルト以外の値を指定することもできる。

```sh
Record(id=0, name='', birth=datetime.datetime(...), value=Decimal('0.0'))
Record(id=1, name='A', birth=datetime.datetime(...), value=Decimal('0.0'))
Record(id=0, name='B', birth=datetime.datetime(...), value=Decimal('9.9'))
```

## 一部だけオプション

　制約がある。

　あるプロパティにデフォルト値をセットしたら、それ以降にあるプロパティにもデフォルト値をセットせねばならない。

　たとえば以下のようなことはできない。

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

## `id`

　列名が`id`かつ型が整数のときは問答無用で`primary key`制約をつけていいかもしれない。RDBMSはその性質上、レコードを一意に特定するためのキーとなる列が必須である。その名前は大抵`id`。なので列名が`id`なら`primary key`をつけるくらいでいい。

## `FK`

　外部キーは親となる表と列の名前が必要。それを`表名 列名`という半角スペース区切りのテキストで渡す。区切り文字に関しては考えると複雑。SQLのFK的には`表名(列名)`となる。SQLのselect文では`表名.列名`となる。でも面倒なのですべての構文における区切り文字スペースを使うことにした。

## `not null`

　すべての項目は`not null`をつける。もしNULLをつけたい列があればNullable項目として`metadata={'N':True}`と指定するようにする。

　NULL参照エラー。NULLポインタエラー。日本では「ぬるぽ」の愛称で親しまれる悪しき存在。これは害悪である。

　NULL参照は10億ドルの損失を生む過ちだった。1965年に考案されたNULLの概念は、後に無数のNULL参照エラーという致命的なバグやクラッシュを引き起こす原因となった。NULLは10億ドルの損失や労力を生み出した悪しき存在となった。そう開発者のアントニー・ホーア氏が語った。

　ぬるぽのない世界をめざす。かくして世はNULL安全言語が礼賛される時代となった。NULLがある言語は`??`演算子などでNULLをうまいこと回避する術を提供する機能を実装した。さらにRustなどの新しい言語ではNULL自体が存在しない作りになり、完全にぬるぽを抹殺せしめた。

　データベースの世界でもNULLの悪名高さは有名。[NULL撲滅委員会][]なるものさえあった。

[NULL撲滅委員会]:http://mickindex.sakura.ne.jp/database/db_getout_null.html

　とにかくNULLには消えてもらいたいのが現代の総意である。今まで散々こき使ってきたくせに突然ポイ捨てされるのも哀れだが、そういう流れなのだ。

　というわけでSQLでcreate tableするときは`not null`制約をデフォルトでつけることにする。

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


## もっとシンプルに書きたい

　必要な要素は限りなく少ない。

```
id int PK
name str UK
sid int FK
birth dt = NOW
nullable str N
is_delete bool
```

　SQLite3の型だけに絞れば1字で表現できる。できれば省略したときは`TEXT`としたいが、後続の制約と区別がつかなくなりそう。

略|SQLite3型|意味
--|---------|----
`n`|`NULL`|NULL
`i`|`INTEGER`|整数
`r`|`REAL`|浮動小数点数
`b`|`BLOB`|バイナリ
`t`|`TEXT`|テキスト

key|type|value|意味(SQLキーワード)
---|----|-----|-------------------
`p`,`pk`|bool|`True`/`False`|`primary key`
`u`,`uk`|bool|`True`/`False`|`unique`
`f`,`fk`|str|`表名 列名`|`references t(c)`
`n`,`nl`|bool|`True`/`False`|`not null`を外す
`d`,`df`|str|`デフォルト値`|`default デフォルト値`
`c`,`ck`|str|`条件式`|`check(条件式)`

　ついでに`AUTOINCREMENT`は`a`で表現する。重複もしない。

略|SQLite3型|意味
--|---------|----
`a`|`AUTOINCREMENT`|一度使用したIDを二度と使わない（DELETEしたIDは永久欠番）


　`n`だけが重複する。ひとつの列あたり次の4パターンありうる。

* `名 型 制`
* `名 型`
* `名 制`
* `名` 

　このうち`n`が重複するので`id n`としたとき`n`は型なのか制約なのか判断がつかない。

　もっとも、型を`NULL`にすることは考えにくい。それは非対応にすればいいか。これで`n`は制約の`not null`を外してNullableな列であることを表せる。

　複数列が関わる制約については以下。`+PK`のようにプレフィクスを付けて列名でないことを示す。プレフィクスは何でもいいが列名で使える記号`[a-zA-Z_]`以外で、かつ絶対に名前として使わなそうな字にしたい。それでいて制約を付与することがイメージできる字がよい。

```
id int
name str
sid int
birth dt = NOW
nullable str N
+PK id sid
+UK id sid
+FK id sid TableName
+CK id<5 && sid<3
```

　`WITHOUT_ROWID`テーブルを作るときは以下。

```
-ID
```

# 所感

　実装はまた今度。ちょっと大変そう。


# SQL化

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

　たとえば以下のような。

```python
@dataclass
class Record:
    id: int

SqlBuilder.create_table(Record) # create table Record(id integer);
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

　もういっそSQL文は生のテキストで書いてしまえばいいのでは？

　問題は何だったか思い出してみる。`select`したとき行と列がすべて配列であり、1行目2列目のname列を取り出すとき`rows[0][1]`と書かねばならないことだ。これを`rows[0]['name']`としたい。もっといえば`rows[0].name`で参照できるようにしたい。

　しかも指定する列はそのときのSQL文にあわせる。

```python
cols = (1,)
where = (18,)
con.execute(f"update record set is_adult=? where id>=?", (cols + where))
```

　以下でどうか。`update set`と`列名=?`を書かずに済む。ただし`where`句は条件による演算子があるため文字列として表現せざるを得ない。

```python
from collections import namedtuple
user = namedtuple('users' , 'id name')
user.id = 2
user.name = 'B'
SqlBuilder.update(user, where="id>=? and name=?", order_by="id asc, name desc", data=(1, 'A'))
```

　order_byを少しだけ略記。

```python
from collections import namedtuple
user = namedtuple('users' , 'id name')
user.id = 2
user.name = 'B'
SqlBuilder.update(user, where="id>=? and name=?", order_by="+id -name", data=(1, 'A'))
```

　条件もすべて`namedtuple`の値として表現してしまう。型名もいれることで`where`句, `order_by`句であることを区別させる。`update`の第一引数だけは`set`句であるとし、以降はオプション。namedtuple型を期待し、その型名で何の句であるか判断する。最後にタプルまたはタプルの配列だったらそれが`?`にセットする値とする。ただし第一引数`set`のほうは条件式がないので値をそのままセットする。あとは内部でよろしくやる。なので最後の引数は`where`句などで使う`?`にセットする分だけ書けばいい。

```python
from collections import namedtuple
user = namedtuple('users' , 'id name')
user.id = 2
user.name = 'B'
where = namedtuple('where' , 'id name')
where.id = '>=?'
where.name = '=?'
order_by = namedtuple('order_by' , 'id name')
order_by.id = 'asc'
order_by.name = 'desc'
SqlBuilder.update(user, where, order_by, (1, 'A'))
```

　よくまとまったけど、わかりにくい。書きにくい。

　やはりSQL文はそのまま書いたほうがよさそう。`select`文の戻り値だけ`namedtuple`か`dataclass`にすればいいか。

　ところで、`select`文の結果は必ずしもテーブル定義のような列にならない。たとえば取得する列を何にするかで変わってしまう。列が減ったり増えたりする。`select name from ...`のようにしたり、`select group_id, sum(value) from ... group by group_id;`のようにテーブルにはない`sum`列が追加されたり。

　なので`select`の結果は動的に生成したい。`namedtuple`, `dataclass`どちらも可能だが、型が不要な`namedtuple`のほうが作りやすそう。どうせPythonで静的型チェックなんてできないのだから`namedtuple`のほうが優秀。

```python
user = namedtuple('users' , 'id name')
user.id = 1
user.name = 'A'

db = ntlite('my.db')

db.get()
db.gets()
db.count()
db.exists()
db.exec('create table')
db.exec('select * from ')
```

　実装するのは難しそう。

```sql
@dataclass
class Record:
    id: int
    name: str

select name from table;
```







```python
cols = (1,)
where = (18,)
con.execute(f"update {table} set {col1}=?, {col2}=?, ... where id>=?", (cols + where))
```

```sql
update {table} set {col1}=?, {col2}=?, ... where id>=? and name=? order by {col} asc
```

```sql
update {table} set {col1}=?, {col2}=?, ... where {col}{op}? and name=? order by {col} asc
```

* テーブル名はクラス名から取得する
* 列名はプロパティ名から取得する
* 列に代入する値はプロパティ値で取得する
* `where`
* `order by`

　SQLを同じメソッドで作成するとき次のような問題がある。

* シングルクォート有無問題（整数はなし。テキストは必要）
	* BLOBはpreperd必須
	* preperdはクォート問題を解決する
	* preperdは必須
		* preperdは?の数だけ値が必要
		* 対応する列と紐付いていない
		* 対応する列との間に演算子がある





```python
con.execute(SqlBuilder.update(cols=Record(2,'A'), where=lambda r: 18 <= r.id))
```





































```python
@dataclass
class Record:
    id: int
    name: str
    birth: datetime = datetime.now()
    value: Decimal = Decimal('0.0')

if __name__ == '__main__':
    print(Record())
    print(Record(1, 'A'))
    print(Record(name='B', value=Decimal('9.9')))
```


```python
@dataclass
class Record:
    id: int
    name: str
    birth: datetime = datetime.now()
    value: Decimal # TypeError: non-default argument 'value' follows default argument
```

# mypyをインストールする

```sh
pip install mypy
```

　テスト用コードを書く。

```python
from dataclasses import dataclass, field
@dataclass
class Record:
    item_ids: list[int]

Record([1,2,3])
Record(['A','B']) # ここでエラーになってほしい
```

　実行する。20秒くらいかかる。

```sh
$ mypy record.py
```
```sh
record.py:7: error: List item 0 has incompatible type "str"; expected "int"
record.py:7: error: List item 1 has incompatible type "str"; expected "int"
Found 2 errors in 1 file (checked 1 source file)
```

　OK！　問題箇所のファイル名、行数、位置もメッセージから読み取れる。エラーの理由も英語だけど書いてる。

　これをPython標準で実装してほしかった。


