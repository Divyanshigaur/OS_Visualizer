//cpu.js
        function showAlgo(id) {
            // Hide all sections
            document.querySelectorAll('.algo-section').forEach(section => {
                section.classList.remove('active');
            });

            // Deactivate all buttons
            document.querySelectorAll('.tab-button').forEach(button => {
                button.classList.remove('active');
            });

            // Activate clicked section and button
            document.getElementById(id).classList.add('active');
            event.target.classList.add('active');
        }
        function addRow(tbodyId) {
            const tbody = document.getElementById(tbodyId);

            // Create a neaw row
            const tr = document.createElement('tr');

            // Process ID cell (will set text after adding)
            const tdProcess = document.createElement('td');
            tr.appendChild(tdProcess);

            // Arrival Time input cell
            const tdArrival = document.createElement('td');
            const arrivalInput = document.createElement('input');
            arrivalInput.type = 'number';
            arrivalInput.value = '0';
            arrivalInput.min = '0';
            tdArrival.appendChild(arrivalInput);
            tr.appendChild(tdArrival);

            // Burst Time input cell
            const tdBurst = document.createElement('td');
            const burstInput = document.createElement('input');
            burstInput.type = 'number';
            burstInput.value = '1';
            burstInput.min = '1';
            tdBurst.appendChild(burstInput);
            tr.appendChild(tdBurst);

            // For Priority Scheduling, add Priority input too
            if (tbodyId === 'priority-tbody') {
                const tdPriority = document.createElement('td');
                const priorityInput = document.createElement('input');
                priorityInput.type = 'number';
                priorityInput.value = '1';
                priorityInput.min = '1';
                tdPriority.appendChild(priorityInput);
                tr.appendChild(tdPriority);
            }

            // Action cell with delete button
            const tdAction = document.createElement('td');
            const delButton = document.createElement('button');
            delButton.textContent = '❌';
            delButton.onclick = function() { deleteRow(this, tbodyId); };
            tdAction.appendChild(delButton);
            tr.appendChild(tdAction);

    tbody.appendChild(tr);

    renumberProcesses(tbodyId);
}

function deleteRow(button, tbodyId) {
    const row = button.parentNode.parentNode;
    row.remove();
    renumberProcesses(tbodyId);
}

function renumberProcesses(tbodyId) {
    const tbody = document.getElementById(tbodyId);
    const rows = tbody.rows;

    for (let i = 0; i < rows.length; i++) {
        rows[i].cells[0].textContent = 'P' + (i + 1);
    }
}
///new add  to collect data  Collect user input from CPU scheduling tables (cpu.js)
function collectCpuData(tbodyId) {
    const tbody = document.getElementById(tbodyId);
    const rows = tbody.querySelectorAll("tr");

    const data = [];

    rows.forEach(row => {
        const cells = row.querySelectorAll("td");
        const process = cells[0].textContent;
        const arrivalTime = parseInt(cells[1].querySelector("input").value);
        const burstTime = parseInt(cells[2].querySelector("input").value);

        if (tbodyId === 'priority-tbody') {
            const priority = parseInt(cells[3].querySelector("input").value);
            data.push({ process, arrivalTime, burstTime, priority });
        } else {
            data.push({ process, arrivalTime, burstTime });
        }
    });

    return data;
}


//✅ Step 2: Send the collected data to Flask backend from cpu.js

function runCpuAlgorithm(algorithm, tbodyId) {
    
    const processData = collectCpuData(tbodyId);
    // If Round Robin, include quantum
    let quantum = null;
    if (algorithm === 'rr') {
        const quantumInput = document.getElementById("quantum");
    if (!quantumInput) {
        alert("Please provide a Quantum input field with id='quantum'");
        return;
    }
    quantum = parseInt(quantumInput.value);
}
    // Send the data to backend using a function from api.js
    sendCpuDataToBackend(algorithm, processData,quantum)
        .then(result => {
                    console.log("Backend Result:", result);
                    const avgTatElem = document.getElementById(`avg-tat-${algorithm}`);
                    const avgWtElem = document.getElementById(`avg-wt-${algorithm}`);


        if (avgTatElem && avgWtElem) {
           avgTatElem.textContent = `Average TAT: ${result.average_tat.toFixed(2)}`;
            avgWtElem.textContent = `Average WT: ${result.average_wt.toFixed(2)}`;

        } else {
            console.warn(`Missing average display elements for ${algorithm}`);
        }

            // You can call a function here to visualize the result
            // displayCpuResult(result);
            
        })
        
        .catch(error => {
            console.error("Error:", error);
            alert("Failed to fetch CPU scheduling result. Is Flask running?");
        });
}