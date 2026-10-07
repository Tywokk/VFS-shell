#!/bin/sh
# Общие функции скриптов проверки. Подключается строкой: . "$(dirname "$0")/lib.sh"
# Нужен дисплей; без него: RUNNER="xvfb-run -a" sh scripts/<скрипт>.sh

cd "$(dirname "$0")/.." || exit 1
RUNNER="${RUNNER:-}"
LIMIT="${LIMIT:-3}"
TMP="$(mktemp -d)"
FAILS=0

run_emulator() {
    timeout "$LIMIT" $RUNNER python3 -m src.main "$@"
}

report() {
    if [ "$1" = ok ]; then
        echo "OK:   $2"
    else
        echo "FAIL: $2"
        FAILS=$((FAILS + 1))
    fi
}

has() {
    if grep -q -- "$2" "$1"; then report ok "$3"; else report bad "$3"; fi
}

hasnt() {
    if grep -q -- "$2" "$1"; then report bad "$3"; else report ok "$3"; fi
}

fails() {
    desc="$1"
    shift
    if python3 -m src.main "$@" > /dev/null 2> "$TMP/stderr.txt"; then
        report bad "$desc"
    else
        report ok "$desc"
    fi
}

check_vfs() {
    run_emulator --vfs "$1" --log "$TMP/log.xml" \
        --script scripts/startup_ok.emu > "$TMP/out.txt"
    has "$TMP/out.txt" "vfs    = $1" "параметр --vfs: $1"
    has "$TMP/out.txt" "$2" "$3"
    has "$TMP/log.xml" "<command>tree</command>" "команда tree выполнена"
}

finish() {
    rm -rf "$TMP"
    echo "Провалено проверок: $FAILS"
    [ "$FAILS" -eq 0 ]
}
