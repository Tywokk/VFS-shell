#!/bin/sh
# Каждый параметр (--vfs, --log, --script) отдельно и все три вместе.
# Окно без стартового скрипта остаётся открытым, его закрывает таймаут.
. "$(dirname "$0")/lib.sh"
VFS=vfs/minimal.xml

echo "== --vfs отдельно"
run_emulator --vfs "$VFS" > "$TMP/o1.txt"
has "$TMP/o1.txt" "vfs    = $VFS" "debug: vfs выведен"
has "$TMP/o1.txt" "log    = (не задан)" "debug: log не задан"

echo "== --log отдельно"
run_emulator --log "$TMP/l2.xml" > "$TMP/o2.txt"
has "$TMP/o2.txt" "log    = $TMP/l2.xml" "debug: log выведен"
has "$TMP/l2.xml" "<events" "лог-файл создан при запуске"

echo "== --script отдельно"
run_emulator --script scripts/startup_ok.emu > "$TMP/o3.txt"
has "$TMP/o3.txt" "script = scripts/startup_ok.emu" "debug: script выведен"

echo "== все три параметра"
run_emulator --vfs "$VFS" --log "$TMP/l4.xml" \
    --script scripts/startup_ok.emu > "$TMP/o4.txt"
has "$TMP/o4.txt" "vfs    = $VFS" "debug: vfs"
has "$TMP/o4.txt" "log    = $TMP/l4.xml" "debug: log"
has "$TMP/o4.txt" "script = scripts/startup_ok.emu" "debug: script"
has "$TMP/l4.xml" "<command>exit</command>" "скрипт дошёл до exit"

finish
