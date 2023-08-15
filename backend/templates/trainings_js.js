
const analyzeButton = document.getElementById("analyze-button");
const fileInput = document.getElementById("file-input");
const resultContainer = document.getElementById("result-container");

analyzeButton.addEventListener("click", async () => {
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/analyze/", {
        method: "POST",
        body: formData,
    });

    if (response.ok) {
        const results = await response.json();
        displayResults(results);
    }
});

function displayResults(results) {
    resultContainer.innerHTML = "";
    for (const record of results) {
        const recordDiv = document.createElement("div");
        recordDiv.classList.add("record-box");
        recordDiv.innerHTML = `
            <p>ID: ${record.id}</p>
            <p>Date: ${record.date}</p>
            <p>Bend: ${record.bend}</p>
            <p>Circular Raise: ${record.circular_raise}</p>
            <p>Abduction: ${record.abduction}</p>
            <p>Rear Touch: ${record.rear_touch}</p>
            <p>Side Bend: ${record.side_bend}</p>
            <p>Duration: ${record.duration}</p>
        `;
        resultContainer.appendChild(recordDiv);
    }
}
