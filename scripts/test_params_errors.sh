#!/bin/sh
# Некорректные параметры: эмулятор должен завершаться с ошибкой.
. "$(dirname "$0")/lib.sh"

echo "== неизвестный параметр"
fails "--bogus отклонён" --bogus

echo "== параметры без значения"
fails "--vfs без значения" --vfs
fails "--log без значения" --log
fails "--script без значения" --script

echo "== недоступный лог-файл при остальных параметрах"
fails "лог в несуществующей папке" --vfs /path/to/vfs.xml \
    --log /no/such/dir/log.xml --script scripts/startup_ok.emu
has "$TMP/stderr.txt" "лог-файл" "сообщение об ошибке лога"

finish
