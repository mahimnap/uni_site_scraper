# University Site Scraper and Major Graph Visualization

## Overview

A tool to display course information for the University of Guelph. This tool supports multiple ways of searching and its capabilities are described in the course searching section below. This tool is also built without third-party libraries to improve long-term support.

Python scripts should be run from the root of the Git repository.

## JSON Data File Structure

To improve speed, it was decided to record course information on disk to remove scraping time per execution. Updates to the on-disk course records can be set up to run periodically to improve accuracy of the calendar information. Storing it on disk also allows for the manual editing of data as needed.

## Scraper

Our scraper is built using the playwright library so it can be run from any machine with vanilla Python3 installed. The scraper is also set up to allow for descriptive and helpful logging information to keep the developers informed on erroneous execution. Further improvements can be made to automate the sending of these log files. to the developers. The scraper also records its execution time so the developers can gather the data and study ways to improve it in the future.

It will collect course information from the [University of Guelph website](https://calendar.uoguelph.ca/undergraduate-calendar/course-descriptions/) and output it to a JSON file.<br><br>
To run the course scraper type:
```
python3 src/scraper/course_scraper.py
```
Once the program exits you should see a JSON file containing all the course data in src/scraper/data/scraped_course_data.json<br><br>
To run the major scraper type:
```
python3 src/scraper/major_scraper.py
```
Once the program exits you should see a JSON file containing all the course data in src/scraper/data/scraped_major_data.json

## Course Searching

Once the data has been scraped, the course search tool can be used.
```
python3 src/course_search.py <FLAGS>
```
There are many valid flags that can be used to facilitate the searching of courses:
* -C The creditWeight of the desired courses e.g., `-C 0.5 1.0` or as a range `-C 0.5 - 1.0`
* -T Term of the desired courses e.g., `-T F`
* -L The levels of the desired courses e.g., `-L 1000 3000` or as a range `-L 1000 - 3000`
* -S The subject of the desired courses e.g., `-S CIS`
* -I Left empty most of the time. Can be used to change the location of the JSON data
* -P Use this flag to search for courses with no prerequisites

## Graph Course and Major Visualization

Once the data has been scraped, the course search tool can be used.
```
python3 src/visualizer.py <FLAGS>
```
There are many valid flags that can be used to facilitate the graphing of courses and majors:<br>
NOTE: Choose one of -S, -M and -C
* -S The subject of the desired courses e.g., `-S CIS`
* -M The desired major to graph e.g., `-M CS:C`
* -F Select which file type to use to save the graph e.g., ` `/`-F PNG`
* -N Select name for the graph file e.g., `-N graph`
* -C Select course for the graph to find programs that contain it e.g., `-C CIS*1300`
* -hor Select to display the graph horizontally instead of vertically e.g., `-hor`
* -carleton Select to output a graph of all of Carleton University's courses by subject in a single PDF file
* -multimajor Select to output a graph of all of Guelph University's majors in a single PDF file

## Website dependencies

There is an installation script that checks if dependencies are installed, and if they aren't it installs them.
To run the script type:
```
./websiteSetup.sh
```
Debugging tips for SSL can be found at the following sites: [1](https://www.cloudsavvyit.com/1306/how-to-create-and-use-self-signed-ssl-on-nginx/),[2](https://www.humankode.com/ssl/create-a-selfsigned-certificate-for-nginx-in-5-minutes),[3](https://www.howtogeek.com/177621/the-beginners-guide-to-iptables-the-linux-firewall/)

## Website build

To build the app for production to the `build` folder, go to the web directory and type:<br>
NOTE: Running the command through VSCode terminal may not work due to low memory, run through ssh instead
```
npm run build
```
It correctly bundles React in production mode and optimizes the build for the best performance. The build is minified and the filenames include the hashes.

## Run backend

To start running the backend of the website, use uwsgi to start Flask.<br>
Type the following command:
```
uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app
```
The 0.0.0.0:5000 means that the backend runs on port 5000 and is open to all IP addresses. HTTP indicates the information transfer protocol and the w flag indicates what to run.

## Testing

There are unit tests set up for many functionalities. 
To run the unit tests, type:
```
python3 -m unittest -b
```
The tests will show in the terminal, depicting whether they passed or failed, and how long it took to complete every test.

Testing the NGINX server can be done using `sudo nginx -t`

## VM

To setup the VM log in, clone the repo, move to the wanted sprint branch, and then run the VM setup script. It will install all the necessary software.
```
sh vmSetup.sh
```

## NGINX

To check the status of the currently running NGINX server: `systemctl status nging.service`
To restart the NGINX server and apply changes to configuration settings: `sudo systemctl restart nginx`
To start the NGINX server: `sudo systemctl nginx start`

NGINX is currently configured with a self-signed certificate. To view, enter `https://131.104.49.100` in the address bar.

# Config Files
To set up the server please move the config files to the correct location
1. Move 'flaskapi' to /etc/nginx/sites-available/flaskapi
2. Run `sudo ln -s /etc/nginx/sites-available/flaskapi /etc/nginx/sites-enabled/` to enable the website config
3. Remove the 'default' file from /etc/nginx/sites-enabled/ 
4. Move 'flaskapi.service' to /etc/systemd/system/flaskapi.service to add a service that can easily be started and stopped

Note that file paths in both files may have to be changed to respect your computer's specific file hierarchy

Then run 
```
systemctl start flaskapi
systemctl enable flaskapi
systemctl restart nginx
```
You will be able to view the status of the flask api and NGINX with commands like
```
systemctl status flaskapi
systemctl status nginx
```

# Program Monitor
There is a shell script named `programMonitor.sh` in the main directory that if ran, gives the ability to monitor dependencies in real time. If there are issues found, an email will be sent to the mailing list that expresses the issues. To configure this feature, go to `test/program_monitor/settings.json`.<br><br>
To run the script, type:
```
./programMonitor.sh
```

# Dockerize
There is a script named `dockerize.sh` that installs docker if it isn't already installed, then creates and image that has the application in it, and runs said container.<br><br>
Currently the script supports Debian, Ubuntu, Fedora, and CentOS. MacOS and Windows aren't supported as they require the installation and usage of the docker desktop app<br><br>
To run the script, type:
```
./dockerize.sh
```
There are also a few commands that may be of use:
```
sudo docker image rm -f image_name                      DELETES OLD IMAGE

sudo docker build -t image_name .                       BUILDS IMAGE FROM THIS DOCKERFILE

sudo docker run -d --name container_name image_name     CREATES A CONTAINER FROM THE GENERATED IMAGE AND RUNS IT

sudo docker ps -a                                       VIEW PREVIOUSLY RAN AND CURRENTLY RUNNING CONTAINERS

sudo docker container prune                             DELETES UNUSED CONTAINERS

sudo docker image prune                                 DELETES UNUSED IMAGES
```
