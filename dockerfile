# DOCKER COMMANDS
# sudo docker image rm -f testbuild                      DELETES OLD IMAGE
# sudo docker build -t testbuild .                       BUILDS IMAGE FROM THIS DOCKERFILE
# sudo docker run -d --name testcontainer testbuild      CREATES A CONTAINER FROM THE GENERATED IMAGE AND RUNS IT
# sudo docker ps -a                                      VIEW PREVIOUSLY RAN AND CURRENTLY RUNNING CONTAINERS
# sudo docker container prune                            DELETES UNUSED CONTAINERS
# sudo docker image prune                                DELETES UNUSED IMAGES

# Specifying the base image
FROM python:3.8-slim-buster

# Copying the work directory
WORKDIR /w22_cis3760_team1
COPY . .

# Exposing TCP port 5000 for flask server
EXPOSE 5000/tcp

# Update the list of commands that can be downloaded, and upgrade the current commands as well
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install sudo -y

# Run the two scripts used to setup dependencies
RUN ./vmSetup.sh
RUN ./websiteSetup.sh

# # Running commands to set it up
# RUN apt-get install gcc -y
# RUN apt-get install chromium -y
# RUN apt-get install graphviz -y
# RUN apt-get install npm -y
# RUN pip3 install -r requirements.txt
# RUN playwright install

CMD sleep 120