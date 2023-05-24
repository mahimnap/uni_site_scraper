import subprocess
import smtplib
import ssl
import json
import time
from datetime import datetime
import requests
from playwright.sync_api import sync_playwright

# Function that checks if a command gives expected output
def check_command(command, expected_output, flag, check_in):
   try:
      cur_cmd_bytes = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
      cur_cmd_string = str(cur_cmd_bytes).replace("\\n", "\n").replace("b'", "").lower()[:-2]
      if check_in is True:
         if expected_output in cur_cmd_string:
            dependency_map[flag] = "True"
      else: 
         if expected_output not in cur_cmd_string:
            dependency_map[flag] = "True"
   except:
      return

# Function that tests the API backend and verify results
def testAPIBackend():
   api_map = {
      "/": "True",
      "/api/graphExample": "True",
      "/api/pdfGraph": "True",
      "/api/preqs": "True",
      "/api/search": "True"
   }
   server = "http://131.104.49.100"


   # Testing to ensure that files are returned
   if (not requests.get(server + "/").text.startswith("<!doctype html>")):
      api_map["/"] = "False"

   if (not requests.get(server + "/api/graphExample").text.startswith("<script src=")):
      api_map["/api/graphExample"] = "False"
      
   if (not requests.get(server + "/api/pdfGraph").text.startswith("<!DOCTYPE html>")):
      api_map["/api/pdfGraph"] = "False"

   # Test APIs with with bad request (missing required parameters)
   if (not requests.get(server + "/api/preqs").status_code == 400):
      api_map["/api/preqs"] = "False"

   if (not requests.get(server + "/api/search").status_code == 400):
      api_map["/api/search"] = "False"


   # Test search API with bad parameter format
   r = requests.get(server + "/api/search?university=guelph&subjects=&terms=F%20W%20S&prereqs=yes&levels=1000%20-%205000&credits=abc")
   if ("Course weight must be numeric!" not in r.text):
      api_map["/api/search"] = "False"

   # Test prereq API with good request
   r = requests.get(server + "/api/preqs?code=COOP*1000&carleton=false")
   if (not r.status_code == 200 and r.text.startswith('{"results":"')):
      api_map["/api/preqs"] = "False"

   # Test search API with good request
   r = requests.get(server + "/api/search?university=guelph&subjects=cis&terms=F&prereqs=yes&levels=3000&credits=0.75")
   if (not r.status_code == 200 and r.text == '{"results":"[{\"code\": \"CIS*3760\", \"creditWeight\": \"0.75\", \"department\": \"School of Computer Science\", \"description\": \"This course is an examination of the software engineering process, the production of reliable systems and techniques for the design and development of complex software. Topics include object-oriented analysis, design and modeling, software architectures, software reviews, software quality, software engineering, ethics, maintenance and formal specifications.\", \"equivalent\": \"No Data\", \"location\": \"Guelph\", \"name\": \"Software Engineering\", \"offerings\": [\"No Data\"], \"prereq\": \"CIS*2750, CIS*3750\", \"restrictions\": \"No Data\", \"term\": [\"F\", \"W\"]}, {\"code\": \"CIS*3750\", \"creditWeight\": \"0.75\", \"department\": \"School of Computer Science\", \"description\": \"This course is an introduction to the issues and techniques encountered in the design and construction of software systems, focusing on the theory and models of software evolution. Topics include requirements and specifications, prototyping, design principles, object-oriented analysis and design, standards, integration, risk analysis, testing and debugging.\", \"equivalent\": \"No Data\", \"location\": \"Guelph\", \"name\": \"System Analysis and Design in Applications\", \"offerings\": [\"No Data\"], \"prereq\": \"9.00 credits including CIS*2520, (CIS*2430 or ENGG*1420)\", \"restrictions\": \"No Data\", \"term\": [\"F\", \"W\"]}]"}'):
      api_map["/api/preqs"] = "False"

   return api_map

# Function to test the front-end of the website
def testFrontEnd():
   frontend_test_map = {
      "titleAsExpected": "True",
      "footerAsExpected": "True",
      "courseSearchPage": "True",
      "graphSubjectsPage": "True",
      "graphMajorsPage": "True",
      "submitQueryExists": "True"

   }

   with sync_playwright() as playwright_instance:

      root_link = "http://131.104.49.100/"
      browser = playwright_instance.chromium.launch() 
      page = browser.new_page() 
      page.goto(root_link, timeout = 0)

      # Verify title is as expected
      try:
         if (page.title() != "CIS3760 Team 1"):
               frontend_test_map["titleAsExpected"] = "False"
      except:
         frontend_test_map["titleAsExpected"] = "False"

      # Verify footer is as expected
      try:
         if (page.locator("footer").inner_text() != "CIS 3760 Team One Website"):
               frontend_test_map["footerAsExpected"] = "False"
      except:
         frontend_test_map["footerAsExpected"] = "False"

      # Verify that the search for courses page works and has the 'Submit Query' button available
      try:
         page.click('text="Search for Courses"')

         if (page.locator('css=[aria-current="page"]').inner_text() != "Search for Courses"):
               frontend_test_map["courseSearchPage"] = "False"
         
         if (page.locator(".App-button").inner_text() != "Submit Query"):
               frontend_test_map["submitQueryExists"] = "False"
      except:
         frontend_test_map["courseSearchPage"] = "False"
         frontend_test_map["submitQueryExists"] = "False"

      # Verify that the graph subjects page works
      try:
         page.click('text="Graph Subjects"')

         if (page.locator('css=[aria-current="page"]').inner_text() != "Graph Subjects"):
               frontend_test_map["graphSubjectsPage"] = "False"
      except:
         frontend_test_map["graphSubjectsPage"] = "False"

      # Verify that the graph majors page works
      try:
         page.click('text="Graph Majors"')

         if (page.locator('css=[aria-current="page"]').inner_text() != "Graph Majors"):
               frontend_test_map["graphMajorsPage"] = "False"
      except:
         frontend_test_map["graphMajorsPage"] = "False"

      browser.close()

   return frontend_test_map


# Opening up settings file
while True:
   
   # Map of all dependencies and processes, as well as their status
   dependency_map = {
      # Linux commands
      "Linux-command-pip3" : "False",
      "Linux-command-playwright" : "False",
      "Linux-command-chromium" : "False",
      "Linux-command-dot" : "False",
      "Linux-command-npm" : "False",
      "Linux-command-openssl" : "False",

      # Python packages
      "Python-package-playwright" : "False",
      "Python-package-graphviz" : "False",
      "Python-package-wheel" : "False",
      "Python-package-flask" : "False",
      "Python-package-uwsgi" : "False",

      # Python tests
      "Python-tests" : "False",

      # Flask services
      "Flask-api" : "False",

      # Nginx services
      "Nginx-master-process" : "False",
      "Nginx-worker-process" : "False",
   }

   with open("settings.json") as file:
      data = json.load(file)
   sender_email = data["email_username"]
   sender_pass = data["email_password"]
   receiver_emails = data["email_receivers"]
   loop_interval = data["loop_interval_minutes"]

   # Checking if various linux commands are functional
   check_command("pip3 -V", "command not found", "Linux-command-pip3", False)
   check_command("playwright -V", "command not found", "Linux-command-playwright", False)
   check_command("chromium --product-version", "command not found", "Linux-command-chromium", False)
   check_command("dot -V", "command not found", "Linux-command-dot", False)
   check_command("npm -v", "command not found", "Linux-command-npm", False)
   check_command("openssl version", "command not found", "Linux-command-openssl", False)

   # Checking if all python dependencies are installed
   check_command("pip list", "playwright", "Python-package-playwright", True)
   check_command("pip list", "graphviz", "Python-package-graphviz", True)
   check_command("pip list", "wheel", "Python-package-wheel", True)
   check_command("pip list", "flask", "Python-package-flask", True)
   check_command("pip list", "uwsgi", "Python-package-uwsgi", True)

   # Checking if all python tests are working
   check_command("cd ../../ && python3 -m unittest -b && cd test/program_monitor/", "failed", "Python-tests", False)

   # Checking if the flask api is running
   check_command("ps aux | grep flask", "flaskapi", "Flask-api", True)

   # Checking if nginx is running
   check_command("ps aux | grep nginx", "nginx: master process", "Nginx-master-process", True)
   check_command("ps aux | grep nginx", "nginx: worker process", "Nginx-worker-process", True)

   api_map = testAPIBackend()

   frontend_test_map = testFrontEnd()

   # Initialize email stuff
   num_broken_dependencies = 0
   for dependency in dependency_map:
      if dependency_map[dependency] == "False":
         num_broken_dependencies += 1

   for API in api_map:
      if api_map[API] == "False":
         num_broken_dependencies += 1
      
   for test in frontend_test_map:
      if frontend_test_map[test] == "False":
         num_broken_dependencies += 1

   if num_broken_dependencies != 0:
      try:
         context = ssl.create_default_context()

         # Setting the subject
         message = "Subject: ERROR: " + str(num_broken_dependencies) + " Issue(s) Found On Server\n\n"

         # Setting the header message
         message += "At " + str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + " EST...\n"
         message += "A total of " + str(num_broken_dependencies) + " issue(s) were found for the CIS3760 - team 1 project\n\n"

         # Setting the more detailed information regarding dependencies
         message += "Broken Dependencies\n"
         for dependency in dependency_map:
            if dependency_map[dependency] == "False":
               message += "Dependency: " + dependency + " is broken\n"
         message += "\nWorking Dependencies\n"
         for dependency in dependency_map:
            if dependency_map[dependency] == "True":
               message += "Dependency: " + dependency + " is working\n"
         
         message += "\n"

         # Setting the more detailed information regarding APIs
         message += "Broken APIs\n"
         for API in api_map:
            if api_map[API] == "False":
               message += "Dependency: " + API + " is broken\n"
         message += "\nWorking APIs\n"
         for API in api_map:
            if api_map[API] == "True":
               message += "Dependency: " + API + " is working\n"

         message += "\n"

         # Setting the more detailed information regarding front-end tests
         message += "Broken Front-End Tests\n"
         for test in frontend_test_map:
            if frontend_test_map[test] == "False":
               message += "Dependency: " + test + " is broken\n"
         message += "\nWorking Front-End Tests\n"
         for test in frontend_test_map:
            if frontend_test_map[test] == "True":
               message += "Dependency: " + test + " is working\n"

         # Sending the email
         for email in receiver_emails:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
               server.login(sender_email, sender_pass)
               server.sendmail(sender_email, email, message)
      except:
         print("Error encountered with dependency monitor, there are issues but an email hasn't been sent")
         print("Please check the email credentials as that is most likely the issue")
   time.sleep(60 * loop_interval)