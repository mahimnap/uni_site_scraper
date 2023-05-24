import graphviz as gv
import json
import argparse
import sys
import os
import platform
import re
import shutil

# All valid output file formats
file_formats = ['bmp', 'cgimage', 'canon', 'dot', 'gv', 'xdot', 'eps', 'exr', 'fig', 'gif', 'ico', 'cmap', 'ismap',
                'imap', 'jpg', 'jpeg', 'jpe', 'json', 'json0', 'dot_json', 'pdf', 'pic', 'pct', 'pict', 'plain', 'png',
                'pov', 'ps', 'svg', 'tga', 'vml', 'xlib']

"""
Adds courses to the graph if they are not already in it 
"""


def makeNodeIfNotExists(graph, nodes, course_code, group):
    if course_code in nodes:
        # Node already exists, so do not create a new one
        return False
    else:
        # Finds the course level
        if re.search(r"(?<=\*)\d{1}", course_code):
            level = int(re.search(r"(?<=\*)\d{1}", course_code)[0]) * 1000
        else:
            level = -1

        # Sets the colour of the node based on the course level
        if level == -1:
            graph.attr('node', fillcolor="white", color="black", fontcolor="black")
        if level == 0:
            graph.attr('node', fillcolor="palevioletred1", color="black", fontcolor="black")
        elif level == 1000:
            graph.attr('node', fillcolor="green", color="black", fontcolor="black")
        elif level == 2000:
            graph.attr('node', fillcolor="blue", color="black", fontcolor="white")
        elif level == 3000:
            graph.attr('node', fillcolor="purple", color="black", fontcolor="white")
        elif level == 4000:
            graph.attr('node', fillcolor="orange", color="black", fontcolor="black")
        elif level == 5000:
            graph.attr('node', fillcolor="blanchedalmond", color="black", fontcolor="black")
        elif level == 6000:
            graph.attr('node', fillcolor="cyan", color="black", fontcolor="black")
        elif level == 7000:
            graph.attr('node', fillcolor="firebrick", color="black", fontcolor="black")

        # Sets shape to box if not part of the subject being visualized
        if re.sub(r"\*\d+", "", course_code) != re.sub(r"\*\d+", "", group):
            graph.attr('node', shape="box", style="filled")
        else:
            graph.attr('node', shape="ellipse", style="filled")

        graph.node(course_code)
        nodes.add(course_code)
        return True


"""
Creates a legend subgraph and then adds it to the main graph
"""


def addLegend(graph, carletonFlag):
    legend = gv.Digraph(name="cluster_legend", node_attr={'shape': 'ellipse'})
    legend.attr(rankdir='LR', color="black", label="Legend")

    # Course levels and their colours
    if carletonFlag:
        legend.node("0000 Level Course", fillcolor="palevioletred1", style="filled", color="black", fontcolor="black")
        legend.node("6000 Level Course", fillcolor="cyan", style="filled", color="black", fontcolor="black")
        legend.node("7000 Level Course", fillcolor="firebrick", style="filled", color="black", fontcolor="black")
    legend.node("1000 Level Course", fillcolor="green", style="filled", color="black", fontcolor="black")
    legend.node("2000 Level Course", fillcolor="blue", style="filled", color="black", fontcolor="white")
    legend.node("3000 Level Course", fillcolor="purple", style="filled", color="black", fontcolor="white")
    legend.node("4000 Level Course", fillcolor="orange", style="filled", color="black", fontcolor="black")
    legend.node("5000 Level Course", fillcolor="blanchedalmond", style="filled", color="black", fontcolor="black")

    # Other things that have meaning, e.g., shape
    legend.node("Different Subject\nor\nNon-Major Course", shape="box")
    legend.node("Required Prerequisite (AND)")
    legend.node("", "EXAMPLE*1000")
    legend.node("One of Prerequisite (OR)")

    # Edges between legend boxes for ordering and showing dashed lines
    legend.edge("Required Prerequisite (AND)", "")
    legend.edge("One of Prerequisite (OR)", "", style="dashed")

    if carletonFlag:
        legend.edge("4000 Level Course", "7000 Level Course", style="invis")
        legend.edge("3000 Level Course", "6000 Level Course", style="invis")
        legend.edge("2000 Level Course", "5000 Level Course", style="invis")
        legend.edge("1000 Level Course", "4000 Level Course", style="invis")
        legend.edge("0000 Level Course", "3000 Level Course", style="invis")
    else:
        legend.edge("3000 Level Course", "5000 Level Course", style="invis")
        legend.edge("2000 Level Course", "4000 Level Course", style="invis")
        legend.edge("1000 Level Course", "3000 Level Course", style="invis")

    legend.edge("", "Different Subject\nor\nNon-Major Course", style="invis")

    graph.subgraph(legend)


"""
Creates a subgraph for extra credit requirements and then adds it to the main graph
"""


def createExtraRequirementsSubgraph(graph, requirements):
    extra_requirement_subgraph = gv.Digraph(name="cluster_extra_requirements", node_attr={'shape': 'box'})
    extra_requirement_subgraph.attr(rankdir='LR', color="black", label="Extra Major Requirements", penwidth="2.5")

    all_requirements = ""
    for extra_requirement in requirements:
        all_requirements += "\n" + extra_requirement + " - " + requirements[extra_requirement] + "\n"

    if all_requirements == "":
        all_requirements = "No Extra Requirements"

    extra_requirement_subgraph.node(all_requirements, shape="box", fillcolor="white", color="white")
    graph.subgraph(extra_requirement_subgraph)
    graph.edge("Different Subject\nor\nNon-Major Course", all_requirements, lhead="cluster_extra_requirements",
               ltail="cluster_legend", style="invis")


"""
Check file type from command line to check if its an allowed file type
"""


def checkFileType(graph, fileType):
    if fileType not in file_formats:
        print(f"File type {fileType} not supported, defaulting to pdf")
        graph.format = 'pdf'
        return 'pdf'
    else:
        graph.format = str(fileType)
        return str(fileType)


"""
Function used to graph prerequesites of a course
"""


def graphPrerequesites(graph, nodeExists, course_object, all_courses, course_code, recurse=False, courses=None,
                       edge_set=None):
    if all_courses:
        course_code = course_object["code"]
    makeNodeIfNotExists(graph, nodeExists, course_object["code"], course_code)

    # If there are no prerequesites, go to the next iteration of the loop
    if course_object["prereq"] == "No Data":
        return

    # Add edges and nodes for prerequisites as required
    for j in course_object["prereq"]["AND"]:
        if all_courses:
            course_code = j
        makeNodeIfNotExists(graph, nodeExists, j, course_code)
        if j + course_object["code"] not in edge_set:
            graph.edge(j, course_object["code"], style="dashed")
            edge_set.add(j + course_object["code"])
            edge_set.add(course_object["code"] + j)
        if recurse:
            for course in courses:
                if course['code'] == j:
                    graphPrerequesites(graph, nodeExists, course, False, j, recurse=True, courses=courses,
                                       edge_set=edge_set)
                    break

    for j in course_object["prereq"]["OR"]:
        if all_courses:
            course_code = j
        makeNodeIfNotExists(graph, nodeExists, j, course_code)
        if j + course_object["code"] not in edge_set:
            graph.edge(j, course_object["code"], style="dashed")
            edge_set.add(j + course_object["code"])
            edge_set.add(course_object["code"] + j)
        if recurse:
            for course in courses:
                if course['code'] == j:
                    graphPrerequesites(graph, nodeExists, course, False, j, recurse=True, courses=courses,
                                       edge_set=edge_set)
                    break


"""
Function used to create a graph of all majors related to a course
"""


def whatMajors(graph, course):
    course = ''.join(course).upper()

    # If the * is not given in the course code, add it
    if '*' not in course:
        coursename = re.search(r"\D+", course)[0] + "*" + re.search(r"\d+", course)[0]
    else:
        coursename = course
    graph.node(coursename, shape="box", fillcolor="lightsteelblue")

    program_information = []

    # Load JSON data from file
    if not os.path.exists("scraped_majors_data.json"):
        print("Error: scraped_majors_data.json file not found")
        exit()

    with open('scraped_majors_data.json', 'r') as fp:
        major_information = json.load(fp)
        if "programs" in major_information:
            program_information = major_information["programs"]

    majors = []
    for programcode, program in program_information.items():
        # If we find the course in one of the programs, add create a node for that major
        if coursename in program['courses']:
            majors.append(program['program_name'])

            # Create major node, replace : with _ in the node's name to deal with how graphviz parses names
            graph.node(programcode.replace(":", "_"), label=program['program_name'], fillcolor="aquamarine3")
            graph.edge(coursename, programcode.replace(":", "_"))

    return len(majors)


"""
Function to find the Carelton subject name give the course code
"""


def get_subject_name(course_information, course_code, carletonFlag):
    if not carletonFlag or not "Subjects" in course_information:
        return course_code
    for subject_name, subject_code in course_information["Subjects"].items():
        if subject_code == course_code:
            return subject_name + " " + f"({course_code})"


"""
Function used to create all types of graphs
"""


def create_graph(course_code, course_name, hor, file, carletonFlag, name, all_courses, major, courses, pages,
                 course_information, program_information):
    if not course_name:
        # Graph used to visualize program course progression
        graph = gv.Digraph()
        addLegend(graph, carletonFlag)
    else:
        # Graph that circles around the course
        graph = gv.Digraph(engine="circo")

        # if not pages:
    #    file_type = checkFileType(graph, str(file).lower())

    if major == "EURS": return

    # Set graph attributes, like left-to-right direction, rank separations, node styles
    if hor:
        graph.attr(rankdir='LR')

    graph.attr(ranksep='1.4')
    if carletonFlag:
        graph.attr(ranksep='2')

    graph.attr(compound="true")
    graph.attr('node', style='filled')

    nodeExists = set()

    if course_name:
        if whatMajors(graph, course_name) == 0:
            print(f"No major has the course: {course_name[0]}")
            sys.exit()
    elif (major == ""):
        # Create graph of courses from specified program. Create graph with all programs if not specified
        graph.node(course_code, label=get_subject_name(course_information, course_code, carletonFlag), style="filled",
                   fillcolor="grey", color="black", fontcolor="black", fontsize="30", shape="plaintext")
        for course in courses:
            if all_courses or course["code"].split('*')[0] == course_code:
                graphPrerequesites(graph, nodeExists, course, False, "", edge_set=set())
                graph.edge(course_code, course["code"], style="invis")

                # Replaces incorrect year standing with the appropriate one
                if carletonFlag and course["year_standing"] != "No Required Year":
                    d = {"incorrect": ["irst-year", "econd-year", "hird-year", "ourth-year"]}
                    i = 1
                    correct = True
                    toCheck = course["year_standing"]
                    for w in toCheck.split(' '):
                        if w in d["incorrect"]:
                            if w == "irst-year":
                                makeNodeIfNotExists(graph, nodeExists, "first-year standing".title(), course_code)
                                graph.edge("first-year standing".title(), course["code"])
                                graph.edge(course_code, "first-year standing".title(), style="invis")
                                correct = False
                            elif w == "econd-year":
                                makeNodeIfNotExists(graph, nodeExists, "second-year standing".title(), course_code)
                                graph.edge("second-year standing".title(), course["code"])
                                graph.edge(course_code, "second-year standing".title(), style="invis")
                                correct = False
                            elif w == "hird-year":
                                makeNodeIfNotExists(graph, nodeExists, "third-year standing".title(), course_code)
                                graph.edge("third-year standing".title(), course["code"])
                                graph.edge(course_code, "third-year standing".title(), style="invis")
                                correct = False
                            elif w == "ourth-year":
                                makeNodeIfNotExists(graph, nodeExists, "fourth-year standing".title(), course_code)
                                graph.edge("fourth-year standing".title(), course["code"])
                                graph.edge(course_code, "fourth-year standing".title(), style="invis")
                                correct = False
                            i += 1
                    if correct:
                        makeNodeIfNotExists(graph, nodeExists, course["year_standing"].title(), course_code)
                        graph.edge(course["year_standing"].title(), course["code"])
                        graph.edge(course_code, course["year_standing"].title(), style="invis")
    else:
        # Major selected instead of a specific subject

        # Get major information
        if not os.path.exists("scraped_majors_data.json"):
            print("Error: scraped_majors_data.json file not found")
            exit()

        for program in program_information:
            if program == major:
                courses_to_graph = set(program_information[program]["courses"])
                # Create title node, replace : with _ in the node's name to deal with how graphviz parses names
                graph.node(program_information[program]["program_name"].replace(":", "_"),
                           label=program_information[program]["program_name"], style="filled", fillcolor="grey",
                           color="black", fontcolor="black", fontsize="30", shape="plaintext")

                # Create oval shaped nodes for all major required courses
                for course in courses_to_graph:
                    makeNodeIfNotExists(graph, nodeExists, course, course)
                    # Have all nodes have edges with program name to put it above everything
                    graph.edge(program_information[program]["program_name"].replace(":", "_"), course, style="invis")

                for course in courses:
                    if course["code"] in courses_to_graph:
                        graphPrerequesites(graph, nodeExists, course, False, "", edge_set=set())

                createExtraRequirementsSubgraph(graph, program_information[program]["extra_requirements"])
                break
        else:
            print("Error: Major does not exist")
            exit()
    return str(graph.pipe('gv'))


"""
Main function to create the graph
"""


def graph_major(major, carletonFlag, multiMajor, graph_name):
    course = ""
    course_contain = ""
    current_course = ""
    if carletonFlag == 'false':
        carletonFlag = False
    else:
        carletonFlag = True
        
    if multiMajor == 'false':
        multiMajor = False
    else:
        multiMajor = True

    all_courses = False
    course_code = ""
    program_information = None

    if carletonFlag and (course_contain != "" or multiMajor):
        print("Error: option unavailable with Carleton courses")
        exit()

    if not carletonFlag:
        if not os.path.exists("scraped_course_data.json"):
            print("Error: scrapon file not found")
            exit()

        # Get course information
        with open('scraped_course_data.json', 'r') as fp:
            course_information = json.load(fp)
    else:
        if not os.path.exists("scraped_course_carleton_data.json"):
            print("Error: scrapn_data.json file not found")
            exit()

        # Get course information
        with open('scraped_course_carleton_data.json', 'r') as fp:
            course_information = json.load(fp)

    # Get available programs and courses
    if carletonFlag == False:
        programs = course_information["programs"]
        # Get Guelph's major information
        with open('scraped_majors_data.json', 'r') as fp:
            major_information = json.load(fp)
            program_information = []
            if "programs" in major_information:
                program_information = major_information["programs"]

    courses = course_information["courses"]

    # Deal with S flag, with error checking to see if the program actually exists
    if course == "":
        all_courses = True
    else:
        course_code = course.upper()
        if not carletonFlag and course_code.lower() not in programs:
            print("Error: Given program cannot be found")
            sys.exit()

    major = major.upper()

    course_list = set()
    for course in courses:
        course_list.add(re.search(r".*(?=\*)", course['code'])[0])
    fp.close()
    # Loops through all Carleton subjects if only the carleton flag is set
    if carletonFlag and course_contain != "" and course != "":
        # Creates a temp directory to create all the graphviz files in
        if not os.path.exists('temp'):
            os.mkdir('temp')
        for course in course_list:
            return create_graph(course, course_contain, False, None, carletonFlag, 'temp/', False, major, courses, True,
                         course_information, None)
            print(f'Create {course} graph')
    elif multiMajor == True:
        # Creates a t=emp directory to create all the graphviz files in
        if not os.path.exists('temp'):
            os.mkdir('temp')
        for mjr in program_information:
            return create_graph(course, course_contain, False, None, carletonFlag, 'temp/', False, mjr, courses, True,
                         course_information, program_information)
            print(f'Create {mjr} graph')
    else:
        # Normal one page graph
        return create_graph(course_code, course_contain, False, None, carletonFlag, graph_name, all_courses, major, courses,
                     False, course_information, program_information)

def send_preqs(course_code, carletonFlag):
    graph = gv.Digraph()
    if carletonFlag == 'false':
        carletonFlag = False
    else:
        carletonFlag = True
    addLegend(graph, carletonFlag)
    graph.attr(ranksep='1.4')
    if carletonFlag:
        graph.attr(ranksep='2')

    graph.attr(compound="true")
    graph.attr('node', style='filled')

    if not carletonFlag:
        if not os.path.exists("scraped_course_data.json"):
            print("Error: scraped_course_data.json file not found")
            exit()

        # Get course information
        with open('scraped_course_data.json', 'r') as fp:
            course_information = json.load(fp)
    else:
        if not os.path.exists("scraped_course_carleton_data.json"):
            print("Error: scraped_course_carleton_data.json file not found")
            exit()

        # Get course information
        with open('scraped_course_carleton_data.json', 'r') as fp:
            course_information = json.load(fp)

    # Recursively graphs all preqs of course_code
    for course in course_information["courses"]:
        if course['code'] == course_code:
            graphPrerequesites(graph, set(), course, False, course_code, recurse=True,
                               courses=course_information["courses"], edge_set=set())
            break

    # Returns a dot file as a string
    return str(graph.pipe('gv'))

