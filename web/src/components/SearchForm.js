import "./App.css";
import { useEffect, useState } from "react";
import { PreqGraph } from "./";
import jQuery from "jquery";
import ReactDOM from "react-dom";
import { useNavigate } from "react-router-dom";
import { ListGroup } from "react-bootstrap";

function SearchForm() {
  const userSelectedList = [];
  const [inputs, setInputs] = useState({});
  const [scrollButton, showScrollButton] = useState(false);

  function addToList (value) {
    userSelectedList.push(value);
    updateList();
  }

  function removeFromList (value) {
    const foundIndex = userSelectedList.indexOf(value);
    userSelectedList.splice(foundIndex, 1);
    updateList();
  }

  function UserListItem (props) {
    return (
      <ListGroup.Item>
        <button className='listBtns'>{props.code}</button>
      </ListGroup.Item>
    );
  }

  function updateList () {
    const updatedUserList = (
      <ListGroup>
        {
          userSelectedList.map ( (entry) => (
            <UserListItem
              code={entry}
            />
          ))
        }
      </ListGroup>
    );
    ReactDOM.render(updatedUserList, document.getElementById("userlist"));
  }

  useEffect (() => {
    window.addEventListener("scroll",() => {
      if (window.pageYOffset > 350) {
        showScrollButton(true);
      }
      else {
        showScrollButton(false);
      }
    });
  },[]);

  const autoScroll = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  const handleChange = (event) => {
    const name = event.target.name;
    const value = event.target.value;
    setInputs((values) => ({ ...values, [name]: value }));
  };
  const handleUpdate = (event) => {
    handleChange(event);
    handleSubmit(event, false);
  };
  let navigate = useNavigate();
  
  function Output(props) {
	 // Formats the output only having rows if they are needed
    var joined = props.offerings.join(", ");
    var offerings = null;
    if (props.offerings.join(", ") !== "No Data") {
      offerings = [<b>Offering(s): </b>, joined, <br />];
    }
    var prereq = null;
    if (props.prereq !== "No Data") {
	prereq = [<b>Prerequisite(s): </b>, props.prereq, <br />, <button type="button" onClick={() => { navigate('/preqgraph', { state: jQuery("#App-form-input-university :selected").text().toLowerCase() == 'guelph' ? 'g' + props.code : 'c' + props.code }); }}>Graph</button>, <br />];
    }

    var restrictions = null;
    if (props.restrictions !== "No Data") {
      restrictions = [<b>Restriction(s): </b>, props.restrictions, <br />];
    }
    var equivalent = null;
    if (props.equivalent !== "No Data") {
      equivalent = [<b>Equate(s): </b>, props.equivalent, <br />];
    }
    return (
      <ListGroup.Item>
        <b>
          {props.code} {props.name} {props.term.join(", ")} [
          {props.creditWeight}]
        </b>
        <br />
        {props.description} <br />
        {offerings}
        {prereq}
        {restrictions}
        {equivalent}
        <b>Department(s): </b>
        {props.department}
        <br />
        <b>Location(s): </b>
        {props.location}
        <br />
        <label>
          <b>Add {props.code} to List:&nbsp;</b>
          <input type = "checkbox" className = 'searchedList' id = {props.code} value = {props.code}
          />
        </label>
      </ListGroup.Item>
    );
  }

  const handleSubmit = (event, prevent = true) => {
    if (prevent) {
      event.preventDefault();
    }

    if (inputs.subjects === undefined || inputs.subjects === "") {
      var subjects = "";
    } else {
      var subjects = inputs.subjects;
    }

    var terms = "";
    if (jQuery("#App-form-input-terms-f").is(":checked")) {
      terms = terms + "F";
    }
    if (jQuery("#App-form-input-terms-w").is(":checked")) {
      terms = terms + (terms === "" ? "W" : " W");
    }
    if (jQuery("#App-form-input-terms-s").is(":checked")) {
      terms = terms + (terms === "" ? "S" : " S");
    }
    if (terms === "") {
      terms = "F W S";
    }

    var prereqs = jQuery("#App-form-input-prereqs :selected")
      .text()
      .toLowerCase();

    var university = jQuery("#App-form-input-university :selected")
      .text()
      .toLowerCase();

    if (inputs.levels === undefined || inputs.levels === "") {
      if (university === "carleton") {
        var levels = "0 - 4000";
      } else {
	      var levels = "1000 - 5000";
      }
    } else {
      var levels = inputs.levels;
    }

    if (inputs.credits === undefined || inputs.credits === "") {
      var credits = "0.0 - 6.5";
    } else {
      var credits = inputs.credits;
    }

    jQuery.ajax({
      type: "get",
      dataType: "json",
      url: "/api/search",
      data: {
        university: university,
        subjects: subjects,
        terms: terms,
        prereqs: prereqs,
        levels: levels,
        credits: credits,
      },
      success: function (data) {
        let keys = Object.keys(data);
        if (keys[0] === 'error') {
          alert(data["error"]);
          return;
        }
	if (data['results'] === '[]') {
	  alert("No results found with that query!");
	}
        var dataList = JSON.parse(data["results"]).sort(function compareFn(
          a,
          b
        ) {
          if (a["code"] > b["code"]) {
            return 1;
          }
          return -1;
        });
		
		// Creates a list formatted output
        const listObj = (
          <ListGroup className="App-list-group">
            {" "}
            {dataList.map((part) => (
              <Output
                code={part["code"]}
                name={part["name"]}
                term={part["term"]}
                creditWeight={part["creditWeight"]}
                description={part["description"]}
                offerings={part["offerings"]}
                department={part["department"]}
                location={part["location"]}
                restrictions={part["restrictions"]}
                prereq={part["prereq"]}
                equivalent={part["equivalent"]}
              />
            ))}{" "}
          </ListGroup>
        );
        ReactDOM.render(listObj, document.getElementById("output"));

        let checkboxes = document.querySelectorAll ('.searchedList');
        checkboxes.forEach (function (checkbox) {
          checkbox.addEventListener('change', function (){
            if (checkbox.checked == true){
              addToList (checkbox.value);
            }
            else {
              removeFromList(checkbox.value);
            }
          })
        });

      },
      fail: function (error) {
        alert(error);
      },
    });
  };

//testList = document.getElementById ('output').querySelectorAll('.list-group-item');
  return (
    <div className="App-body">
      <div className="App">
        {scrollButton && (
          <button onClick={autoScroll} className="auto-scroll-button">
            &#8679;
          </button>
        )}
        <form id="App-search-form" onSubmit={handleSubmit}>
          <h2>Search for Guelph Courses</h2>

          <p className="App-form-row">
            <p className="App-form-labels">Guelph or Carleton</p>
            <select
              className="App-form-input"
              id="App-form-input-university"
              onChange={handleUpdate}
            >
              <option value="Yes">Guelph</option>
              <option value="No">Carleton</option>
            </select>
          </p>

          <p className="App-form-row">
            <p className="App-form-labels">Course Subject(s)</p>
            <input
              className="App-form-input"
              id="App-form-input-subjects"
              type="text"
              name="subjects"
              value={inputs.subjects || ""}
              onChange={handleChange}
              placeholder="Enter Course Subject(s)"
            />
            <input
              id="subjectsyntax"
              name="subjectsyntax"
              type="text"
              value="Examples: 'CIS' or 'CIS BIOL'"
            />
          </p>
          <p className="App-form-row">
            <p className="App-form-labels">Term(s)</p>

            <div className="App-checkbox-group" onChange={handleUpdate}>
              <span className="App-checkbox">
                <input
                  id="App-form-input-terms-f"
                  type="checkbox"
                  name="checkbox-f"
                />
                <label for="checkbox-f">F</label>
              </span>

              <span className="App-checkbox">
                <input
                  id="App-form-input-terms-w"
                  type="checkbox"
                  name="checkbox-w"
                />
                <label for="checkbox-w">W</label>
              </span>

              <span className="App-checkbox">
                <input
                  id="App-form-input-terms-s"
                  type="checkbox"
                  name="checkbox-s"
                />
                <label for="checkbox-s">S</label>
              </span>
            </div>
          </p>

          <p className="App-form-row">
            <p className="App-form-labels">Can Have Prereqs</p>
            <select
              className="App-form-input"
              id="App-form-input-prereqs"
              onChange={handleUpdate}
            >
              <option value="Yes">Yes</option>
              <option value="No">No</option>
            </select>
          </p>

          <p className="App-form-row">
            <p className="App-form-labels">Level(s)</p>
            <input
              className="App-form-input"
              id="App-form-input-levels"
              type="text"
              name="levels"ls
              value={inputs.levels || ""}
              onChange={handleChange}
              placeholder="Enter Levels(s)"
            />
            <input
              id="levelsyntax"
              name="levelsyntax"
              type="text"
              value="Examples: '1000' or '1000 - 3000' or '1000 2000 4000'"
            />
          </p>

          <p className="App-form-row">
            <p className="App-form-labels">Credit(s)</p>
            <input
              className="App-form-input"
              id="App-form-input-credits"
              type="text"
              name="credits"
              value={inputs.credits || ""}
              onChange={handleChange}
              placeholder="Enter Credit(s)"
            />
            <input
              id="creditsyntax"
              name="creditsyntax"
              type="text"
              value="Examples: '0.5' or '0.5 0.75' or '0.5 - 0.75'"
            />
          </p>

          <button
            className="App-button"
            id="Submit-search-button"
            type="button"
			onClick={handleSubmit}
			>Submit Query</button>
        </form>
      </div>
      <div>
        <ul id="userlist"></ul>
      </div>
      <div>
        <ul id="output"></ul>
      </div>

      {scrollButton && (
        <button onClick={autoScroll} className="auto-scroll-button">
          &#8679;
        </button>
      )}

    </div>
  );
}

export default SearchForm;

