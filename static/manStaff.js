"use strict"

function showAddModal() {
    // Set the Modal Title appropriately
    document.getElementById("modalTitle").innerHTML = "Add a New Staff Member";

    // Hide the delete and save changes buttons
    document.getElementById("delBut").style.display = "none";
    document.getElementById("savBut").style.display = "none";

    // Show the add button
    document.getElementById("addBut").style.display = "block";

    // Reset Form
    document.getElementById("addStafferForm").reset();

    // Display the modal
    $('#addStafferModal').modal('toggle');

}

function showEditModal(id) {
    // Set the Modal Title appropriately
    document.getElementById("modalTitle").innerHTML = "Edit Staff Member Info";

    // Show the delete and save changes buttons
    document.getElementById("delBut").style.display = "block";
    document.getElementById("delBut").onclick = () => { delStaff(id) };
    document.getElementById("savBut").style.display = "block";

    // Hide the add button
    document.getElementById("addBut").style.display = "none";

    // Set the values of the form.
    let tr = document.getElementById(id);

    document.getElementById("raID").value = tr.getElementsByClassName("raID")[0].innerHTML;
    document.getElementById("fName").value = tr.getElementsByClassName("fName")[0].innerHTML;
    document.getElementById("lName").value = tr.getElementsByClassName("lName")[0].innerHTML;
    document.getElementById("email").value = tr.getElementsByClassName("email")[0].innerHTML;
    document.getElementById("color").value = tr.getElementsByClassName("color")[0].childNodes[0].value;
    document.getElementById("startDate").value = tr.getElementsByClassName("startDate")[0].innerHTML;
    let authLevelTxt = tr.getElementsByClassName("authLevel")[0].innerHTML;
    let authLevelVal;
    switch (authLevelTxt) {
        case 'AHD':
            authLevelVal = 2;
            break;
        case 'HD':
            authLevelVal = 3;
            break;
        case 'RA':
            authLevelVal = 1;
    }
    document.getElementById("authLevelOpts").value = authLevelVal;

    // Display the modal
    $('#addStafferModal').modal('toggle');
}

function submitChanges(id) {

    let data = {
        raID : document.getElementById("raID").value,
        fName : document.getElementById("fName").value,
        lName : document.getElementById("lName").value,
        email : document.getElementById("email").value,
        color : document.getElementById("color").value,
        startDate : document.getElementById("startDate").value,
        authLevel : document.getElementById("authLevelOpts").value
    }

    appConfig.base.callAPI("changeStaffInfo",data,getStaffInfo,"POST");
}

function getStaffInfo() {
    console.log("Refreshing Staff List");

    appConfig.base.callAPI("getStaffInfo",{},
                             (data) => {
                                reDrawTable(data);
                                $('#addStafferModal').modal('toggle');
                             },"GET");
}

function reDrawTable(data) {
    // data = {
    //    raList: [(id,fName,lName,email,dateStarted,resHallName,color,auth_level), ...],
    //    pts: { raID : { name: xxx, pts: xx }, ... }
    // }

    console.log("Redrawing Staff Table");

    let table = document.getElementById("staffTable");
    let oldTBody = table.getElementsByTagName("tbody")[0];

    let newTBody = document.createElement("tbody");

    for (let staffer of data.raList) {

        // Add the points into the list in the expected location
        staffer.splice(6, 0, data.pts[staffer[0]].pts)
        addRow(staffer, newTBody);
    }

    table.replaceChild(newTBody, oldTBody);
}

function addRow(data, table) {
    let newRow = table.insertRow(0);
    newRow.id = data[0];
    newRow.setAttribute("scope","row");

    let col;
    let i = 0;
    for (let d of ["raID","fName","lName","email","startDate","resHall","points","color","authLevel"]) {
        col = newRow.insertCell(i);
        col.className = d;

        if (d == "startDate") {
            let tmp = new Date(data[i]);
            col.innerHTML = tmp.toISOString().substring(0,10);

        } else if (d == "color") {
            let tmp = document.createElement("input");
            tmp.type = "color";
            tmp.value = data[i];
            tmp.disabled = true;
            col.appendChild(tmp);

        } else if (d == "authLevel") {
            switch (data[i]) {
                case 1:
                    col.innerHTML = "RA";
                    break;

                case 2:
                    col.innerHTML = "AHD";
                    break;
                case 3:
                    col.innerHTML = "HD";
                    break;

                default:
                    col.innerHTML = "HD";
                    break;
            }

        } else {
            col.innerHTML = data[i];

        }
        i++;
    }

    let edit = newRow.insertCell(i);
    let editSpan = document.createElement("span");

    editSpan.className = "fa fa-pencil";
    editSpan.setAttribute("onclick","showEditModal("+data[0].toString()+")");
    edit.appendChild(editSpan);

}

function delStaff(id) {

    // Hide the modal
    $('#addStafferModal').modal('toggle');

    appConfig.base.callAPI("removeStaffer",id,function(i) {
        let row = document.getElementById(i);
        row.parentNode.removeChild(row);
    },"POST");
}

function addStaff() {

    let data = {
        raID : document.getElementById("raID").value,
        fName : document.getElementById("fName").value,
        lName : document.getElementById("lName").value,
        email : document.getElementById("email").value,
        color : document.getElementById("color").value,
        startDate : document.getElementById("startDate").value,
        authLevel : document.getElementById("authLevelOpts").value
    }

    appConfig.base.callAPI("addStaffer",data,getStaffInfo,"POST");
}

function showImportModal() {
    // Display the modal
    $('#importStaffModal').modal('toggle');
}

function importStaff() {
    console.log("Importing Staff From .csv");

    // Disable the import button
    document.getElementById("importBut").disabled = true;

    // Submit the form
    document.getElementById("importStaffForm").submit();
}
