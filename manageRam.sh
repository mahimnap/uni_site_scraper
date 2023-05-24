#!/bin/bash
print_green () {
   echo -e "\e[1;32m$1 \e[0m"
}

print_green_no_newline () {
   echo -en "\e[1;32m$1 \e[0m"
}

print_yellow () {
   echo -e "\e[1;33m$1 \e[0m"
}

print_yellow_no_newline () {
   echo -en "\e[1;33m$1 \e[0m"
}

print_red () {
   echo -e "\e[1;31m$1 \e[0m"
}

print_red_no_newline () {
   echo -en "\e[1;31m$1 \e[0m"
}

print_cyan () {
   echo -e "\e[1;36m$1 \e[0m"
}

print_cyan "With this script, you can view how much memory is being used and how much is free"
print_cyan "You are also given the option to clear some memory by ending various VSCode and Docker processes"
print_red "NOTE: VSCode ssh sessions may disconnect if this script is used\n"

# Giving information on the amount of memory free
pre_memory_total=`free | grep Mem: | awk '{print $2}'`
pre_memory_used=`free | grep Mem: | awk '{print $3}'`
pre_memory_available=`free | grep Mem: | awk '{print $7}'`

print_yellow "Total Memory:\t $pre_memory_total bytes"
print_red "Memory Used:\t $pre_memory_used bytes"
print_green "Memory Free:\t $pre_memory_available bytes"

echo ""

# Begin memory clearing
print_yellow_no_newline "Would you like to perform some memory clearing? (y/n)"
performed_clear=0
read user_answer
echo ""
if [ "$user_answer" == "y" ]; then

      # Managing docker processes
      print_yellow_no_newline "(1/2) Would you like to stop the Docker processes? (y/n)"
      read user_answer
      if [ "$user_answer" == "y" ]; then
         performed_clear=1
         sudo systemctl stop docker
         sudo systemctl stop docker.socket
         sudo systemctl stop containerd
      fi

      # Managing vscode processes
      print_yellow_no_newline "(2/2) Would you like to stop the VSCode processes? (y/n)"
      read user_answer
      if [ "$user_answer" == "y" ]; then
         performed_clear=1
         pkill -9 -f vscode
      fi

      echo ""
      print_green "Memory was cleared"
   else
      print_red "No memory was cleared"
fi

# Giving information on the amount of memory free
post_memory_used=`free | grep Mem: | awk '{print $3}'`
memory_cleared="$((pre_memory_used-post_memory_used))"
if [ $memory_cleared -gt 0 ] && [ $performed_clear == 1 ]; then
   print_green "Total memory cleared through the script: $memory_cleared bytes"
fi