
const form = document.getElementById("summarization-form");

// Form submission
form.addEventListener("submit", async (e) => {

    e.preventDefault();

    const dialogueInput = document.getElementById("dialogue-input");
    const summaryText = document.getElementById("summaryContent");
    const submitButton = form.querySelector("button");

    const dialogue = dialogueInput.value.trim();

    if (!dialogue) return;

    // Show loading state
    summaryText.innerText = "Processing...";

    submitButton.disabled = true;

    // Display result section
    document.getElementById("resultSection").classList.add("show");

    try {

        const response = await fetch("/summarize/", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({ dialogue }),

        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        summaryText.innerText = data.summary || "No summary returned.";

    } catch (err) {

        summaryText.innerText = `Error: ${err.message}`;

    } finally {

        submitButton.disabled = false;

    }

});


// Copy Summary
document.getElementById("copyBtn").addEventListener("click", async () => {

    const summary = document.getElementById("summaryContent").innerText;

    const copyBtn = document.getElementById("copyBtn");

    try {

        await navigator.clipboard.writeText(summary);

        copyBtn.innerText = "Copied!";

        setTimeout(() => {
            copyBtn.innerText = "Copy";
        }, 2000);

    } catch (err) {

        copyBtn.innerText = "Copy failed";

    }

});


// Word Counter
document.getElementById("dialogue-input").addEventListener("input", (e) => {

    const text = e.target.value.trim();

    const words = text ? text.split(/\s+/).length : 0;

    document.getElementById("wordCount").innerText = `${words} words`;

});
