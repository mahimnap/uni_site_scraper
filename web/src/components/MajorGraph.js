import './App.css'
import jQuery from "jquery";
import ReactDOM from "react-dom";
import React, { useState } from 'react';
import { Graphviz } from 'graphviz-react';
import { useLocation } from "react-router-dom";
import type { GraphvizOptions } from 'd3-graphviz';
import Select from 'react-select';

const majorList = [
    {label:'ABIO', value:'ABIO'}, {label:'ACCT', value:'ACCT'}, {label:'ACCT:C', value:'ACCT:C'}, {label:'AHN', value:'AHN'}, {label:'ANTH', value:'ANTH'},
    {label:'ANTH:C', value:'ANTH:C'}, {label:'ARTH', value:'ARTH'}, {label:'B.L.A.', value:'B.L.A.'}, {label:'BIESP', value:'BIESP'}, {label:'BIOC', value:'BIOC'},
    {label:'BIOD', value:'BIOD'}, {label:'BIOE', value:'BIOE'}, {label:'BIOE:C', value:'BIOE:C'}, {label:'BIOM', value:'BIOM'}, {label:'BME', value:'BME'},
    {label:'BME:C', value:'BME:C'}, {label:'BMPH', value:'BMPH'}, {label:'BMPH:C', value:'BMPH:C'}, {label:'BPCH', value:'BPCH'}, {label:'BPCH:C', value:'BPCH:C'},
    {label:'BTOX', value:'BTOX'}, {label:'BTOX:C', value:'BTOX:C'}, {label:'CENG', value:'CENG'}, {label:'CENG:C', value:'CENG:C'},{label:'CHEM', value:'CHEM'}, 
    {label:'CHEM:C', value:'CHEM:C'}, {label:'CHPY', value:'CHPY'}, {label:'CHPY:C', value:'CHPY:C'}, {label:'CJPP', value:'CJPP'}, {label:'CJPP:C', value:'CJPP:C'},
    {label:'CLAS', value:'CLAS'}, {label:'CS', value:'CS'}, {label:'CS:C', value:'CS:C'}, {label:'CSTU', value:'CSTU'}, {label:'D.V.M.', value:'D.V.M.'},
    {label:'ECOL', value:'ECOL'}, {label:'ECOL:C', value:'ECOL:C'}, {label:'ECON', value:'ECON'}, {label:'ECON:C', value:'ECON:C'}, {label:'EEP', value:'EEP'},
    {label:'EEP:C', value:'EEP:C'}, {label:'EG', value:'EG'}, {label:'EG:C', value:'EG:C'}, {label:'EM:C', value:'EM:C'}, {label:'ENGL', value:'ENGL'},
    {label:'ENVB', value:'ENVB'}, {label:'ENVE', value:'ENVE'}, {label:'ENVE:C', value:'ENVE:C'}, {label:'ENVS', value:'ENVS'}, {label:'ENVS:C', value:'ENVS:C'},
    {label:'EQM:C', value:'EQM:C'}, {label:'ERM', value:'ERM'}, {label:'ERM:C', value:'ERM:C'}, {label:'ESC', value:'ESC'}, {label:'ESC:C', value:'ESC:C'},
    {label:'EURS', value:'EURS'}, {label:'FAB', value:'FAB'}, {label:'FARE', value:'FARE'}, {label:'FARE:C', value:'FARE:C'}, {label:'FOOD', value:'FOOD'},
    {label:'FOOD:C', value:'FOOD:C'}, {label:'FREN', value:'FREN'}, {label:'FSHD', value:'FSHD'}, {label:'GEM', value:'GEM'}, {label:'GEM:C', value:'GEM:C'},
    {label:'GEOG', value:'GEOG'}, {label:'GEOG:C', value:'GEOG:C'}, {label:'HIST:C', value:'HIST:C'}, {label:'HK', value:'HK'}, {label:'HTM', value:'HTM'},
    {label:'HTM:C', value:'HTM:C'}, {label:'IDS', value:'IDS'}, {label:'MAEC', value:'MAEC'}, {label:'MAEC:C', value:'MAEC:C'}, {label:'MBG', value:'MBG'},
    {label:'MBG:C', value:'MBG:C'}, {label:'MECH', value:'MECH'}, {label:'MEF', value:'MEF'}, {label:'MEF:C', value:'MEF:C'}, {label:'MFB', value:'MFB'},
    {label:'MFB:C', value:'MFB:C'}, {label:'MGMT', value:'MGMT'}, {label:'MGMT:C', value:'MGMT:C'}, {label:'MICR', value:'MICR'}, {label:'MICR:C', value:'MICR:C'},
    {label:'MKMN', value:'MKMN'}, {label:'MKMN:C', value:'MKMN:C'}, {label:'MSCI', value:'MSCI'}, {label:'MUSC', value:'MUSC'}, {label:'NANO', value:'NANO'},
    {label:'NANO:C', value:'NANO:C'}, {label:'NANS', value:'NANS'}, {label:'NEUR', value:'NEUR'}, {label:'PHIL', value:'PHIL'}, {label:'PHYS', value:'PHYS'},
    {label:'PHYS:C', value:'PHYS:C'}, {label:'PLSC', value:'PLSC'}, {label:'PLSC:C', value:'PLSC:C'}, {label:'POLS', value:'POLS'}, {label:'POLS:C', value:'POLS:C'},
    {label:'PSCI', value:'PSCI'}, {label:'PSYC', value:'PSYC'}, {label:'RE', value:'RE'}, {label:'RE:C', value:'RE:C'}, {label:'SART', value:'SART'},
    {label:'SENG', value:'SENG'}, {label:'SENG:C', value:'SENG:C'}, {label:'SOC', value:'SOC'}, {label:'SPAH', value:'SPAH'}, {label:'SPMT', value:'SPMT'},
    {label:'SPMT:C', value:'SPMT:C'}, {label:'THPY', value:'THPY'}, {label:'THST', value:'THST'}, {label:'WBC', value:'WBC'}, {label:'WRE', value:'WRE'},
    {label:'WRE:C', value:'WRE:C'}, {label:'ZOO', value:'ZOO'}
  ]

var red_courses = [];
var results;
var saved_results;

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

function MajorGraph() {
	const { innerWidth, innerHeight } = window;
	const [selectValue,setSelectValue] = useState("")

	const defaults: Options<GraphvizOptions> = {
		height: Math.floor(innerHeight * 0.7),
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

	const handler = (event) => {
	  const value = event.value;
	  setSelectValue(value);
	  red_courses = [];

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

        var dots = '';
        jQuery.ajax({
            type: "get",
            dataType: "json",
            url: "/api/dotFile",
            data: {
                major: value,
                carletonFlag: false,
                multiMajor: false,
                graph_name: "graph"
            },
            success: function (data) {
                // Gets rid of the junk put in by python
                dots = data.results.substring(2, data.results.length - 1);
                dots = dots.replaceAll('\\n', '\n').replaceAll('\\t', '\t').replaceAll('\\"', '"').replace('label="\\\\N",', '').replace('\\\\,', '');
                saved_results = dots;
                setDot(dots);
                update_nodes(setDot, saved_results);
            },
            fail: function (error) {
                alert(error);
            },
        });
	}
	
	return(
	<div className="App-body">
        <form>
            <Select 
              className = "App-select" 
              onChange={handler}
              options={majorList}
            />
        
        </form>
		<h1>{selectValue}</h1>
		<div id="graph"><Graphviz dot={dot} options={graphOptions}/></div>
	</div>
	);
}

export default MajorGraph;