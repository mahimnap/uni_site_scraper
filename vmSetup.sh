
# Sprint 3
if [[ `pip3 -V | grep "command not found"` -ne "" ]]; then
   sudo apt install python3-pip -y
fi

pip3 freeze > currently_installed.txt
# diff currently_installed.txt requirements.txt > remainder.txt
cat requirements.txt | while read line; do
if [ "$(cat currently_installed.txt | grep "$line")" == "" ]; then
   pip3 install "$line"
fi
done

if [[ `playwright -V | grep "command not found"` -ne "" ]]; then
   playwright install
fi

if [[ `chromium --product-version | grep "command not found"` -ne "" ]]; then
   sudo apt-get install chromium -y
fi

if [[ `dot -V | grep "command not found"` -ne "" ]]; then
   sudo apt-get install graphviz -y
fi

# Sprint 5
if [[ `npm -v | grep "command not found"` -ne "" ]]; then
   sudo apt-get install npm
fi

rm currently_installed.txt