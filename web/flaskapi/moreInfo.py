import json

def guelphCourseInfo (searchVal):
    f = open ('scraped_course_data.json')

    myList = json.load (f)
    result = None
    for course in myList['courses']:
        if course['code'] == searchVal:
            return course

    f.close()

    return 'Nothing Found'

def carletonCourseInfo (searchVal):
    f = open ('scraped_course_carleton_data.json')

    myList = json.load (f)
    result = None
    for course in myList['courses']:
        if course['code'] == searchVal:
            return course

    f.close()

    return 'Nothing Found'
