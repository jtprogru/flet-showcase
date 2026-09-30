#!/bin/sh
# Скачивает сборку витрины под текущую ОС и архитектуру из GitHub Releases,
# сверяет контрольную сумму и устанавливает приложение.
#
#   install.sh            последняя версия
#   install.sh v2.1.0     конкретная версия
#
# macOS: ~/Applications/flet-showcase.app
# Linux: ~/.local/opt/flet-showcase, команда ~/.local/bin/flet-showcase
# Каталоги меняются через INSTALL_DIR и BIN_DIR, репозиторий через REPO.

set -eu

REPO="${REPO:-jtprogru/flet-showcase}"
VERSION="${1:-latest}"
APP=flet-showcase

fail() {
    echo "Ошибка: $*" >&2
    exit 1
}

case "$(uname -s)" in
    Darwin) os=macos ;;
    Linux) os=linux ;;
    *) fail "$(uname -s) не поддерживается, для Windows есть scripts/install.ps1" ;;
esac

case "$(uname -m)" in
    x86_64 | amd64) arch=x64 ;;
    arm64 | aarch64) arch=arm64 ;;
    *) fail "архитектура $(uname -m) не поддерживается" ;;
esac

# Терминал под Rosetta показывает x86_64 на Apple Silicon: берём нативную сборку.
if [ "$os" = macos ] && [ "$arch" = x64 ] &&
    [ "$(sysctl -in sysctl.proc_translated 2> /dev/null)" = 1 ]; then
    arch=arm64
fi

if [ "$os" = macos ]; then
    asset="$APP-$os-$arch.zip"
else
    asset="$APP-$os-$arch.tar.gz"
fi

if [ "$VERSION" = latest ]; then
    base="https://github.com/$REPO/releases/latest/download"
else
    case "$VERSION" in
        v*) ;;
        *) VERSION="v$VERSION" ;;
    esac
    base="https://github.com/$REPO/releases/download/$VERSION"
fi

download() {
    if command -v curl > /dev/null 2>&1; then
        curl -fL --progress-bar -o "$2" "$1"
    elif command -v wget > /dev/null 2>&1; then
        wget -q --show-progress -O "$2" "$1"
    else
        fail "нужен curl или wget"
    fi
}

sha256() {
    if command -v sha256sum > /dev/null 2>&1; then
        sha256sum "$1" | cut -d' ' -f1
    else
        shasum -a 256 "$1" | cut -d' ' -f1
    fi
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT INT TERM

echo "Скачиваю $asset ($VERSION)"
download "$base/$asset" "$tmp/$asset" || fail "не удалось скачать $base/$asset"
download "$base/SHA256SUMS.txt" "$tmp/SHA256SUMS.txt" ||
    fail "не удалось скачать SHA256SUMS.txt"

expected="$(awk -v f="$asset" '$2 == f { print $1 }' "$tmp/SHA256SUMS.txt")"
[ -n "$expected" ] || fail "в SHA256SUMS.txt нет строки для $asset"
[ "$(sha256 "$tmp/$asset")" = "$expected" ] || fail "контрольная сумма $asset не совпала"

if [ "$os" = macos ]; then
    install_dir="${INSTALL_DIR:-$HOME/Applications}"
    ditto -x -k "$tmp/$asset" "$tmp/unpacked"
    mkdir -p "$install_dir"
    rm -rf "${install_dir:?}/$APP.app"
    mv "$tmp/unpacked/$APP.app" "$install_dir/"
    echo "Готово: $install_dir/$APP.app"
    echo "Запуск: open \"$install_dir/$APP.app\""
else
    install_dir="${INSTALL_DIR:-$HOME/.local/opt/$APP}"
    bin_dir="${BIN_DIR:-$HOME/.local/bin}"
    mkdir -p "$tmp/unpacked"
    tar -xzf "$tmp/$asset" -C "$tmp/unpacked"
    mkdir -p "$(dirname "$install_dir")" "$bin_dir"
    rm -rf "$install_dir"
    mv "$tmp/unpacked/$APP" "$install_dir"
    ln -sf "$install_dir/$APP" "$bin_dir/$APP"
    echo "Готово: $install_dir"
    echo "Запуск: $bin_dir/$APP"
fi
