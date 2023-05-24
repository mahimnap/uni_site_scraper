from flask import Flask, request
from website_search import executeSearch

app = Flask(__name__, static_folder='../build', static_url_path='/')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/graphExample')
def graph():
    return app.send_static_file('graph.html')

@app.route('/api/search')
def get_search_results():
    #boolPrereq = request.args['prereqs']
    #credits = request.args['credits']
    #terms = request.args['terms']
    #levels = request.args['levels']
    #subjects = request.args['subjects']
    return {"results":str(executeSearch (False, ['0.5'], ['F'], ['2000'], ['CIS']))}

