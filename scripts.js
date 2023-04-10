document.addEventListener('DOMContentLoaded', function() {
  function getProjectNameFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('project-name');
  }

  function fetchCSV(projectName) {
    const url = `data/${projectName}/${projectName}_clean.csv`;
    return fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Error fetching CSV data from ${url}`);
        }
        return response.text();
      })
      .then(csvData => {
        return new Promise((resolve, reject) => {
          Papa.parse(csvData, {
            header: true,
            complete: results => {
              resolve(results.data);
            },
            error: error => {
              reject(error);
            }
          });
        });
      })
      .catch(error => {
        console.error('Error fetching and parsing CSV data:', error);
      });
  }

  // Click event listener to reset search input when clicking outside the table
  document.addEventListener("click", function(event) {
    const elementTable = document.getElementById("ElementTable");
    const elementTypeTable = document.getElementById("chart-2");
    const elementNameTable = document.getElementById("chart-3");
  
    if (
      !elementTable.contains(event.target) &&
      !elementTypeTable.contains(event.target) &&
      !elementNameTable.contains(event.target)
    ) {
      const searchInput = document.getElementById("searchInput");
      searchInput.value = "";
      
      // Manually dispatch the input event to update the table
      searchInput.dispatchEvent(new Event("input"));
    }
  });
  
  
  

  const projectName = getProjectNameFromUrl();

  if (projectName) {
    fetchCSV(projectName).then(data => {
      // Call the functions to create the charts and tables with the data
      createChart1(data);
      createElementTable(data);
      createChart2(data);
      createChart3(data);

      // Write Project Header
      const projectHeader = document.getElementById("project-header");
      projectHeader.textContent = `IFC Data Overview - ${projectName}`;
    });
  } else {
    console.error('No project name specified in the URL.');
  }
});



// Chart-1: File Summaries
function createChart1(data) {
  const table = document.getElementById('chart-1');
  table.innerHTML = '';

  // Calculate values from the data
  const numberOfElements = data.length;
  const uniqueElementNames = new Set(data.map(item => item['vyzn.source.ElementName'])).size;
  const emptyElementNames = data.filter(item => !item['vyzn.source.ElementName']).length;
  const numberOfColumns = Object.keys(data[0]).length;


  // Create the table header row
  const headerRow = document.createElement('tr');
  const labelHeader = document.createElement('th');
  labelHeader.textContent = 'IFC Data Summary';
  headerRow.appendChild(labelHeader);

  const valueHeader = document.createElement('th');
  valueHeader.textContent = '';
  headerRow.appendChild(valueHeader);
  table.appendChild(headerRow);

  // Add row function
  function addRow(label, value) {
    const tableRow = document.createElement('tr');
    const labelCell = document.createElement('td');
    labelCell.textContent = label;
    tableRow.appendChild(labelCell);

    const valueCell = document.createElement('td');
    valueCell.textContent = value;
    tableRow.appendChild(valueCell);

    table.appendChild(tableRow);
  }

  // Add the calculated values to the table
  addRow('Number of elements in file', numberOfElements);
  addRow('Number of different element names', uniqueElementNames);
  addRow('Number of entries without ElementNames', emptyElementNames, 'emptyElementNames');
  addRow('# of columns', numberOfColumns, 'numberOfColumns');
}
// Chart-2: ElementTypes
function createChart2(data) {
  const table = document.getElementById("chart-2");
  table.innerHTML = "";

  // Group the data by ElementType and calculate the Count and SumArea
  const groupedData = data.reduce((acc, item) => {
    const elementType = item["vyzn.reference.ElementType"];
    const grossArea = parseFloat(item["vyzn.GrossArea"]) || 0;

    if (!acc[elementType]) {
      acc[elementType] = { count: 0, sumArea: 0 };
    }
    acc[elementType].count += 1;
    acc[elementType].sumArea += grossArea;

    return acc;
  }, {});

  // Create the table header row
  const headerRow = document.createElement("tr");
  const elementTypeHeader = document.createElement("th");
  elementTypeHeader.textContent = "ElementType";
  headerRow.appendChild(elementTypeHeader);

  const countHeader = document.createElement("th");
  countHeader.textContent = "Count";
  headerRow.appendChild(countHeader);

  const sumAreaHeader = document.createElement("th");
  sumAreaHeader.textContent = "SumArea";
  headerRow.appendChild(sumAreaHeader);
  table.appendChild(headerRow);

  // Create the table body
  for (const elementType in groupedData) {
    const tableRow = document.createElement("tr");
    const elementTypeCell = document.createElement("td");
    elementTypeCell.textContent = elementType;
    tableRow.appendChild(elementTypeCell);

    const countCell = document.createElement("td");
    countCell.textContent = groupedData[elementType].count;
    tableRow.appendChild(countCell);

    const sumAreaCell = document.createElement("td");
    sumAreaCell.textContent = groupedData[elementType].sumArea.toFixed(2);
    tableRow.appendChild(sumAreaCell);

    table.appendChild(tableRow);

    // Add the click event listener
    tableRow.addEventListener("click", () => {
    document.getElementById("searchInput").value = elementType;
    triggerSearch();
    });
  }
}

// Chart-3: ElementNames
function createChart3(data) {
  const table = document.getElementById("chart-3");
  table.innerHTML = "";

  // Group the data by ElementName and calculate the Count and SumArea
  const groupedData = data.reduce((acc, item) => {
    const elementName = item["vyzn.source.ElementName"];
    const grossArea = parseFloat(item["vyzn.GrossArea"]) || 0;

    if (!acc[elementName]) {
      acc[elementName] = { count: 0, sumArea: 0 };
    }
    acc[elementName].count += 1;
    acc[elementName].sumArea += grossArea;

    return acc;
  }, {});

  // Create the table header row
  const headerRow = document.createElement("tr");
  const elementNameHeader = document.createElement("th");
  elementNameHeader.textContent = "ElementName";
  headerRow.appendChild(elementNameHeader);

  const countHeader = document.createElement("th");
  countHeader.textContent = "Count";
  headerRow.appendChild(countHeader);

  const sumAreaHeader = document.createElement("th");
  sumAreaHeader.textContent = "SumArea";
  headerRow.appendChild(sumAreaHeader);
  table.appendChild(headerRow);

  // Create the table body
  for (const elementName in groupedData) {
    const tableRow = document.createElement("tr");
    const elementNameCell = document.createElement("td");
    elementNameCell.textContent = elementName;
    tableRow.appendChild(elementNameCell);

    const countCell = document.createElement("td");
    countCell.textContent = groupedData[elementName].count;
    tableRow.appendChild(countCell);

    const sumAreaCell = document.createElement("td");
    sumAreaCell.textContent = groupedData[elementName].sumArea.toFixed(2);
    tableRow.appendChild(sumAreaCell);

    table.appendChild(tableRow);

    // Add the click event listener
    tableRow.addEventListener("click", () => {
    document.getElementById("searchInput").value = elementName;
    triggerSearch();
    });
  }
}

function triggerSearch() {
  const searchString = document.getElementById("searchInput").value.toLowerCase();
  const dataRows = document.querySelectorAll("#ElementTable tr");

  dataRows.forEach((row, index) => {
    if (index === 0) return; // Skip the header row
    const rowText = row.textContent.toLowerCase();
    if (rowText.includes(searchString)) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });
}


// Element Table
function createElementTable(data) {
  const table = document.getElementById('ElementTable');
  table.innerHTML = '';

  // Create the table header row
  const headerRow = document.createElement('tr');
  const guidHeader = document.createElement('th');
  guidHeader.textContent = 'GUID';
  headerRow.appendChild(guidHeader);

  const elementTypeHeader = document.createElement('th');
  elementTypeHeader.textContent = 'ElementType';
  headerRow.appendChild(elementTypeHeader);

  const elementNameHeader = document.createElement('th');
  elementNameHeader.textContent = 'ElementName';
  headerRow.appendChild(elementNameHeader);

  const levelHeader = document.createElement('th');
  levelHeader.textContent = 'Level';
  headerRow.appendChild(levelHeader);

  const grossAreaHeader = document.createElement('th');
  grossAreaHeader.textContent = 'GrossArea';
  headerRow.appendChild(grossAreaHeader);
  table.appendChild(headerRow);

  // Create the table body
  data.forEach(row => {
    const tableRow = document.createElement('tr');
    const guidCell = document.createElement('td');
    guidCell.textContent = row['vyzn.source.GUID'];
    tableRow.appendChild(guidCell);

    const elementTypeCell = document.createElement('td');
    elementTypeCell.textContent = row['vyzn.reference.ElementType'];
    tableRow.appendChild(elementTypeCell);

    const elementNameCell = document.createElement('td');
    elementNameCell.textContent = row['vyzn.source.ElementName'];
    tableRow.appendChild(elementNameCell);

    const levelCell = document.createElement('td');
    levelCell.textContent = row['vyzn.source.floor'];
    tableRow.appendChild(levelCell);

    const grossAreaCell = document.createElement('td');
    grossAreaCell.textContent = row['vyzn.GrossArea'];
    tableRow.appendChild(grossAreaCell);

    table.appendChild(tableRow);
  });
  

  // Add the search functionality
  document.getElementById('searchInput').addEventListener('input', function() {
    const searchString = this.value.toLowerCase();
    const dataRows = document.querySelectorAll('#ElementTable tr');

    dataRows.forEach((row, index) => {
      if (index === 0) return; // Skip the header row
      const rowText = row.textContent.toLowerCase();
      if (rowText.includes(searchString)) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  });
}

