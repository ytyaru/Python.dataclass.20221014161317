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


