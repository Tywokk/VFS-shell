#!/bin/sh
# XML-лог: события, время, аргументы, ошибка; остановка скрипта на ошибке.
. "$(dirname "$0")/lib.sh"
VFS=/path/to/vfs.xml

echo "== скрипт без ошибок: все параметры"
run_emulator --vfs "$VFS" --log "$TMP/ok.xml" \
    --script scripts/startup_ok.emu > /dev/null
has "$TMP/ok.xml" "<command>ls</command>" "в логе есть ls"
has "$TMP/ok.xml" "<arg>-l</arg>" "в логе есть аргумент"
has "$TMP/ok.xml" "<time>" "в логе есть дата и время"
hasnt "$TMP/ok.xml" "<error>" "ошибок в логе нет"

echo "== скрипт с ошибкой: все параметры"
run_emulator --vfs "$VFS" --log "$TMP/err.xml" \
    --script scripts/startup_error.emu > /dev/null
has "$TMP/err.xml" "<command>cd</command>" "команды до ошибки выполнены"
has "$TMP/err.xml" "<error>foo: команда не найдена</error>" \
    "ошибка записана в лог"
hasnt "$TMP/err.xml" "after_error" "после ошибки скрипт остановлен"

finish
