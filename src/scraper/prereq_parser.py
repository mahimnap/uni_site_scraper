import re

"""
This function removes text not related to course codes from the prerequesites
"""
def cleanPrerequisites(line):
    # Checking if theres course prereqs at all
    if '*' not in line:
        return "No Data"
        
    # Capitalizing OR, AND, and OF, and fixing 1of case for easier parsing in the future
    m = re.sub(r'\bor\b', 'OR', line)
    m = re.sub(r'\band\b', 'AND', m)
    m = re.sub(r'\bof\b', 'OF', m)
    m = re.sub(r'1of', '1 OF', m)
    
    # Regex that removes course credit requirement words
    m = re.sub(r'\b[0-9]+\.[0-9]+\b', '', m)
    
    # Regex that removes all words that are fully lower case
    m = re.sub(r'\b[a-z]+\b', '', m)
    
    # Regex that removes all words that start with a capital letter
    m = re.sub(r'\b[A-Z]{1}[a-z]*\b', '', m)

    # Regex that removes percentages
    m = re.sub(r'[0-9]*%', '', m)
    
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
    
    # Regex that removes extra whitespace and dots and colons
    m = re.sub(r'^\s+', '', m)
    m = re.sub(r'\s+', ' ', m)
    m = re.sub(r'[.:]', '', m)
    
    return m

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
