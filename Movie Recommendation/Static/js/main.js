// main.js

// Wait until the DOM is fully loaded before executing the JavaScript
document.addEventListener("DOMContentLoaded", function() {
    // Get the input element by its name attribute
    const searchInput = document.querySelector("input[name='prompt']");
    
    // Check if the element exists before adding event listener
    if (searchInput) {
        // Add an event listener to handle input events
        searchInput.addEventListener('input', function() {
            // Get the value of the input and call searchMovie function
            const prompt = searchInput.value.trim();
            searchMovie();
        });
    }
});

// Define the searchMovie function
function searchMovie() {
    const prompt = document.getElementById('movieSearch').value;  // Get the prompt value
    console.log("Searching for movies related to:", prompt);  // Log the actual prompt value
    if (prompt) {
      // Fetch the movie results from the backend
      fetch(`/result/?prompt=${encodeURIComponent(prompt)}`)
        .then(response => response.text())
        .then(html => {
          // Process the HTML response and display it
          document.getElementById("recommendation").innerHTML = html;
        })
        .catch(error => console.error("Error fetching search results:", error));
    } else {
      alert("Please enter a prompt.");
    }
  }
  
