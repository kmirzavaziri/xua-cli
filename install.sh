#!/bin/bash
if [ $EUID -ne 0 ]; then
    echo -e "You need to have root privileges to run this script.\nPlease run 'sudo ./install.sh'."
    exit
fi

SOURCE_XUA_DIR=$(dirname "$0")
XUA_CLI_DIR=/usr/bin/xua-cli
CLI_DIR=/usr/bin

mkdir -p $XUA_CLI_DIR
rm -rf $XUA_CLI_DIR
cp -r $SOURCE_XUA_DIR/xua $XUA_CLI_DIR
ln -sf $XUA_CLI_DIR/xua $CLI_DIR/xua