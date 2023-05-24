#if changes are made: sudo systemctl restart flaskapi

from flask import Flask, request, send_file
from visualizer import send_preqs, graph_major, create_graph, send_subjects
from website_search import executeSearch
from getSubjectList import guelphList, carletonList
from moreInfo import carletonCourseInfo, guelphCourseInfo
import json

app = Flask(__name__, static_folder='../build', static_url_path='/')

@app.route('/')
def index():
  return app.send_static_file('index.html')

@app.route('/api/homeuog')
def uog_image():
  return send_file ('uog.jpg')

@app.route('/api/graphExample')
def graph():
  return app.send_static_file('graphold.html')

@app.route('/api/dotFile')
def dotFile():
  return {"results": graph_major(request.args['major'], request.args['carletonFlag'], request.args['multiMajor'], request.args['graph_name'])}


@app.route('/api/guelphSubjectSearch')
def guelphSubjectSearch():
  return {"results": send_subjects(request.args['subject_name'])}
  #return {"results": create_graph(request.args['course_code'], request.args['course_name'], request.args['hor'], request.args['file'], request.args['carletonFlag'], request.args['name'], request.args['all_courses'], request.args['major'], finalSubjectList, request.args['pages'], request.args['course_information'], request.args['program_information'])}

#def create_graph(course_code, course_name, hor, file, carletonFlag, name, all_courses, major, courses, pages, course_information, program_information)
#
'''
@app.route('/api/carletonSubjectSearch')
def carletonSubjectSearch():
    user_subject = request.args['course_name'] #call course_name on frontend ajax
    return {"results": create_graph(request.args['course_code'], request.args['course_name'], request.args['hor'], request.args['file'], request.args['carletonFlag'], request.args['name'], request.args['all_courses'], request.args['major'], request.args['courses'], request.args['pages'], request.args['course_information'], request.args['program_information'])}
'''   
    
@app.route('/api/pdfGraph')
def pdfgraph():
  return app.send_static_file('pdfgraph.html')

@app.route ('/api/preqs')
def preqs():
  return {"results": send_preqs(request.args['code'], 'false')}
    #return {"results": send_preqs(request.args['code'], request.args['carleton'])}

@app.route ('/api/carlpreqs')
def carlpreqs():
  return {"results": send_preqs(request.args['code'], 'true')}

@app.route ('/api/guelphsubjectlist')
def guelph_list ():
  return {"results":guelphList()}

@app.route ('/api/carletonsubjectlist')
def carleton_list ():
  return {"results":carletonList()}

@app.route ('/api/guelphmoreinfo')
def guelph_more_info ():
  return {"results": guelphCourseInfo(request.args['code'])}

@app.route ('/api/carletonmoreinfo')
def carleton_more_info ():
  return {"results": carletonCourseInfo(request.args['code'])}

@app.route ('/api/search')
def get_form_inputs():
 userPrereq = request.args['prereqs'].lower()

 if userPrereq == 'yes':
   boolPrereq = False
 else:
   boolPrereq = True

 # Get Subject search criteria
 userSubjects = request.args['subjects']
 subjectList = userSubjects.strip().replace(",", " ").split(' ')
 if userSubjects == '':
   subjectList = []

 # Get School term search criteria
 userTerms = request.args['terms']
 termList = userTerms.strip().split(' ')

 # Get course weight search criteria
 userCredits = request.args['credits']

 # Filter characters
 for char in userCredits:
     if not char.isdigit() and char not in ['-', ',', ' ', '.']:
         return {"error": "Course weight must be numeric!"}

 # Replace commas and spaces
 creditList = userCredits.strip().replace(",", " ").split(' ')

 # Check for argument values
 if ("-" in creditList and len(creditList) == 2) or len(creditList) > 3 or (len(creditList) == 3 and "-" not in creditList):
    return {"error": "Invalid course weight format!"}


 # Number checking credits
 for credit in creditList:
     if credit != "-":
         try:
             numCheck = float(credit)
             if numCheck % 0.25 != 0:
                 return {"error": "Course weight must be divisble by 0.25!"}
             if numCheck < 0:
                 return {"error": "Course weight must be positive!"}
         except Exception as e:
             return {"error": "Course weight must be a number!"}

 # Get course level search criteria
 userLevels = request.args['levels']

 # Filter characters
 for char in userLevels:
     if not char.isdigit() and char not in ["-", ' ', ',']:
         return {"error": "Course levels must be numeric!"}

 # Replace commas and spaces
 levelList = userLevels.strip().replace(",", " ").split(' ')

 # Check for argument values
 if ("-" in levelList and len(levelList) == 2) or len(levelList) > 3 or (len(levelList) == 3 and '-' not in levelList):
    return {"error": "Invalid course level format!"}

 # Number checking levels
 for level in levelList:
     if level != "-":
         try:
             numCheck = float(level)
             if numCheck < 0:
                 return {"error": "Course level must be positive!"}
         except Exception as e:
             return {"error": "Course level must be a number!"}

 return {"results":json.dumps(executeSearch(boolPrereq, creditList, termList, levelList, subjectList, request.args['university'].lower()))}

