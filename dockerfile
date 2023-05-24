# DOCKER COMMANDS
# sudo docker image rm -f testbuild                      DELETES OLD IMAGE
# sudo docker build -t testbuild .                       BUILDS IMAGE FROM THIS DOCKERFILE
# sudo docker run -d --name testcontainer testbuild      CREATES A CONTAINER FROM THE GENERATED IMAGE AND RUNS IT
# sudo docker ps -a                                      VIEW PREVIOUSLY RAN AND CURRENTLY RUNNING CONTAINERS
# sudo docker container prune                            DELETES UNUSED CONTAINERS
# sudo docker image prune                                DELETES UNUSED IMAGES

# Specifying the base image
FROM python:3.8-slim-buster

# Updating apt packages
RUN apt-get update -y
RUN apt-get upgrade -y

# Copying the work directory
WORKDIR /w22_cis3760_team1
COPY . .

# Exposing TCP port 5000 for flask server
EXPOSE 5000/tcp

# Update the list of commands that can be downloaded, and upgrade the current commands as well
RUN apt-get install sudo -y
RUN apt-get install gcc -y
RUN apt-get install curl -y
RUN apt-get install nodejs -y

# Run the vmsetup script to setup some preliminary commands
RUN bash ./vmSetup.sh

# Set correct version of NPM/NodeJS
SHELL ["/bin/bash", "--login", "-c"]
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash
RUN nvm install 17.4.0

# Run the website setup script to setup more commands and nginx
RUN bash ./websiteSetup.sh
RUN cd web
RUN npm run build

CMD uwsgi --socket 0.0.0.0:5000 --protocol=http -w -wsgi:app