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
   
   print_green "Docker has been installed\n"
else
   print_green "Docker is already installed\n"
fi

print_yellow "Preparing container to be ran..."

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
sudo docker run -d -p$container_port:5000 --name w22_cis_3760_team1_image dpdr
print_green "New container is now running"