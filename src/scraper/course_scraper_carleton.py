from datetime import datetime
from playwright.sync_api import sync_playwright
import time
import json
import sys
import logging
import logging.handlers
import argparse
import os
import json 
import re

"""
This function instantiates a log file that keeps track of how long it takes to scrape the courses
"""
def createLogFile():
    today = datetime.today().strftime("%d-%m-%Y_%H-%M-%S")

    if not os.path.exists('src/scraper/logs'):
        os.makedirs('src/scraper/logs')

    with open('src/scraper/logs/carleton_' + today, 'w') as f:
        f.write("Carleton Scraper Log file for " + today + ":\n\n\n")

        # Sets logging level based on debug flag
        uppers = [s.upper() for s in sys.argv]
        if "-d" in uppers or "--d" in uppers or "-debug" in uppers or "--debug" in uppers:
            logging.basicConfig(filename = 'src/scraper/logs/carleton_' + today, level = logging.DEBUG)
        else:
            logging.basicConfig(filename = 'src/scraper/logs/carleton_' + today, level = logging.INFO)

    return logging.getLogger()

"""
This function gets commandline args to see if it is supposed to use debug mode (defaulted to off) 
"""
def get_args():
    parser = argparse.ArgumentParser(description="A Course Data JSON builder utility for Carleton University")
    parser.add_argument('-D', '-d', default=False, help = 'Use this flag to execute in DEBUG mode', required=False, action="store_true")
    args = parser.parse_args()
    return args

"""
This function parses the prerequisites into ANDs and ORs so its easier to graph
"""
def parsePrerequisites(prereq):
    cur_prereq = {}
    cur_prereq['AND'] = []
    cur_prereq['OR'] = []
    
    mode = 'AND'
    override = False
    ignore_next_lookahead = 0

    # loop through string, parsing prerequisites
    i = 0
    while i < len(prereq):
        # Check if we are at an OR
        if i + 1 < len(prereq) and prereq[i:i+2] == "OR":
            mode = "OR"
            i += 1
        # Check if we are at an AND
        elif i + 2 < len(prereq) and prereq[i:i+3] == "AND":
            mode = "AND"
            i += 2
        # Check if we are entering an OF block
        elif i + 1 < len(prereq) and prereq[i:i+2] == "OF":
            mode = "OR"
            override = True
            i += 1
        # Commas are ANDs
        elif prereq[i] == ',' and override == False:
            mode = "AND"
        # Override is used because commas are interpreted in ORs inside a OF block 
        elif override == 1 and (prereq[i] == ')' or prereq[i] == ']'):
            override = False
            mode = "AND"
        # This means it is a course code because we have looked for every other possible uppercase already
        elif prereq[i].isupper(): 
            # Gets index at the end of the course code
            end_of_course_code = prereq.find('*', i) + 4

            # Look ahead after course code (e.g., X OR Y --> X will look ahead to find out its an OR)
            j = end_of_course_code - 1
            while j < len(prereq) and ignore_next_lookahead == 0:
                if j + 1 < len(prereq) and prereq[j:j+2] == "OR":
                    mode = 'OR'
                    # If it is an OR we want to skip the next look ahead because we already know the next course is also an OR (e.g, X or Y)
                    # Set to 2 because its decremented after its set, thus being 1 on the next loop allowing for the skip to occur and be set to 0 after
                    ignore_next_lookahead = 2
                    break
                elif override == False and (prereq[j] == ',' or (j + 2 < len(prereq) and prereq[j:j+3] == "AND")):
                    mode = 'AND'
                    break
                j += 1
            
            # Reduce ignore lookahead counter 
            if ignore_next_lookahead > 0:
                ignore_next_lookahead -= 1

            # Append the course to the corresponding section
            cur_prereq[mode].append(prereq[i:end_of_course_code + 1])
            i += end_of_course_code - i - 1
        
        i += 1
    return cur_prereq

"""
This function goes to root url and extracts all the type links 
- Type refers to type of course e.g. type AERO has course AERO 2110 
"""
def getCourseTypeLinks (page, root_link, debug, logger):
    root_type_div = page.query_selector("div.course")
    type_href_list = root_type_div.query_selector_all("a")
    type_cleaned_href_list = []

    for href in type_href_list:
        if (href.inner_html().find(')') != -1):
            type_cleaned_href_list.append(root_link + href.inner_html().replace(')', ''))
        else:
            type_cleaned_href_list.append(root_link + href.inner_html()) 

    if debug:
        logger.info(datetime.now().strftime("%d-%m-%Y_%H:%M:%S") + ": Retrieved the links of course types. Beginning course scraping...")
    
    return type_cleaned_href_list 

"""
This function extracts course information from previously extracted type links 
"""
def getCourseInfo(page, course_type_links, debug, logger):
    scraped_data = {}
    scraped_data["courses"] = [] 
    for course_type_link in course_type_links:
        print("Visiting: " + course_type_link)
        page.goto(course_type_link, timeout = 0)
        #print ("Parsing: " + course_type_link) 
        courses = page.query_selector_all(".courseblock")
        department = page.query_selector("[class=red]").text_content()
        for course in courses:
                
            # Getting course code
            try:
                course_code = course.query_selector(".courseblockcode").text_content()
                course_code = re.sub(r"\s+", '*', course_code)
            except:
                course_code = "No Data"
                    
            # Getting credit weight
            try:
                raw_title = course.query_selector(".courseblocktitle").text_content().split('\n')[0]
                # remove unicdoe non break spaces
                credit_weight = ' '.join(raw_title.split())
                credit_weight = re.sub(r'.*\[(.*) ((credits)|(credit))\].*', r'\1', credit_weight)
            except:
                credit_weight = 0

            # Get description
            try:
                description = course.text_content()
                description = description.split('\n')[3]
            except:
                description = "No Data"
            
            # Getting the raw preqreq string with some preliminary cleaning
            try:
                course_prereqs_raw = course.query_selector(".coursedescadditional").text_content()
                for match in re.finditer(r'[A-Z]{3,4}\s+[0-9]{4}', course_prereqs_raw):
                    course_prereqs_raw = course_prereqs_raw[:match.end() - 5] + "*" + course_prereqs_raw[match.end() - 4:]
                prereq_match = re.search(r'prerequisite\(s\)\: ', course_prereqs_raw, re.IGNORECASE)
                course_prereqs_raw = course_prereqs_raw[prereq_match.end():]
            except:
                course_prereqs_raw = "No Data"
                
            # Parse out year standing prerequisite before cleaning
            year_standing = re.findall(r'[a-z]+-year standing', course_prereqs_raw)
            if len(year_standing) == 0:
                year_standing = ["No Required Year"]

            # Clean text from prerequisites
            
            if debug:
                logger.info(datetime.now().strftime("%d-%m-%Y_%H:%M:%S") + ": Retrieved course data for " + str(course_code) + " at url: " + str(course_type_link) + ". Cleaning prequisites now...")
            cur_preqreq = cleanPrerequisites(course_prereqs_raw, debug, logger)
            if debug:
                logger.info(datetime.now().strftime("%d-%m-%Y_%H:%M:%S") + ": Prequisites for " + str(course_code)+ " successfully cleaned\n")
                
            # Parse prerequisites into ANDs and ORs
            if cur_preqreq != "No Data":
                cur_preqreq = parsePrerequisites(cur_preqreq)
            
            course_output_data = {
                "code" : course_code, 
                "prereq" : course_prereqs_raw, # Change to cur_prereq to use parsed ANDs and ORs
                "year_standing": year_standing[0], 
                "creditWeight": str(format(float(credit_weight), '.2f')),
                "department": department,
                "location": "Carleton",
                "description": description,
                "offerings": ["No Data"],
                "term": ["S", "F", "W"],
                "equivalent": "No Data",
                "restrictions": "No Data"
            }
            scraped_data["courses"].append(course_output_data)
                
    return scraped_data

"""
This function removes text not related to course codes from the prerequesites
"""
def cleanPrerequisites(line, debug, logger=None):
    try:
        # Checking if theres course prereqs at all
        if '*' not in line:
            return "No Data"
            
        # Regex that removes rogue capital letter matches (ADDED IN SPRINT 4)
        m = re.sub(r'[A-Z]+\s+', '', line)
        if logger and debug:
            logger.info(datetime.now().strftime("%d-%m-%Y_%H:%M:%S") + ": Removed rogue capital letters")

        # Capitalizing OR, AND, and OF, and fixing 1of case for easier parsing in the future
        m = re.sub(r'\bor\b', 'OR', m)
        m = re.sub(r'\band\b', 'AND', m)
        m = re.sub(r'\bof\b', 'OF', m)
        m = re.sub(r'one of', '1 OF', m)
        m = re.sub(r'1of', '1 OF', m)
        if logger and debug:
            logger.info(datetime.now().strftime("%d-%m-%Y_%H:%M:%S") + ": Capitalized conjuctional logic in prequisites (and/or/of)")
        
        # Regex that removes course credit requirement words
        m = re.sub(r'\b[0-9]+\.[0-9]+\b', '', m)
        if logger and debug:
            logger.info(datetime.now().strftime("%d-%m-%Y_%H:%M:%S") + ": Removed course credit requirement words")
        
        # Regex that removes all words that are fully lower case
        m = re.sub(r'\b[a-z]+\b', '', m)
        
        # Regex that removes all words that start with a capital letter
        m = re.sub(r'\b[A-Z]{1}[a-z]*\b', '', m)

        # Regex that removes percentages
        m = re.sub(r'[0-9]*%', '', m)
        if logger and debug:
            logger.info(datetime.now().strftime("%d-%m-%Y_%H:%M:%S") + ": Removed redundant syntax (upper/lower case, symbols)")
        
        # Regex that removes 1000 2000 3000 and 4000 if not in course code
        m = re.sub(r' 1000| 2000| 3000| 4000', '', m)

        # Regex that removes text before first capture and after last capture of the course code
        m = re.sub(r'^.*?([([A-Z]+\*[0-9]+)', r'\1', m)
        m = re.sub(r'(.*[A-Z]+\*[0-9)\]]+).*$', r'\1', m)
        
        # Regex that removes fixes cases where there is a space before the comma after a course
        m = re.sub(r'([([A-Z]+\*[0-9]+) ,', r'\1,', m)

        # Regex that removes random commas that dont correspond to a course
        m = re.sub(r' , ', '', m)

        # Regex that removes commas at the end of line
        m = re.sub(r',$', r'', m)
        
        # Regex that removes a few rogue characters
        m = re.sub(r'\'', '', m)
        m = re.sub(r'\+', '', m)
        m = re.sub(r'[.:;-]', '', m)
        if logger and debug:
            logger.info(datetime.now().strftime("%d-%m-%Y_%H:%M:%S") + ": Fixed whitespace and grammar irregularities")
        
        # Looping to remove extra ANDs and ORs that get isolated due to cleaning but were not yet removed
        for index in range(10):
            # Regex that removes extra whitespace and dots and colons and semicolons (ADDED IN SPRINT 4)
            m = re.sub(r'^\s+', '', m)
            m = re.sub(r'\s+', ' ', m)

            # Regex that fixes weird bracket cases and commas (ADDED IN SPRINT 4)
            m = re.sub(r'\(\s+\)', '', m)
            m = re.sub(r'\[\]', '', m)

            # Replace / in prereq (e.g., LING/COMP*2500 --> LING*2500 OR COMP*2500)
            test = re.findall(r'(?:[A-Z]{4}/)+(?:[A-Z]{4}\*[0-9]{4})', m) 
            for match in test:
                matchedCourses = match.split('/')

                # Get course number from final course
                courseNum = matchedCourses[-1][-5:]

                # Append course number to every course before the final
                for j in range(len(matchedCourses) - 1):
                    matchedCourses[j] += courseNum

                # Rejoin into one string, then replace the old text with the new parsed version
                test3 = " OR ".join(matchedCourses)
                m = re.sub(re.escape(match), re.escape(test3), m)
                m = re.sub(r'\\', r'', m)

            # Special case that needs to be handled separately (this is not actually a prerequisite)
            m = re.sub(r'BIB FINA\*5515', '', m)

            m = re.sub(r'\(', ' (', m)
            m = re.sub(r'\)', ') ', m)
            m = re.sub(r'\) ,', '),', m)
            m = re.sub(r' , ', ', ', m)
            
            # Regex that fixes the ANDs ORs OFs and , (ADDED IN SPRINT 4)
            m = re.sub(r'\(AND', 'AND', m)
            m = re.sub(r'AND\)', 'AND', m)
            m = re.sub(r'\( AND', 'AND', m)
            m = re.sub(r'AND \)', 'AND', m)
            m = re.sub(r', AND', 'AND', m)
            m = re.sub(r'AND ,', 'AND', m)
            m = re.sub(r'OR AND', 'AND', m)
            m = re.sub(r'OF AND', 'AND', m)
            m = re.sub(r'OF AND', 'AND', m)
            m = re.sub(r'AND OF', 'AND', m)
            m = re.sub(r'AND AND', 'AND', m)
            m = re.sub(r'ORAND', 'AND', m)
            m = re.sub(r'OFAND', 'AND', m)
            m = re.sub(r'ANDOF', 'AND', m)
            m = re.sub(r'ANDAND', 'AND', m)
            
            m = re.sub(r'\(OR', 'OR', m)
            m = re.sub(r'OR\)', 'OR', m)
            m = re.sub(r'\( OR', 'OR', m)
            m = re.sub(r'OR \)', 'OR', m)
            m = re.sub(r'\, OR', 'OR', m)
            m = re.sub(r'OR ,', 'OR', m)
            m = re.sub(r'AND OR', 'OR', m)
            m = re.sub(r'OF OR', 'OR', m)
            m = re.sub(r'OR OF', 'OR', m)
            m = re.sub(r'OR OR', 'OR', m)
            m = re.sub(r'ANDOR', 'OR', m)
            m = re.sub(r'OFOR', 'OR', m)
            m = re.sub(r'OROF', 'OR', m)
            m = re.sub(r'OROR', 'OR', m)
            
            m = re.sub(r'\(OF', 'OF', m)
            m = re.sub(r'OF\)', 'OF', m)
            m = re.sub(r'\( OF', 'OF', m)
            m = re.sub(r'OF \)', 'OF', m)
            m = re.sub(r', OF', 'OF', m)
            m = re.sub(r'OF ,', 'OF', m)
            m = re.sub(r'OF OF', 'OF', m)
            m = re.sub(r'OFOF', 'OF', m)
            
            m = re.sub(r'AND ', ' AND ', m)
            m = re.sub(r' AND', ' AND ', m)
            m = re.sub(r'OR ', ' OR ', m)
            m = re.sub(r' OR', ' OR ', m)
            
            # Regex that fixes more weird bracket cases that need to be removed
            m = re.sub(r'\( ', '(', m)
            m = re.sub(r' \)', ')', m)
            m = re.sub(r'\(OR\)', '', m)
            m = re.sub(r'\(AND\)', '', m)
            m = re.sub(r'\(OF\)', '', m)

            # Getting rid of leftover brackets
            if(m.count('(') == 1 and m.count(')') == 0):
                m = re.sub(r'\(', '', m)
            if(m.count('(') == 0 and m.count(')') == 1):
                m = re.sub(r'\)', '', m)
        
        # Regex that fixes a space between course code asterisk and letters
        m = re.sub(r'\s+\*', '*', m)
        
        # Regex that removes text before first capture and after last capture of the course code (ADDED IN SPRINT 4)
        m = re.sub(r'^.*?([([A-Z]+\*[0-9]+)', r'\1', m)
        m = re.sub(r'(.*[A-Z]+\*[0-9)\]]+).*$', r'\1', m)
                
        # Regex that removes extra whitespace and dots and colons and semicolons (ADDED IN SPRINT 4)
        m = re.sub(r'^\s+', '', m)
        m = re.sub(r'\s+', ' ', m)

        if logger and debug:
            logger.info(datetime.now().strftime("%d-%m-%Y_%H:%M:%S") + ": Prequisite cleaning complete!")
        return m
    except Exception as e:
        if logger:
            logger.info(datetime.now().strftime("%d-%m-%Y_%H:%M:%S") + ": Error occured during prerequisite cleaning: ", e)
        else:
            print("Error occured during prerequisite cleaning: ", e)

"""
This function dumps the formatted data into a JSON file 
"""
def outputJSONData (scraped_data):
    if not os.path.exists('src/scraper/data'):
        os.makedirs('src/scraper/data')
    with open('src/scraper/data/scraped_course_carleton_data.json', 'w') as outfile:
        json.dump(scraped_data, outfile, sort_keys=True, indent=4)

    
def main():
    logger=None 
    arguments = get_args()
    debug = arguments.D

    if debug:
        logger = createLogFile()

    with sync_playwright() as playwright_instance:

        scrape_time_start = time.time()

        root_link = "https://calendar.carleton.ca/undergrad/courses/"
        browser = playwright_instance.chromium.launch() 
        page = browser.new_page() 
        page.goto(root_link, timeout = 0)

        if debug:
            logger.info(datetime.now().strftime("%d-%m-%Y_%H:%M:%S") + ": Connected to Carleton Undergraduate calendar")

        course_type_links = getCourseTypeLinks(page, root_link, debug, logger)
        scraped_data = getCourseInfo(page, course_type_links, debug, logger) 
        outputJSONData(scraped_data)
        browser.close()

    scrape_time_end = time.time()
    exec_time = scrape_time_end - scrape_time_start

    if debug: 
        logger.info("\n\n\nTime to completion:\t" + str(exec_time) + " seconds...")

if __name__ == "__main__":
    main()
