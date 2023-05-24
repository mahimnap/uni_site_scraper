import './App.css'
import jQuery from "jquery";
import ReactDOM from "react-dom";
import React, { useState } from 'react';
import { Graphviz } from 'graphviz-react';
import { useLocation } from "react-router-dom";
import type { GraphvizOptions } from 'd3-graphviz';
import Select from 'react-select';

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
          url: "/api/carletonmoreinfo",
          data: {
            code: this.__data__.key,
          },
          success: function (data) {
            let values = data['results']
            alert("Course Code: " + values['code'] + "\nYear Standing: " + values['year_standing']); 
          },
          fail: function (error) {
            alert(error);
          },
        });

			}
		}
	}
}
	
function CarletonSubjectGraph() {
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
	const [graphOptions, setGraphOptions] = useState(defaults);

	const subjectList = [] 

	jQuery.ajax({
		type: "get",
		dataType: "json",
		url: "/api/carletonsubjectlist",
		data: {},
		success: function (data) {
			let subjects = data['results']; 
			for (let i = 0; i < subjects.length; i++){
				subjectList.push(subjects[i]);
			}
		},
		fail: function (error) {
			alert(error);
		},
	});

	const handler = (event) => {
		const value = event.value
		setSelectValue(value)
  
		var dots = '';
		jQuery.ajax({
			type: "get",
			dataType: "json",
			url: "/api/carlpreqs",
			data: {
				code: value,
				carleton: 'false'
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
	
	return(
	<div className="App-body">
		<form style={{width: '250px'}}>
			<Select 
				className = "App-select" 
					onChange={handler}
					options = {subjectList}
			/>
		</form>
		<div id="graph"></div>
	</div>
	);
}

export default CarletonSubjectGraph;