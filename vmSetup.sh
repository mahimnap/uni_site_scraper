#!/bin/bash

if ! command -v pip3 -V &> /dev/null; then
   sudo apt install python3-pip -y
fi

pip3 freeze > currently_installed.txt
cat requirements.txt | while read line; do
if [ "$(cat currently_installed.txt | grep "$line")" == "" ]; then
   pip3 install "$line"
fi
done

if ! command -v playwright -V &> /dev/null; then
   playwright install
fi

if ! command -v chromium --product-version &> /dev/null; then
   sudo apt-get install chromium -y
fi

if ! command -v dot -V &> /dev/null; then
   sudo apt-get install graphviz -y
fi

if ! command -v npm -v &> /dev/null; then
   sudo apt-get install npm
fi

rm currently_installed.txt
