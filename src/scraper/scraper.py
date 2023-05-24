from datetime import datetime
from playwright.sync_api import sync_playwright
import time
import json
import sys
import traceback
import logging
import logging.handlers
import os

"""
This function instantiates a log file that keeps track of how long it takes to scrape the courses
"""
def createLogFile():
    today = datetime.today().strftime("%d-%m-%Y_H-%H_M-%M_S-%S")

    if not os.path.exists('src/scraper/logs'):
        os.makedirs('src/scraper/logs')

    with open('src/scraper/logs/' + today, 'w') as f:
        f.write("Log file for " + today + ":\n\n\n")

        # Sets logging level based on debug flag
        uppers = [s.upper() for s in sys.argv]
        if "-d" in uppers or "--d" in uppers or "-debug" in uppers or "--debug" in uppers:
            logging.basicConfig(filename = 'src/scraper/logs/' + today, level = logging.DEBUG)
        else:
            logging.basicConfig(filename = 'src/scraper/logs/' + today, level = logging.INFO)

    return logging.getLogger()

"""
This function extracts a particular string from an html page based on the query parameter given 
"""
def extractString(logger, course, query, span):
    try:
        extracted_string = course.query_selector(query)

        if span == True:
            extracted_string = extracted_string.query_selector("span")

        extracted_string = extracted_string.inner_text()

    except Exception as e:
        extracted_string = "No Data"
        logger.debug("Error while extracting title:\n" + str(e))
    
    return extracted_string

"""
This function parses course data from a course list html page 
"""
def getData(logger, course):
    # Getting the course code string
    code = extractString(logger, course, ".detail-code", False)

    # Getting the course title string
    title = extractString(logger, course, ".detail-title", False)

    # Getting the course term string
    term_raw = extractString(logger, course, ".detail-typically_offered", False)
    term = []

    if "No Data" in term_raw:
        term.append("No Data")
    else:
        if "summer" in term_raw.lower():
            term.append("S")
        if "fall" in term_raw.lower():
            term.append("F")
        if "winter" in term_raw.lower():
            term.append("W")
        
    # Getting the credit weight string
    credit_weight = extractString(logger, course, ".detail-hours_html", False)
    credit_weight = credit_weight.replace('[',"").replace(']',"")
        
    # Getting the course description
    description = extractString(logger, course, ".courseblockextra", False)
        
    # Getting the course location
    location = extractString(logger, course, ".detail-location_s_", True)

    # Getting the course department
    department = extractString(logger, course, ".detail-department_s_", True)
        
    # Getting the course offerings
    offerings_raw = extractString(logger, course, ".detail-offering", True)
    offerings = []

    if "No Data" in offerings_raw:
        offerings.append("No Data")
    else:
        if "distance education" in offerings_raw.lower():
            offerings.append("DE")
        if "even-numbered" in offerings_raw.lower():
            offerings.append("Even")
        if "odd-numbered" in offerings_raw.lower():
            offerings.append("Odd")
    
    # Getting the course restrictions
    restrictions = extractString(logger, course, ".detail-restriction_s_", True)
        
    # Getting the course equivalents
    equivalents = extractString(logger, course, ".detail-equate_s_", True)
        
    # Getting the course prerequisites
    prerequesites = extractString(logger, course, ".detail-prerequisite_s_", True)

    return {
                'name' : title,
                'code' : code,
                'description' : description,
                'prereq' : prerequesites,
                'creditWeight' : credit_weight,
                'term' : term,
                'department' : department,
                'location' : location,
                'equivalent' : equivalents,
                'restrictions' : restrictions,
                'offerings' : offerings
            }

def main():
    # Instantiate new log file
    logger = createLogFile()

    with sync_playwright() as playwright_instance:

        # Get to page and start scraping timer
        browser = playwright_instance.chromium.launch()
        page = browser.new_page()
        page.goto("https://calendar.uoguelph.ca/undergraduate-calendar/course-descriptions/", timeout = 0)
        scrape_time_start = time.time()
        
        # Getting all links on the main page under the az_sitemap class, and then constructing a new list with their hrefs
        links_html = page.query_selector_all(".az_sitemap a")
        program_links_unflitered = []
        for link in links_html:
            program_links_unflitered.append(link.get_attribute("href"))
            
        # Removing all links that aren't course description links
        program_links = []
        for link in program_links_unflitered:
            if "course-descriptions" in str(link):
                program_links.append(str(link))
                
        # Setting up the dictionary for JSON file output
        scraped_data = {}
        scraped_data["courses"] = []
        total_num_programs = 0
        total_num_courses = 0

        # Looping through the individual pages
        prefix_link = "https://calendar.uoguelph.ca/"
        for link in program_links:
            total_num_programs += 1
            print("Visiting: '" + str(prefix_link) + str(link) + "'")
            page.goto(prefix_link + link)
            courses = page.query_selector_all(".courseblock")
            
            # Looping through all of the courses on the department page
            for course in courses:
                total_num_courses += 1

                # Parsing the data into a dictionary that will be used for JSON output
                scraped_data['courses'].append(getData(logger, course))
        
        # Creating a data file
        scrape_time_end = time.time()
        scraped_data["total_num_courses"] = str(total_num_courses)
        scraped_data["total_num_programs"] = str(total_num_programs)
        scraped_data["time_taken_to_scrape"] = str(scrape_time_end - scrape_time_start)
        scraped_data["time_scraped"] = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S EST"))
        
        if not os.path.exists('src/scraper/data'):
            os.makedirs('src/scraper/data')
        
        with open('src/scraper/data/json_data.json', 'w') as outfile:
            json.dump(scraped_data, outfile, sort_keys=True, indent=4)
        browser.close()

    exec_time = scrape_time_end - scrape_time_start
    logger.info("Time to completion:\t" + str(exec_time))


main()
