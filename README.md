# W22 CIS*3760 Team 1

## Overview

A CLI tool to display course information for the University of Guelph. This tool supports multiple ways of searching and its capabilities are described in the course searching section below. This tool is also built without third-party libraries to improve long-term support.

Python scripts should be run from the root of the Git repository.

## JSON Data File Structure

To improve speed, it was decided to record course information on disk to remove scraping time per execution. Updates to the on-disk course records can be set up to run periodically to improve accuracy of the calendar information. Storing it on disk also allows for the manual editing of data as needed.

## Scraper

Our scraper is built using the playwright library so it can be run from any machine with vanilla Python3 installed. The scraper is also set up to allow for descriptive and helpful logging information to keep the developers informed on erroneous execution. Further improvements can be made to automate the sending of these log files. to the developers. The scraper also records its execution time so the developers can gather the data and study ways to improve it in the future.

It will collect course information from the [University of Guelph website](https://calendar.uoguelph.ca/undergraduate-calendar/course-descriptions/) and output it to a JSON file.
To run the scraper type:
```
python3 src/scraper/scraper.py
```
Once the program exits you should see a JSON file containing all the course data in src/scraper/data/scraped_data.json

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

## Graph Course Visualization

Once the data has been scraped, the course search tool can be used.
```
python3 src/visualizer.py <FLAGS>
```
This is the flag that will be used for deciding which course
* -S The subject of the desired courses e.g., `-S CIS`
* -F Select which file type to use to save the graph e.g., `-F png`/`-F PNG`
* -N Select name for the graph file e.g., `-N graph`
* -hor Select to display the graph horizontally instead of vertically e.g., `-hor`

## Testing

There are unit tests set up for many functionalities. 
To run the unit tests, type:
```
python3 -m unittest -b
```
The tests will show in the terminal, depicting whether they passed or failed, and how long it took to complete every test.

## VM

To setup the VM log in, clone the repo, move to the wanted sprint branch, and then run the VM setup script. It will install all the necessary software.
```
sh vmSetup.sh
```