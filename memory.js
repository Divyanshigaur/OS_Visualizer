//memory.js
function showAlgo(id) {
            document.querySelectorAll('.algo-section').forEach(section => {
                section.classList.remove('active');
            });

            document.querySelectorAll('.tab-button').forEach(button => {
                button.classList.remove('active');
            });

            document.getElementById(id).classList.add('active');
            event.target.classList.add('active');
        }

async function runAlgorithm(algorithm, frames, referenceString) {
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/${algorithm}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        frames: parseInt(frames),
        reference_string: referenceString.split(",").map(Number),
      }),
    });

    const result = await response.json(); // 🟡 This crashes if response is empty
    console.log(result);
    displayResult(result); // Your logic here
  } catch (error) {
    console.error("Error:", error);
    alert("Something went wrong. Check if Flask is running.");
  }
}


// Individual functions calling the common function
function runFIFO() {
  const frames = document.getElementById('fifo-frames').value;
  const reference = document.getElementById('fifo-reference').value;
  runAlgorithm('fifo', frames, reference);
}
///may remove 
function displayResult(result) {
  const activeSection = document.querySelector('.algo-section.active');
  const outputDiv = activeSection.querySelector('div[id$="-output"]');

  outputDiv.innerHTML = `
    <h3>Results:</h3>
    <p><strong>Page Faults:</strong> ${result.page_faults}</p>
    <h4>Frame States:</h4>
    <pre>${result.frame_states.map(state => JSON.stringify(state)).join('\n')}</pre>
  `;
}


function runLRU() {
  runAlgorithm('lru');
}

function runOptimal() {
  runAlgorithm('optimal');
}
