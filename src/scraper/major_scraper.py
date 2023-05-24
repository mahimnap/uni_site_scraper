import json
from unittest import skip
from playwright.sync_api import sync_playwright
import re

# Create a dictionary of course requirements for each program major
def create_majors(major_dict):
    final_majors = {}
    final_majors["programs"] = {}

    # Iterate through program majors
    for major in major_dict["entry"]:
        try:
            table_text = major["table_obj"]
            
            # Find all courses in this program major
            courses = re.findall(r'[A-Z]{3,4}\*[0-9]{4}', table_text)

            # Parse out extra credit requirements
            total_extra_requirements = {}
            bad_words = ["*", "Select", "Semester", "work", "Exchange", "Option", "Stream", "following", "semesters", "admission"]
            for i in table_text.split('\n'): 
                # Smallest length I found was around 14, this len check is used to cull non elective text
                if len(i) > 13:

                    # Skip the line if it contains information signifying its not a credit requirement
                    skip_line = False
                    for j in bad_words:
                        if j in i:
                            skip_line = True
                            break
                    
                    if not skip_line:
                        # Strip whitespace, split into credit number and requirement
                        extra_requirements = i.strip()
                        
                        # Remove duplicate credit value from the start, then extract credit weight of electives from the end of the string
                        extra_requirements = re.sub(r'^\d+\.\d+\s*', r'', extra_requirements)
                        weight = extra_requirements[len(extra_requirements) - 4:]

                        # Remove duplicated credit value on the end, and restrip whitespace
                        extra_requirements = re.sub(r'\d+\.\d+$', r'', extra_requirements)
                        extra_requirements = extra_requirements.strip()

                        # Case where text is like up to X total credits in the rest of the semester
                        if "total credits in this semester" in extra_requirements or "to a maximum of" in extra_requirements:
                            extra_requirements = "Electives or Restricted Electives"
                        
                        # Capitalize first letter
                        if len(extra_requirements) > 0 and extra_requirements[0].isalpha:
                            extra_requirements = extra_requirements[0].upper() + extra_requirements[1:]

                        total_extra_requirements[extra_requirements] = weight

            # Build program major
            final_cur_major = {}
            final_cur_major["program_name"] = major["program_name"]
            final_cur_major["program_link"] = major["program_link"]
            final_cur_major["courses"] = sorted(list(set(courses)))
            final_cur_major["extra_requirements"] = total_extra_requirements

            code = re.sub(r'.*\((.*)\)$', r'\1',  major["program_name"])
            final_majors["programs"][code] = final_cur_major
        except Exception as e:
            print(e)
            pass
    return final_majors

def main():
    with sync_playwright() as scrape:
        browser = scrape.chromium.launch()
        page = browser.new_page()

        # Leaving 30 second default timeout while testing (i.e. not timeout = 0)
        page.goto('https://calendar.uoguelph.ca/undergraduate-calendar/degree-programs/')

        # Extracting all degree links and storing in degree_links 
        links = page.query_selector('[id="textcontainer"]').query_selector_all("a")
        degree_links = []
        for link in links:
            degree_links.append(link.get_attribute("href"))

        # All links extracted will be appended to this
        root_url = 'https://calendar.uoguelph.ca/'

        # Loop through all the degrees, extract the major links, and store in major_links 
        major_links = []

        for link in degree_links:
            page.goto(root_url + link)
            # print("Checking Degree Link: " + root_url + link)

            # Checking if page has a requirements tab
            try:
                requirements_tab = page.query_selector('[id="requirementstextcontainer"]')
                if(requirements_tab):
                    major_links.append(root_url + link)
            except:
                pass
            
            # Checking if page has a programs tab
            try:
                programs_tab = page.query_selector('[id="programstextcontainer"]')
                if(programs_tab):
                    temp_links = programs_tab.query_selector_all("a")
                    for n in temp_links:
                        major_links.append(root_url + n.get_attribute("href")) 
            except:
                pass
            
            # Checking if page has a schedule of studies tab
            try:
                sched_of_stud = page.query_selector('[id="scheduleofstudiestextcontainer"]')
                if(sched_of_stud):
                    major_links.append(root_url + link) 
            except:
                pass
        
        # Getting the list of pages that have majors
        # NOTE: major_links_table_dict is an array of programs, where each has attribute "program_name", "program_link", and "table_obj" 
        major_links_table_dict = {}
        major_links_table_dict["entry"] = []
        for link in major_links:
            print("Visiting: " + link)
            page.goto(link)
            
            try:
                major_links_table_entry_dict = {}
                # Checking if the current tab is a requirements, programs, or schedule of studies tab
                current_tab = page.query_selector('[id="requirementstextcontainer"]')
                if(current_tab is None):
                    current_tab = page.query_selector('[id="programstextcontainer"]')
                if(current_tab is None):
                    current_tab = page.query_selector('[id="scheduleofstudiestextcontainer"]')
                if(current_tab is None):
                    continue
                
                # Checking if the entry contains a major or schedule of studies
                check_minor = current_tab.query_selector_all('h2,h3')
                for cur_degree in check_minor:
                    if("major" in cur_degree.inner_text().lower() or "schedule of studies" in cur_degree.inner_text().lower()):
                        
                        # Getting the name of the major and link
                        major_title = page.query_selector('[class="page-title"]')
                        major_links_table_entry_dict["program_name"] = major_title.text_content()
                        major_links_table_entry_dict["program_link"] = link
                
                # Check to see if the page contains a Major header and a Schedule of Studies header
                check_headers = current_tab.query_selector_all('h2,h3')
                found_major = False
                found_sos = False
                for header in check_headers:
                    if "major" in header.inner_text().lower():
                        found_major = True
                    elif "schedule of studies" in header.inner_text().lower():
                        found_sos = True
                skip_sos = (found_major and found_sos)
                
                # Looking for all h2, h3, and tables since a table will almost always have a major prior to it
                current_tab_items = current_tab.query_selector_all('h2,h3,table');
                for i in range(len(current_tab_items)):
                    cur_item = current_tab_items[i].inner_text().lower()
                    cur_item_html = current_tab_items[i].inner_html().lower()
                    
                    # Checking if an element that contains major is found, or schedule of studies (only if major isn't found on the page)
                    # After that check if its a table or not
                    if ("major" in cur_item or ("schedule of studies" in cur_item and not skip_sos)) and "thead" not in cur_item_html:
                        table_obj = current_tab_items[i+1]
                        major_links_table_entry_dict["table_obj"] = table_obj.inner_text()
                        
                        # Check if there are any courses present in the inner text
                        if "*" in table_obj.text_content():
                            major_links_table_dict["entry"].append(major_links_table_entry_dict)
                        break
            except:
                pass

        # Dumping the parsed JSON data 
        with open("src/scraper/data/scraped_majors_data.json", "w") as f:
            json.dump(create_majors(major_links_table_dict), f, sort_keys=True, indent=4)

        browser.close()
if __name__ == '__main__':
    main() 