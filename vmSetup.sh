#!/bin/bash
print_green () {
   echo -e "\e[1;32m$1 \e[0m"
}

print_yellow () {
   echo -e "\e[1;33m$1 \e[0m"
}

print_red () {
   echo -e "\e[1;31m$1 \e[0m"
}

print_cyan () {
   echo -e "\e[1;36m$1 \e[0m"
}

if ! command -v pip3 -V &> /dev/null; then
   sudo apt install python3-pip -y
fi

pip3 freeze > currently_installed.txt
cat requirements.txt | while read line; do
if [ "$(cat currently_installed.txt | grep "$line")" == "" ]; then
   pip3 install "$line"
fi
done

print_yellow "\nInstalling Playwright..."
if ! command -v playwright -V &> /dev/null; then
   playwright install
else
   print_green "Playwright is already installed"
fi

print_yellow "\nInstalling Chromium..."
if ! command -v chromium --product-version &> /dev/null; then
   sudo apt-get install chromium -y
else
   print_green "Chromium is already installed"
fi

print_yellow "\nInstalling Graphviz..."
if ! command -v dot -V &> /dev/null; then
   sudo apt-get install graphviz -y
else
   print_green "Graphviz is already installed"
fi

print_yellow "\nInstalling Npm..."
if ! command -v npm -v &> /dev/null; then
   sudo apt-get install npm -y
else
   print_green "Npm is already installed\n"
fi

rm currently_installed.txt
