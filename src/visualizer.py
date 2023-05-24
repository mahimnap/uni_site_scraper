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
    legend.node("Different Subject Course", shape="box")
    legend.node("Required Prerequisite (AND)")
    legend.node("", "EXAMPLE*1000")
    legend.node("One of Prerequisite (OR)")

    # Edges between legend boxes for ordering and showing dashed lines
    legend.edge("Required Prerequisite (AND)", "")
    legend.edge("One of Prerequisite (OR)", "",  style="dashed")
    legend.edge("1000 Level Course", "3000 Level Course",  style="invis")
    legend.edge("2000 Level Course", "4000 Level Course",  style="invis")
    legend.edge("3000 Level Course", "5000 Level Course",  style="invis")
    legend.edge("", "Different Subject Course",  style="invis")

    graph.subgraph(legend)

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
Main function to create the graph
"""
def main():
    # Platform check for windows to add graphviz to the PATH
    if platform.system() == 'Windows':
        os.environ["PATH"] += os.pathsep + 'C:\\Program Files\\Graphviz\\bin\\'

    # Get course information
    with open('src/scraper/data/scraped_data.json', 'r') as fp:
        course_information = json.load(fp)

    # Get available programs and courses
    programs = course_information["programs"]
    courses = course_information["courses"]

    # Grab program specification from command line
    parser = argparse.ArgumentParser(description="A course prerequisite visualization utility")

    parser.add_argument('-S', '-s', default = "", help = 'Enter subject', required = False, metavar = "course")
    parser.add_argument('-hor', '-HOR', default = False, help = 'Display graph horizontally', required = False, action = "store_true")
    parser.add_argument('-N', '-n', default = "graph", help = 'Name of graph pdf', required = False)
    parser.add_argument('-F', '-f', nargs='?', default='pdf', help='Enter file type (examples: ' + str(file_formats) + ')', required=False, metavar="file")
    
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
    
    # Graph used to visualize program course progression
    A = gv.Digraph()
    file_type = checkFileType(A, str(args.F).lower())
    addLegend(A)
    
    # Set graph attributes, like left-to-right direction, rank separations, node styles
    if args.hor:
        A.attr(rankdir='LR')

    A.attr(ranksep='1.4')    
    A.attr('node', style='filled')
    
    nodeExists = set()

    # Create graph of courses from specified program. Create graph with all programs if not specified
    for i in courses:
        if all_courses or i["code"].split('*')[0] == course_code:
            # Make a node for the course if it doesn't exist already
            if all_courses:
                course_code = i["code"]
            makeNodeIfNotExists(A, nodeExists, i["code"], course_code)

            # If there are no prerequesites, go to the next iteration of the loop
            if i["prereq"] == "No Data":
                continue

            # Add edges and nodes for prerequisites as required
            for j in i["prereq"]["AND"]:
                if all_courses:
                    course_code = j
                makeNodeIfNotExists(A, nodeExists, j, course_code)
                A.edge(j, i["code"])

            for j in i["prereq"]["OR"]:
                if all_courses:
                    course_code = j
                makeNodeIfNotExists(A, nodeExists, j, course_code)
                A.edge(j, i["code"], style = "dashed")

    # Create graph output based on file type
    A.render(args.N, view=False)
    os.remove(args.N)
    print(f"Created graph {os.getcwd()}/{args.N}.{file_type}")
    
    fp.close()


if __name__ == "__main__":
    main()
