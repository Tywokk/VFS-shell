#!/bin/sh
# Варианты VFS: по умолчанию, минимальная, несколько файлов, глубокая.
. "$(dirname "$0")/lib.sh"

echo "== без --vfs: VFS по умолчанию в памяти"
run_emulator --log "$TMP/log.xml" --script scripts/startup_ok.emu \
    > "$TMP/out.txt"
has "$TMP/out.txt" "vfs    = (не задан)" "параметр --vfs не задан"
has "$TMP/out.txt" "каталогов: 1, файлов: 2" "создана VFS по умолчанию"

echo "== минимальная VFS: один файл"
check_vfs vfs/minimal.xml "каталогов: 0, файлов: 1" "загружен один файл"

echo "== несколько файлов, включая base64"
check_vfs vfs/several_files.xml "каталогов: 0, файлов: 4" "загружено 4 файла"

echo "== вложенность в три и более уровня"
check_vfs vfs/deep.xml "каталогов: 5, файлов: 5" "загружено дерево каталогов"

finish
