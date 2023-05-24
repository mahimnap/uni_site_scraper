import './App.css'
import jQuery from "jquery";
import ReactDOM from "react-dom";
import React, { useState } from 'react';
import { Graphviz } from 'graphviz-react';
import { useLocation } from "react-router-dom";
import type { GraphvizOptions } from 'd3-graphviz';

function click_node() {
	var anchors = document.getElementsByClassName('node');
	for(var i = 0; i < anchors.length; i++) {
		var anchor = anchors[i];
		// Adds an onclick function to all course code nodes
		if (anchor.__data__.key.search("\\*") !== -1 && anchor.__data__.key.length > 6){
			anchor.onclick = function() {
				//alert(this.__data__.key);
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

function PreqGraph() {
    var dots = '';
	let location = useLocation();
	let course_code = 'none';
	if (location.state){
		course_code = location.state.substring(1);
		let carleton = location.state.charAt(0) == 'g' ? false : true;
		jQuery.ajax({
		  type: "get",
		  dataType: "json",
		  url: "/api/preqs",
		  data: {
			code: course_code,
			carleton: carleton
		  },
		  success: function (data) {
			  // Gets rid of the junk put in by python
			  dots = data.results.substring(2, data.results.length - 1);
			  dots = dots.replaceAll('\\n', '\n').replaceAll('\\t', '\t').replaceAll('\\"', '"').replaceAll('label="\\\\N",', '');
			  
			  while (document.getElementById('graph') === null);
			  // Renders the Graph when it is ready
			  ReactDOM.render(<Graphviz dot={dots} options={graphOptions}/>, document.getElementById('graph'));
			  click_node();
		  },
		  fail: function (error) {
			alert(error);
		  },
		});
	}

	const { innerWidth, innerHeight } = window;

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

	const [graphOptions, setGraphOptions] = useState(defaults);
	
	return(<div className="App-body"><h2>{course_code}</h2><div id="graph"></div></div>);
}

export default PreqGraph;