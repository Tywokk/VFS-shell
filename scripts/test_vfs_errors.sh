#!/bin/sh
# Ошибки VFS: эмулятор сообщает о них и не открывает окно.
. "$(dirname "$0")/lib.sh"

echo "== файл VFS не найден"
fails "несуществующий файл" --vfs vfs/no_such_file.xml
has "$TMP/stderr.txt" "Ошибка VFS" "сообщение об ошибке VFS"

echo "== некорректный XML"
fails "битый XML" --vfs vfs/broken.xml
has "$TMP/stderr.txt" "Ошибка VFS" "сообщение об ошибке VFS"

finish
