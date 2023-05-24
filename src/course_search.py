import json
import os
import sys
import argparse
import platform
import re

"""
Checks and validates the input of all of the arguments input by the user.
Converting the output to the correct form and replacing ranges with the appropriate output
"""
def argument_parser(output, credits_unedited, terms, levels_unedited, subjects): # args.C, args.T, args.L, args.S
    credits = set()
    levels = set()
    error_strings = set()
    error_codes = []

    # Gets all the different options in the json
    course_subjects = set()
    course_levels = set()
    course_credits = set()

    for course in output['courses']:
        # Adds all course codes, all levels, and all weights into the set for better error checking
        course_subjects.add(re.search(".*(?=\*)", course['code'])[0]) # Gets the subject of the course
        course_levels.add(str(int(re.search("(?<=\*)\d{1}", course['code'])[0]) * 1000)) # Gets the level of the course
        course_credits.add(course['creditWeight'])

    course_subjects = sorted(course_subjects)
    course_levels = sorted(course_levels)
    course_credits = sorted(course_credits)

    # Checks if the json had the right information
    if not output or not course_subjects or not course_levels or not course_credits:
        print("Error: Invalid json file")
        return -1

    # Error handling for credit weight
    last = ""
    isRange = False
    
    for credit in credits_unedited:
        if isRange:
            # Checking for level range formatting
            if credit == '-':
                error_strings.add("Error: Credit range is improperly formatted")
                break
            isRange = False

            # Gets all credits in the range
            for i in course_credits:
                if float(i) >= float(last) and float(i) <= float(credit):
                    credits.add(i)
        
        if credit == '-':
            isRange = True
        else:
            # Checks if the credit value is invalid
            if float(credit) < 0.0 or float(credit) % 0.25 != 0:
                error_strings.add("Credit amount must be a non-negative float divisible by 0.25")
            else:
                # Saves the previous credit while searching for range
                last = credit
                credits.add(str(format(float(credit), '.2f')))

    # Error handling for terms
    for idx, term in enumerate(terms):
        terms[idx] = term.upper()
        term = terms[idx]
        if term == 'F' or term == 'FALL':
            terms[idx] = 'F'
        elif term == 'S' or term == 'SUMMER':
            terms[idx] = 'S'
        elif term == 'W' or term == 'WINTER':
            terms[idx] = 'W'
        else:
            error_strings.add("Term must be F(Fall), W(Winter) or S(Summer)")

    # Error handling for levels
    last = ""
    isRange = False
    for level in levels_unedited:
        if isRange:
            # Checking for level range formatting
            if level == '-':
                error_strings.add("Level range is improperly formatted")
                break
            isRange = False

             # Gets all levels in the range
            for i in course_levels:
                if int(i) >= int(last) and int(i) <= int(level):
                    levels.add(i)
        if level == '-':
            isRange = True
        else:
            # Checks if the level value is invalid
            if level not in course_levels:
                error_strings.add("Level must be one of " + ", ".join(course_levels))
            else:
                # Saves the previous level while searching for range
                last = level
                levels.add(level)

    # Error handling for subjects (looking for unknown course codes)
    for idx, subject in enumerate(subjects):
        subjects[idx] = subject.upper()
        if subjects[idx] not in course_subjects:
            error_strings.add("Unknown course code")
            error_codes.append(subject)

    # If errors exist, print out errors and exit 
    if error_strings:
        for error_string in error_strings:
            if error_string == "Unknown course code":
                if len(error_codes) == 1:
                    print(error_string + ": ", end = "")
                else: print(error_string + "s: ", end = "")
                print(", ".join(error_codes))
            else:
                print(error_string)
        return -1
    return( {"credits": credits, "terms": terms, "levels": levels, "subjects": subjects})


"""
Searches through the JSON for courses matching the specification of the user
"""
def search(output, credits, terms, noprereq, subjects, levels):
    # Lists to hold matches for a given flag
    creditMatch = []  
    termMatch = [] 
    levelMatch = []
    subjectMatch = []
    prereqMatch = [] 

    # Dictionary from JSON data file was created earlier (output)
    for course in output['courses']:
        
        # Add all courses to creditMatch if not searching for a specific credit range. Otherwise, only add courses that match the criteria
        if len(credits) == 0:
            creditMatch.append(course['code'])
        elif course['creditWeight'] in credits:
            creditMatch.append(course['code'])
        
        # Add all courses to termMatch if not searching for specific terms. Otherwise, add only courses that match at least one of the terms
        if len(terms) == 0:
            termMatch.append(course['code'])
        else:
            # Perform set intersection to see if the course has terms that align with the search criteria
            result = set(course['term']) & set(terms) 
            if (len(result) > 0):
                termMatch.append(course['code'])
        
        # Only add courses without prerequestites to prereqMatch if searching for courses with no prerequesties, else add all of them
        if (noprereq == False):
            prereqMatch.append(course['code'])
        elif (course['prereq'] == 'No Data' ) and (noprereq == True):
            prereqMatch.append(course['code'])

        # Add all courses if not looking for a particular subject. Otherwise, add only courses that match the specfic subject code
        if len(subjects) == 0: 
            subjectMatch.append(course['code']) 
        else:
            result = course['code'].partition('*')
            if result[0] in subjects:
                subjectMatch.append(course['code'])

        # Adds all courses of the specified level to levelMatch. If no specific level is specified, add all courses 
        if len(levels) == 0: 
            levelMatch.append(course['code'])
        elif str(int(re.search("(?<=\*)\d{1}", course['code'])[0]) * 1000) in levels:  # Gets the level of the course
            levelMatch.append(course['code'])

    # Intersection of all of the flag matches
    return set(creditMatch) & set(termMatch) & set(prereqMatch) & set(subjectMatch) & set(levelMatch)

"""
Prints of the courses found by the search function into a user readable form
"""
def print_output(output, finalList):
    print("MATCHED COURSES:")
    print(" ")

    # Looping through output file and finalList from above to find a match on courde code and printing course info in acceptable format
    for allCourses in output['courses']:
        for formattedCourse in finalList:
            if formattedCourse == allCourses['code']:
                temp_term = allCourses['term']
                stripped_term = str(temp_term).replace('[','').replace(']','').replace('\'','').replace('\"','').replace(',','').replace(' ','')
                temp_offerings = allCourses['offerings']
                stripped_offerings = str(temp_offerings).replace ('[','').replace(']','').replace('\'','')

                print(allCourses['code'], allCourses['name'], stripped_term, "[" + allCourses['creditWeight'] + "]")
                print(allCourses['description'])
                print("Prerequisite(s):",  allCourses['prereq'])
                print("Equate(s):", allCourses['equivalent'])
                print("Offering(s):", stripped_offerings)
                print("Restriction(s):", allCourses['restrictions'])
                print("Department(s):", allCourses['department'])
                print("Location(s):", allCourses['location'])
                print(" ")

"""
Opens a JSON file and returns the data
"""
def getJSONData(json_location):
    if not os.path.exists(json_location):
        print("Error: JSON file not found")
        return -1

    f = open(json_location, "r")
    output = json.load(f)
    f.close()

    return output


if __name__ == '__main__':
    # Gets the correct file path based on the user's operating system
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        sysRelDefault = 'src/scraper/data/json_data.json'
        sysRelHelp = 'The location of the input json if not in scraper/data'
    elif platform.system() == 'Windows':
        sysRelDefault = 'src\scraper\data\json_data.json'
        sysRelHelp = 'The location of the input json if not in scraper\data'
    else: 
        print('Error: ' + platform.system() + ' not supported') 
        sys.exit()

    # Every flag accepts a list of arguments, except filelocation(relative path) and prereq(t/f)
    parser = argparse.ArgumentParser(description = 'A course search utility')
    parser.add_argument('-C', '-c', nargs = '*', default = [], help = 'The creditWeight of the desired courses (0.5 1.0) or range (0.5 - 1.0)', required = False, metavar = "creditWeight")
    parser.add_argument('-T', '-t', nargs = '*', default = [], help = 'Term of the desired courses (F)', required = False, metavar = "term")
    parser.add_argument('-L', '-l', nargs = '*', default = [], help = 'The levels of the desired courses (1000 3000) or range (1000 - 3000)', required = False, metavar = "level")
    parser.add_argument('-S', '-s', nargs = '*', default = [], help = 'The subject of the desired courses (CIS)', required = False, metavar = "subject")
    parser.add_argument('-I', '-i', nargs = '?', default = sysRelDefault, help = sysRelHelp, required = False, metavar = "\"filelocation\"")
    parser.add_argument('-P', '-p', default = False, help = 'Use this flag to search for courses with no prerequisites', required = False, action = "store_true")

    args = parser.parse_args()
    noprereq = args.P
    
    # Opening JSON data file
    output = getJSONData(args.I)
    if output == -1:
        sys.exit()

    parsed = argument_parser(output, args.C, args.T, args.L, args.S)
    if parsed == -1:
        sys.exit()

    finalList = search(output, parsed["credits"], parsed["terms"], noprereq, parsed["subjects"], parsed["levels"])

    print_output(output, finalList)
