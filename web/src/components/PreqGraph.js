import './App.css'
import jQuery from "jquery";
import ReactDOM from "react-dom";
import React, { useState } from 'react';
import { Graphviz } from 'graphviz-react';
import { useLocation } from "react-router-dom";
import type { GraphvizOptions } from 'd3-graphviz';

var red_courses = [];
var results;
var saved_results;
var course_code = 'none';

function checkAdj(course){
    let rtn = true;
    let next = results.match(new RegExp("(?<=\").*?(?=\" -> \"" + course + "\")", "g"));
    if (next !== null){
        next.forEach(check => {
            if (check.indexOf('*') !== -1){
                let colour = results.match(new RegExp("(?<=" + check.replace("*", "\\*") + "\"\t \\[fillcolor=).*?,"));
                if (colour === null || colour[0] !== 'red,'){
                    rtn = false;
                }
            }
        });
        return rtn;
    }
}

function recurse(missing){
    missing.forEach(course => {
        course = course.replace("*", "\\*");

        // Recolour current node
        let contains_fillcolor = results.match(new RegExp("(?<=" + course + "\"\t \\[fillcolor=).*?,"));
        if (contains_fillcolor !== null){
            results = results.replace(new RegExp("(?<=" + course + "\"\t \\[fillcolor=).*?,"), "red,"); //replaces fill colour with red
        }else{
            results = results.replace(new RegExp("(?<=" + course + "\"\t \\[)height"), "fillcolor=red, height"); //adds red fill colour to node
        }
        //results = results.replace(new RegExp("(?<=" + course + "\"\t \\[fillcolor=red,.*?fontcolor=).*?,", "s"), "black,");


        // Get child nodes
        let next = results.match(new RegExp("(?<=" + course + "\" -> \").*?(?=\")", "g"));
        let make_red = [];
        if (next !== null){
            next.forEach(check => {
                // Get the arrow's properties
                let style = results.match(new RegExp("(?<=" + course + "\" -> \"" + check.replace("*", "\\*") + "\"\\s+\\[).*?(?=\\])", "gs"))[0];
                if (style.match(new RegExp("style=dashed", "gs")) !== null){ //OR
                    // Function to check if all nodes connected to check are red
                    if (checkAdj(check.replace("*", "\\*"))){
                        make_red.push(check);
                    }
                }else{ //AND
                    make_red.push(check);
                }
            });
            if (make_red !== []){
                recurse(make_red);
            }
        }
      });
}

function PreqGraph() {
    var dots = '';
	let location = useLocation();

    const { innerWidth, innerHeight } = window;
    const defaults: Options<GraphvizOptions> = {
        height: Math.floor(innerHeight * 0.8),
        width: Math.floor(innerWidth * 0.95),
        scale: 1,
        tweenPrecision: 1,
        engine: 'dot',
        keyMode: 'title',
        convertEqualSidedPolygons: false,
        fade: false,
        growEnteringEdges: false,
        fit: true,
        tweenPaths: false,
        tweenShapes: false,
        useWorker: false,
        zoom: true,
    };
    const [dot, setDot] = useState('graph { bgcolor="transparent" }');
    const [graphOptions, setGraphOptions] = useState(defaults);

    function update_nodes() {
        var anchors = document.getElementsByClassName('node');
        jQuery("title").remove();
        for(var i = 0; i < anchors.length; i++) {
            var anchor = anchors[i];
            // Adds an onclick function to all course code nodes
            if (anchor.__data__.key.search("\\*") !== -1 && anchor.__data__.key.length > 6){
                anchor.onclick = function() {
                    let pos = red_courses.indexOf(this.__data__.key);
                    if (pos == -1){
                        red_courses.push(this.__data__.key);
                    }else{
                        red_courses.splice(pos, 1);
                    }
                    results = saved_results;
                    recurse(red_courses);
                    let save_pos = document.getElementById('graph0').getAttribute('transform');
                    setDot(results);
                    jQuery("title").remove();
                    document.getElementById('graph0').setAttribute('transform', save_pos);
                }
                anchor.ondblclick = function() {
                    jQuery.ajax({
                        type: "get",
                        dataType: "json",
                        url: "/api/guelphmoreinfo",
                        data: {
                            code: this.__data__.key,
                        },
                        success: function (data) {
                            let values = data['results']
                            alert("Course Code: " + values['code'] + "\nName: " + values['name'] + "\nDescription: " + values['description'] + "\nWeight: " + values['creditWeight'] +
                            "\nDepartment: " + values['department'] + "\nEquivalent Courses: " + values['equivalent'] + "\nLocation: " + values['location']);
                        },
                        fail: function (error) {
                            alert(error);
                        },
                    });
			    }
            }
        }
    }

    if (course_code !== location.state.substring(1)){
        course_code = location.state.substring(1);
        let carleton = location.state.charAt(0) == 'g' ? false : true;
		let url = "/api/preqs";
		if (carleton === true){
			url = "/api/carlpreqs";
		}
        red_courses = [];
        jQuery.ajax({
            type: "get",
            dataType: "json",
            url: url,
            data: {
                code: course_code,
                carleton: carleton
            },
            success: function (data) {
                // Gets rid of the junk put in by python
                dots = data.results.substring(2, data.results.length - 1);
                dots = dots.replaceAll('\\n', '\n').replaceAll('\\t', '\t').replaceAll('\\"', '"').replace('label="\\\\N",', '').replace('\\\\,', '');
                saved_results = dots;
                setDot(dots);
                update_nodes();
            },
            fail: function (error) {
                alert(error);
            },
        });
	}

	return(<div className="App-body"><div id="graph"><Graphviz dot={dot} options={graphOptions}/></div></div>);
}

export default PreqGraph;
