#!/usr/bin/env bash
#set -Ceu
set -Cu
#---------------------------------------------------------------------------
# mypyをインストールして確認用コードでエラー表示する。
# 前提条件としてpyenvで3.5以上のPythonをインストールしている必要がある。
# もしpyenvがなくシステムのPythonならpipの前にsudoなど管理者用コマンドが必要。
# CreatedAt: 2022-10-14
#---------------------------------------------------------------------------
Run() {
	THIS="$(realpath "${BASH_SOURCE:-0}")"; HERE="$(dirname "$THIS")"; PARENT="$(dirname "$HERE")"; THIS_NAME="$(basename "$THIS")"; APP_ROOT="$PARENT";
	cd "$HERE"
	IsExistCmd() { type "$1" > /dev/null 2>&1; }
	Install() { IsExistCmd "$1" || pip install "$1"; }
	Install mypy
	echo '----- mypyを実行する(1件あたり20秒くらいかかる) -----'
	#for file in {test-data-class-1.py,test-data-class-2.py}; do
	while read file; do
		echo "----- $file -----"
		mypy "$file"
		python "$file"
	done < <(find . -name '*.py' | sort)
	echo '===== テスト完了 ====='
}
Run "$@"
