[en](./README.md)

# dataclass

　dataclassの動作確認をする。

# デモ

* [demo](https://ytyaru.github.io/Python.dataclass.20221014161317/)

![img](https://github.com/ytyaru/Python.dataclass.20221014161317/blob/master/doc/0.png?raw=true)

# 特徴

* セールスポイント

# 開発環境

* <time datetime="2022-10-14T16:13:14+0900">2022-10-14</time>
* [Raspbierry Pi](https://ja.wikipedia.org/wiki/Raspberry_Pi) 4 Model B Rev 1.2
* [Raspberry Pi OS](https://ja.wikipedia.org/wiki/Raspbian) buster 10.0 2020-08-20 <small>[setup](http://ytyaru.hatenablog.com/entry/2020/10/06/111111)</small>
* bash 5.0.3(1)-release
* Python 2.7.16
* Python 3.10.5
* [pyxel][] 1.3.1

[pyxel]:https://github.com/kitao/pyxel

```sh
$ uname -a
Linux raspberrypi 5.10.103-v7l+ #1529 SMP Tue Mar 8 12:24:00 GMT 2022 armv7l GNU/Linux
```

# インストール

　3.7以上のPythonをインストールする。

　次に以下のように[pyxel][]をインストールする。

* [pyxel/README](https://github.com/kitao/pyxel/blob/master/README.ja.md#%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB%E6%96%B9%E6%B3%95)

```sh
sudo apt install python3 python3-pip libsdl2-dev libsdl2-image-dev
git clone https://github.com/kitao/pyxel.git
cd pyxel
make -C pyxel/core clean all
pip3 install .
```

# 使い方

```sh
git clone https://github.com/ytyaru/Python.dataclass.20221014161317
cd Python.dataclass.20221014161317/src
./run.py
```

# 注意

* 注意点など

# 著者

　ytyaru

* [![github](http://www.google.com/s2/favicons?domain=github.com)](https://github.com/ytyaru "github")
* [![hatena](http://www.google.com/s2/favicons?domain=www.hatena.ne.jp)](http://ytyaru.hatenablog.com/ytyaru "hatena")
* [![twitter](http://www.google.com/s2/favicons?domain=twitter.com)](https://twitter.com/ytyaru1 "twitter")
* [![mastodon](http://www.google.com/s2/favicons?domain=mstdn.jp)](https://mstdn.jp/web/accounts/233143 "mastdon")

# ライセンス

　このソフトウェアはCC0ライセンスである。

[![CC0](http://i.creativecommons.org/p/zero/1.0/88x31.png "CC0")](http://creativecommons.org/publicdomain/zero/1.0/deed.ja)

