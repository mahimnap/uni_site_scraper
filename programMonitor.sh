#!/bin/bash

# Declaring functions
print_green () {
   echo -e "\e[1;32m$1 \e[0m"
}

print_yellow () {
   echo -e "\e[1;33m$1 \e[0m"
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

# Main code
print_cyan "Running program monitor run script...\n"

# Checking if in the correct directory
if [[ `ls | grep "programMonitor.sh"` == "" ]]; then
	print_red "Must be run from the root of the repository"
	exit
fi

# Running the program if it's running
if [[ `ps aux | grep "program_monitor_client.py" | wc -l` > 2 ]]; then
	print_red_no_newline "Program monitor is already running, restart (y/n)?"
   read restart_monitor

   if [[ $restart_monitor == "y" ]]; then
      print_yellow "\nKilling old program monitor process"
      pkill -9 -f program_monitor_client 2>&1 </dev/null &
      print_yellow "Launching new program monitor process"
      cd test/program_monitor
      python3 program_monitor_client.py 2>&1 </dev/null &
      print_green "\nProgram monitor has been restarted"

   elif [[ $restart_monitor == "n" ]]; then
      print_red_no_newline "Would you like to shut it down (y/n)?"
      read restart_monitor_shutdown

      if [[ $restart_monitor_shutdown == "y" ]]; then
         print_yellow "Killing the program monitor process"
         pkill -9 -f program_monitor_client 2>&1 </dev/null &
         print_green "\nProgram monitor has been shut down"
      elif [[ $restart_monitor_shutdown == "n" ]]; then
         print_green "\nProgram monitor has not been shut down"
      fi
   fi
else
   print_red "Program monitor is not currently running"

   print_yellow "Launching new program monitor process"
   cd test/program_monitor
   python3 program_monitor_client.py 2>&1 </dev/null &

   print_green "\nProgram monitor has been launched"
fi