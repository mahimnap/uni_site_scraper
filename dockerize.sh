# Declaring functions
print_green () {
   echo -e "\e[1;32m$1 \e[0m"
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

print_cyan "This is a script that performs the docker setup, visit the readme for more information\n"

# Checking if currently in the correct directory
if [[ `ls | grep "dockerize.sh"` == "" ]]; then
	print_red "Must be run from the root of the repository"
	exit
fi

# Checking if docker is installed, if not then installing
print_yellow "Checking if docker is installed..."
if [[ `docker -v | grep "command not found"` -ne "" ]]; then
   print_red "Docker is not currently installed, installing..."
   print_yellow "Checking machine OS..."

   if [[ `hostnamectl | grep "Debian"` -ne "" ]]; then
      print_green "Found Debian, installing docker for Debian...\n"

      # Uninstall old versions
      sudo apt-get remove docker docker-engine docker.io containerd runc -y

      # Update the apt package index and install packages to allow apt to use a repository over HTTPS
      sudo apt-get update -y
      sudo apt-get install ca-certificates -y
      sudo apt-get install curl -y
      sudo apt-get install gnupg -y
      sudo apt-get install lsb-release -y

      # Add Docker’s official GPG key
      curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
      echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

      # Update the apt package index, and install the latest version of Docker Engine and containerd
      sudo apt-get update -y
      sudo apt-get install docker-ce docker-ce-cli containerd.io -y
   
      print_green "Docker has been installed for Debian\n"
   elif [[ `hostnamectl | grep "Ubuntu"` -ne "" ]]; then
      print_green "Found Ubuntu, installing docker for Ubuntu...\n"

      # Uninstall old versions
      sudo apt-get remove docker docker-engine docker.io containerd runc -y

      # Update the apt package index and install packages to allow apt to use a repository over HTTPS
      sudo apt-get update -y
      sudo apt-get install ca-certificates -y
      sudo apt-get install curl -y
      sudo apt-get install gnupg -y
      sudo apt-get install lsb-release -y

      # Add Docker’s official GPG key
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
      echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

      # Update the apt package index, and install the latest version of Docker Engine and containerd
      sudo apt-get update -y
      sudo apt-get install docker-ce docker-ce-cli containerd.io -y
   
      print_green "Docker has been installed for Ubuntu\n"
   elif [[ `hostnamectl | grep "Fedora"` -ne "" ]]; then
      print_green "Found Fedora, installing docker for Fedora...\n"

      # Uninstall old versions
      sudo dnf remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-selinux docker-engine-selinux docker-engine

      # Setting up the repository
      sudo dnf -y install dnf-plugins-core
      sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
      
      # Install the latest version of Docker Engine and containerd
      sudo dnf install docker-ce docker-ce-cli containerd.io
   
      # Launching docker process
      sudo systemctl start docker

      print_green "Docker has been installed for Fedora\n"
   elif [[ `hostnamectl | grep "CentOS"` -ne "" ]]; then
      print_green "Found CentOS, installing docker for CentOS...\n"

      # Uninstall old versions
      sudo yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine

      # Setting up the repository
      sudo yum install -y yum-utils
      sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
      
      # Install the latest version of Docker Engine and containerd
      sudo yum install docker-ce docker-ce-cli containerd.io

      # Launching docker process
      sudo systemctl start docker
   
      print_green "Docker has been installed for CentOS\n"
   elif [[ `hostnamectl | grep "Mac"` -ne "" ]]; then
      print_green "Found MacOS, installing docker for MacOS...\n"

      print_red "ERROR - Docker cannot be installed for MacOS through the CLI, aborting\n"
      exit
   fi
else
   print_green "Docker is already installed\n"
fi

print_yellow "Preparing container to be ran...\n"

# Starting docker processes
print_yellow "Starting docker daemon processes..."
sudo systemctl start docker
sudo systemctl start docker.socket
sudo systemctl start containerd
print_green "Successfully started docker daemon processes...\n"

# Deleting old image if it already exists and pruning to remove unused containers and images to save space
print_yellow "Deleting unused and old containers/images..."
sudo docker image rm -f w22_cis_3760_team1_image
sudo docker container prune
sudo docker image prune
print_green "Successfully deleted unused and old containers/images\n"

# Creating new image
print_yellow "Creating new docker image from dockerfile..."
sudo docker build -t w22_cis_3760_team1_image .
print_green "Successfully created new docker image\n"

# Getting a port to run the container with
print_yellow_no_newline "Enter a port to map the container to (default 5000): "
read container_port
if [ "$container_port" == "" ]; then
    container_port="5000"
fi
print_green "Container port has been configured\n"

# Running the container
print_yellow "Running the docker image, creating new container..."
sudo docker run -d -p$container_port:5000 --name w22_cis_3760_team1_container w22_cis_3760_team1_image
print_green "New container is now running"