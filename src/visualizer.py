import graphviz as gv
import json
import argparse
import sys
import os
import platform
import re

# All valid output file formats
file_formats = ['bmp', 'cgimage', 'canon', 'dot', 'gv', 'xdot', 'eps', 'exr', 'fig', 'gif', 'ico', 'cmap', 'ismap', 'imap', 'jpg', 'jpeg', 'jpe', 'json', 'json0', 'dot_json', 'pdf', 'pic', 'pct', 'pict', 'plain', 'png', 'pov', 'ps', 'svg', 'tga', 'vml', 'xlib']

"""
Adds courses to the graph if they are not already in it 
"""
def makeNodeIfNotExists(graph, nodes, course_code, group):
    if course_code in nodes:
        # Node already exists, so do not create a new one
        return
    else:
        # Finds the course level
        if re.search("(?<=\*)\d{1}", course_code):
            level = int(re.search("(?<=\*)\d{1}", course_code)[0]) * 1000
        else:
            level = 0
        
        # Sets the colour of the node based on the course level
        if level == 1000:
            graph.attr('node', fillcolor="green", color="black", fontcolor = "black")
        elif level == 2000:
            graph.attr('node', fillcolor="blue", color="black", fontcolor = "white")
        elif level == 3000:
            graph.attr('node', fillcolor="purple", color="black", fontcolor = "white")
        elif level == 4000:
            graph.attr('node', fillcolor="orange", color="black", fontcolor = "black")
        elif level == 5000:
            graph.attr('node', fillcolor="blanchedalmond", color="black", fontcolor = "black")
        
        # Sets shape to box if not part of the subject being visualized
        if re.sub("\*\d+", "", course_code) != re.sub("\*\d+", "", group):
            graph.attr('node', shape="box", style="filled")
        else:
            graph.attr('node', shape="ellipse", style="filled")

        graph.node(course_code)
        nodes.add(course_code)
        
"""
Creates a legend subgraph and then adds it to the main graph
"""
def addLegend(graph):
    legend = gv.Digraph(name = "cluster_legend", node_attr={'shape': 'ellipse'})
    legend.attr(rankdir='LR', color="black", label="Legend")

    # Course levels and their colours
    legend.node("1000 Level Course", fillcolor="green", style="filled", color="black", fontcolor = "black")
    legend.node("2000 Level Course", fillcolor="blue", style="filled", color="black", fontcolor = "white")
    legend.node("3000 Level Course", fillcolor="purple", style="filled", color="black", fontcolor = "white")
    legend.node("4000 Level Course", fillcolor="orange", style="filled", color="black", fontcolor = "black")
    legend.node("5000 Level Course", fillcolor="blanchedalmond", style="filled", color="black", fontcolor = "black")

    # Other things that have meaning, e.g., shape
    legend.node("Different Subject\nor\nNon-Major Course", shape="box")
    legend.node("Required Prerequisite (AND)")
    legend.node("", "EXAMPLE*1000")
    legend.node("One of Prerequisite (OR)")

    # Edges between legend boxes for ordering and showing dashed lines
    legend.edge("Required Prerequisite (AND)", "")
    legend.edge("One of Prerequisite (OR)", "",  style="dashed")
    legend.edge("1000 Level Course", "3000 Level Course",  style="invis")
    legend.edge("2000 Level Course", "4000 Level Course",  style="invis")
    legend.edge("3000 Level Course", "5000 Level Course",  style="invis")
    legend.edge("", "Different Subject\nor\nNon-Major Course",  style="invis")

    graph.subgraph(legend)

"""
Creates a subgraph for extra credit requirements and then adds it to the main graph
"""
def createExtraRequirementsSubgraph(graph, requirements):
    extra_requirement_subgraph = gv.Digraph(name = "cluster_extra_requirements", node_attr={'shape': 'box'})
    extra_requirement_subgraph.attr(rankdir='LR', color="black", label="Extra Major Requirements", penwidth = "2.5")

    all_requirements = ""
    for extra_requirement in requirements:
        all_requirements += "\n" + extra_requirement + " - " + requirements[extra_requirement] + "\n"

    extra_requirement_subgraph.node(all_requirements, shape="box", fillcolor="white", color="white")
    graph.subgraph(extra_requirement_subgraph)
    graph.edge("Different Subject\nor\nNon-Major Course", all_requirements, lhead="cluster_extra_requirements", ltail="cluster_legend", style="invis")

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
def graphPrerequesites(graph, nodeExists, course_object, all_courses, course_code):
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
        graph.edge(j, course_object["code"])

    for j in course_object["prereq"]["OR"]:
        if all_courses:
            course_code = j
        makeNodeIfNotExists(graph, nodeExists, j, course_code)
        graph.edge(j, course_object["code"], style = "dashed")    


"""
Function used to create a graph of all majors related to a course
"""
def whatMajors(graph, course):
    course = ''.join(course).upper()
    
    # If the * is not given in the course code, add it
    if not '*' in course:
        coursename = re.search("\D+", course)[0] + "*" + re.search("\d+", course)[0]
    else:
        coursename = course
    graph.node(coursename, shape="box", fillcolor="lightsteelblue")
    
    program_information = []

    # Load JSON data from file
    if not os.path.exists("src/scraper/data/scraped_majors_data.json"):
        print("Error: scraped_majors_data.json file not found")
        exit()

    with open('src/scraper/data/scraped_majors_data.json', 'r') as fp:
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
Main function to create the graph
"""
def main():
    # Platform check for windows to add graphviz to the PATH
    if platform.system() == 'Windows':
        os.environ["PATH"] += os.pathsep + 'C:\\Program Files\\Graphviz\\bin\\'

    if not os.path.exists("src/scraper/data/scraped_course_data.json"):
        print("Error: scraped_course_data.json file not found")
        exit()

    # Get course information
    with open('src/scraper/data/scraped_course_data.json', 'r') as fp:
        course_information = json.load(fp)

    # Get available programs and courses
    programs = course_information["programs"]
    courses = course_information["courses"]

    # Grab program specification from command line
    parser = argparse.ArgumentParser(description="A course prerequisite visualization utility")
    parser.add_argument('-N', '-n', default = "graph", help = 'Name of graph pdf', required = False, metavar="filename")

    # Only one of -S and -M is allowed
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-S', '-s', default = "", help = 'Enter subject', required = False, metavar = "course")
    group.add_argument('-M', '-m', default = "", help = 'Enter major name', required = False, metavar = "major")
    group.add_argument('-C', '-c', nargs="*", default='', help='Enter a course to see what majors contain it', required=False, metavar="contains")
    parser.add_argument('-hor', '-HOR', default = False, help = 'Display graph horizontally', required = False, action = "store_true")
    parser.add_argument('-F', '-f', default='pdf', help='Enter file type (examples: ' + str(file_formats) + ')', required=False, metavar="filetype")
    
    # Don't let the user run without commands
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    
    args = parser.parse_args()

    all_courses = False

    # Deal with S flag, with error checking to see if the program actually exists
    if args.S == "":
        all_courses = True
    else:
        course_code = args.S.upper()
        if course_code.lower() not in programs:
            print("Error: Given program cannot be found")
            sys.exit()
    
    major = args.M.upper()

    if not args.C:
        # Graph used to visualize program course progression
        graph = gv.Digraph() 
        addLegend(graph)
    else:
        # Graph that circles around the course
        graph = gv.Digraph(engine="circo") 
    
    file_type = checkFileType(graph, str(args.F).lower())
    
    # Set graph attributes, like left-to-right direction, rank separations, node styles
    if args.hor:
        graph.attr(rankdir='LR')

    graph.attr(ranksep='1.4')    
    graph.attr(compound="true")
    graph.attr('node', style='filled')
    
    nodeExists = set()
    
    if args.C:
        if whatMajors(graph, args.C) == 0:
            print(f"No major has the course: {args.C[0]}")
            sys.exit()
    elif (major == ""):
        # Create graph of courses from specified program. Create graph with all programs if not specified
        for i in courses:
            if all_courses or i["code"].split('*')[0] == course_code:
                graphPrerequesites(graph, nodeExists, i, all_courses, course_code)
    else:
        # Major selected instead of a specific subject

        # Get major information
        if not os.path.exists("src/scraper/data/scraped_majors_data.json"):
            print("Error: scraped_majors_data.json file not found")
            exit()

        with open('src/scraper/data/scraped_majors_data.json', 'r') as fp:
            major_information = json.load(fp)
            program_information = []
            if "programs" in major_information:
                program_information = major_information["programs"]
                
        for program in program_information:
            if program == major:
                courses_to_graph = set(program_information[program]["courses"])
                # Create title node, replace : with _ in the node's name to deal with how graphviz parses names
                graph.node(program_information[program]["program_name"].replace(":", "_"), label=program_information[program]["program_name"], style="filled", fillcolor="grey", color="black", fontcolor = "black", fontsize="30", shape="plaintext")
                
                # Create oval shaped nodes for all major required courses
                for course in courses_to_graph:
                    makeNodeIfNotExists(graph, nodeExists, course, course)
                    # Have all nodes have edges with program name to put it above everything
                    graph.edge(program_information[program]["program_name"].replace(":", "_"), course, style="invis")
                
                for course in courses:
                    if course["code"] in courses_to_graph:
                        graphPrerequesites(graph, nodeExists, course, False, "")
                
                createExtraRequirementsSubgraph(graph, program_information[program]["extra_requirements"])
                break
        else:
            print("Error: Major does not exist")
            exit()


    # Create graph output based on file type
    graph.render(args.N, view=False)
    os.remove(args.N)
    print(f"Created graph {os.getcwd()}/{args.N}.{file_type}")
    
    fp.close()

if __name__ == "__main__":
    main()
