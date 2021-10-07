# Xua Command-Line Interface
Website: http://xuarizmi.ir/

Documentations: http://xuarizmi.ir/docs/

Documentations Repo: https://github.com/kmirzavaziri/xua-doc

## Installation
 - Install `pip`
```
sudo apt install python3-pip
```
 - Add `pip` packages directory to `PATH`
```
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then PATH="$HOME/.local/bin${PATH:+":$PATH"}"; fi
```
 - Install `xua`
```
pip install -e git+https://github.com/kmirzavaziri/xua-cli/#egg=xua
```
