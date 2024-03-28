function search(page, perPage) {
  var query = document.getElementById("searchInput").value;

  // Construct the URL with query parameters
  var url = `/search?query=${encodeURIComponent(
    query
  )}&page=${page}&per_page=${perPage}`;

  // Send AJAX request to Flask backend
  fetch(url)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      displayResults(data);
      updatePaginationControls(data);
    })
    .catch((error) => console.error("Error:", error));
}

function updatePaginationControls(data) {
  document.getElementById("pageNumberInput").value = data.page;
  document.getElementById("perPageSelect").value = data.per_page;

  document.getElementById("previousButton").disabled = data.page === 1;
  document.getElementById("nextButton").disabled =
    data.page === data.total_pages;
}

// Rest of your pagination functions...

function displayResults(data) {
  var table = document.getElementById("resultsTable");
  table.innerHTML = ""; // Clear previous results

  // Create table header
  var headerRow = table.insertRow();
  for (var key in data.results[0]) {
    var headerCell = headerRow.insertCell();
    headerCell.textContent = key;
  }

  // Create table rows
  data.results.forEach(function (item) {
    var row = table.insertRow();
    for (var key in item) {
      var cell = row.insertCell();
      cell.textContent = item[key];
    }
  });

  // Display pagination controls
  // Example: Previous Page button, Next Page button, Page number input, Rows per page select
  // You can implement pagination controls based on the pagination information received in the data object
}

// Pagination variables
var currentPage = 1;
var perPage = 10; // Default number of rows per page

// Function to fetch search results for the next page
function nextPage() {
  currentPage++;
  search(currentPage, perPage);
}

// Function to fetch search results for the previous page
function previousPage() {
  if (currentPage > 1) {
    currentPage--;
    search(currentPage, perPage);
  }
}

// Function to fetch search results for a specific page
function goToPage() {
  var pageNumber = parseInt(document.getElementById("pageNumberInput").value);
  if (pageNumber >= 1) {
    currentPage = pageNumber;
    search(currentPage, perPage);
  }
}

// Function to change the number of rows per page
function changePerPage() {
  perPage = parseInt(document.getElementById("perPageSelect").value);
  currentPage = 1; // Reset to first page when changing rows per page
  search(currentPage, perPage);
}
