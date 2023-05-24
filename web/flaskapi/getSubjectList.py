import json

def guelphList ():
  f = open ('scraped_course_data.json')
  courseList = json.load (f)
  courseCodeList = []

  for course in courseList['courses']:
    courseCodeList.append({'label':course['code'], 'value':course['code']})

  f.close()

  return courseCodeList

def carletonList ():
  f = open ('scraped_course_carleton_data.json')
  courseList = json.load (f)
  courseCodeList = []

  for course in courseList['courses']:
    courseCodeList.append({'label':course['code'], 'value':course['code']})

  f.close()

  return courseCodeList
