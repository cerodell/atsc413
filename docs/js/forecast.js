
// ########################## SIDE BAR ##########################
const sidebar = document.querySelector(".sidebar");
const sidebarClose = document.querySelector("#sidebar-close");
const menu = document.querySelector(".menu-content");
const menuItems = document.querySelectorAll(".submenu-item");
const subMenuTitles = document.querySelectorAll(".submenu .menu-title");

sidebarClose.addEventListener("click", () => sidebar.classList.toggle("close"));

menuItems.forEach((item, index) => {
  item.addEventListener("click", () => {
    menu.classList.add("submenu-active");
    item.classList.add("show-submenu");
    menuItems.forEach((item2, index2) => {
      if (index !== index2) {
        item2.classList.remove("show-submenu");
      }
    });
  });
});

subMenuTitles.forEach((title) => {
  title.addEventListener("click", () => {
    menu.classList.remove("submenu-active");
  });
});

// ####################### END SIDE BAR ##########################


// ####################### MENU ##########################
// Menu is defined by the div to the right tof the side bar,
//  its where the images and button are located

// Get the menu item links
var menuItems_c = document.querySelectorAll('.menu-items a');

// Add click event listeners to the menu item links
menuItems_c.forEach(function(menuItem) {
  menuItem.addEventListener('click', function(event) {
    // Prevent the default link behavior
    event.preventDefault();

    // Store the selected menu item's href in localStorage
    localStorage.setItem('selectedMenuItem', menuItem.getAttribute('href'));
  });
});

// Check if a menu item selection is cached in localStorage
var selectedMenuItem = localStorage.getItem('selectedMenuItem');
if (selectedMenuItem !== null) {
  // Find the menu item link with the cached href and trigger a click event
  var selectedMenuItemLink = document.querySelector('.menu-items a[href="' + selectedMenuItem + '"]');
  if (selectedMenuItemLink) {
    selectedMenuItemLink.click();
  }
}
// #################### END MENU ##########################


// #################### DATETIME ##########################

// Compare if a date is in the past
function isDateInPast(dateToCheck, referenceDate) {
  return dateToCheck.getTime() < referenceDate.getTime();
}


function parseDateTime(dateTimeString) {
  // Extract year, month, day, and hour from the string
  var year = parseInt(dateTimeString.substr(0, 4));

  var month = parseInt(dateTimeString.substr(4, 2));

  var day = parseInt(dateTimeString.substr(6, 2));

  var hour = parseInt(dateTimeString.substr(9, 2));

  // Create a new Date object using the extracted values
  var date = new Date(year, month - 1, day, hour);
  // console.log('date '  + date)

  return date;
}

function formatDate(date) {
  var year = date.getFullYear().toString();
  var month = (date.getMonth() + 1).toString().padStart(2, '0');
  var day = date.getDate().toString().padStart(2, '0');
  var hour = date.getHours().toString().padStart(2, '0');
  return year + month + day + 'Z' + hour;
}
// #################### END DATETIME ########################



// ####################### IMAGES ##########################
// This is for displaying and looping through images

// Retrieve the cached variable
var loc = localStorage.getItem("loc");
var int = localStorage.getItem("int");
var valid = localStorage.getItem("valid");
var varname = localStorage.getItem("varname");

// Log the cached variables
console.log("loc:", loc);
console.log("int:", int);
console.log("valid:", valid);
console.log("varname:", varname);
showImage(loc, int, valid, varname);


function toggleDropdown() {
  const dropdownContainer = document.getElementById('dropdownContainer');
  dropdownContainer.classList.toggle('open');
}

var currentIndex = 0; // Initialize the current index of the date range
const buttons = document.querySelectorAll('.dropdown-option');
buttons.forEach(function(button) {
  button.addEventListener('click', function() {
    const dataI = button.getAttribute('i');
    const dataJ = button.getAttribute('j');
    localStorage.setItem("dataI", dataI);
    localStorage.setItem("dataJ", dataJ);

    console.log("dataI  "  +dataI);
    console.log("dataJ  "  +dataJ);
  });
});

function showImage(loc, int, valid, varname) {
  var dataI = localStorage.getItem("dataI");
  var dataJ = localStorage.getItem("dataJ");
  if (isDateInPast(parseDateTime(valid), parseDateTime(dataI))) {
    var valid = dataI
    localStorage.setItem("valid", valid);
    console.log("valid  less than dataI" );
  } else if (isDateInPast(parseDateTime(dataJ), parseDateTime(valid))) {
    var valid = dataJ
    localStorage.setItem("valid", valid);
    console.log("dataJ  less than valid" );
  }else{
    }
  if (loc === localStorage.getItem("loc", loc)) {
    console.log("Same location");
  } else {
    var valid = int
    localStorage.setItem("valid", valid);
    console.log("New location");
  }
  imageUrl = `../img/${loc}/gfs/${int}/${varname}-${valid.split('Z').join("")}.jpeg`
  $.get(imageUrl)
    .done(function() {
      localStorage.setItem("loc", loc);
      localStorage.setItem("int", int);
      localStorage.setItem("valid", valid);
      localStorage.setItem("varname", varname);
      console.log(imageUrl);
      const currentImage = document.getElementById('currentImage');
      currentImage.src = imageUrl;
    }).fail(function() {
      if (isDateInPast(parseDateTime(valid), parseDateTime(int))) {
        var valid = int
        localStorage.setItem("valid", valid);
      }else{
      }
      var loc = localStorage.getItem("loc");
      var varname = localStorage.getItem("varname");
      imageUrl = `../img/${loc}/gfs/${int}/${varname}-${valid.split('Z').join("")}.jpeg`
      console.log(imageUrl);
      const currentImage = document.getElementById('currentImage');
      currentImage.src = imageUrl;
    })

}

// #################### END IMAGES ##########################



// ####################### NAVIGATION #######################



// Event listener for keyboard arrow keys
document.addEventListener('keydown', function(event) {
  var loc = localStorage.getItem("loc");
  var int = localStorage.getItem("int");
  var valid = localStorage.getItem("valid");
  var varname = localStorage.getItem("varname");

  // Check if the event target is an input element to prevent conflicts with text input fields
  if (event.target.tagName !== "INPUT") {
    if (event.code === 'ArrowLeft') {
      // Decrement the int date-time by one hour
      var prevDateTime = decrementDateTime(valid);
      showImage(loc, int, prevDateTime, varname);
    } else if (event.code === 'ArrowRight') {
      // Increment the int date-time by one hour
      var nextDateTime = incrementDateTime(valid);
      showImage(loc, int, nextDateTime, varname);
    }
  }
});

// Function to increment the int date-time by one hour
function incrementDateTime(dateTime) {
  var date = parseDateTime(dateTime);
  date.setHours(date.getHours() + 3); // Increment by one hour
  return formatDate(date);
}

// Function to decrement the int date-time by one hour
function decrementDateTime(dateTime) {
  var date = parseDateTime(dateTime);
  date.setHours(date.getHours() - 3); // Decrement by one hour
  return formatDate(date);
}












// // Function to handle the next image
// function nextImage() {
//   var loc = localStorage.getItem("loc");
//   var int = localStorage.getItem("int");
//   var varname = localStorage.getItem("varname");
//   showImage(loc, int, varname);
// }

// // Function to handle the previous image
// function prevImage() {
//   var loc = localStorage.getItem("loc");
//   var int = localStorage.getItem("int");
//   var varname = localStorage.getItem("varname");
//   showImage(loc, int, varname);
// }

// // Event listener for keyboard arrow keys
// document.addEventListener('keydown', function(event) {
//   var loc = localStorage.getItem("loc");
//   var int = localStorage.getItem("int");
//   var varname = localStorage.getItem("varname");

//   if (event.code === 'ArrowLeft') {
//     // Handle previous image
//     prevImage();
//   } else if (event.code === 'ArrowRight') {
//     // Handle next image
//     nextImage();
//   }
// });

// // Event listener for the "Previous" button
// const prevButton = document.getElementById('prevButton');
// prevButton.addEventListener('click', prevImage);

// // Event listener for the "Next" button
// const nextButton = document.getElementById('nextButton');
// nextButton.addEventListener('click', nextImage);


// #################### END VAV ##########################

// if (typeof loc !== 'undefined') {
//     var loc = "high_level"
//     localStorage.setItem("loc", loc);
//   } else {
//   }

// if (typeof int !== 'undefined') {
//     var int = "20190516Z00"
//     localStorage.setItem("int", int);
//   } else {
//   }

// if (typeof valid !== 'undefined') {
//     var valid = "20190516Z00"
//     localStorage.setItem("valid", valid);
//   } else {
//   }

// if (typeof valid !== 'undefined') {
//   var dataI = "20190516Z00"
//   localStorage.setItem("dataI", dataI);
// } else {
// }

// if (typeof valid !== 'undefined') {
//   var dataJ = "20190518Z00"
//   localStorage.setItem("dataJ", dataJ);
// } else {
// }

// if (typeof varname !== 'undefined') {
//   var varname = "50kPa"
//   localStorage.setItem("varname", varname);
// } else {
// }

// Get the sidebar element

// Get the toggle button element
const toggleButton = document.querySelector('#btn');

// Add event listener to the toggle button
toggleButton.addEventListener('click', function() {
  // Toggle the collapsed class on the sidebar
  sidebar.classList.toggle('collapsed');
});

function changeText() {
  const btn = document.getElementById('btn');
  const submenuText1 = document.getElementById('submenu-text1');
  const submenuText2 = document.getElementById('submenu-text2');
  const submenuText3 = document.getElementById('submenu-text3');
  const submenuText4 = document.getElementById('submenu-text4');

  if (btn.textContent === 'Forecast Parameters') {
    btn.textContent = 'FP';
    submenuText1.textContent = 'UH';
    submenuText1.style.fontSize = '10px'; // Change the font size to desired value
    submenuText2.textContent = 'UM';
    submenuText2.style.fontSize = '10px'; // Change the font size to desired value
    submenuText3.textContent = 'SF';
    submenuText3.style.fontSize = '10px'; // Change the font size to desired value
    submenuText4.textContent = 'MP';
    submenuText4.style.fontSize = '10px'; // Change the font size to desired value


  } else {
    btn.textContent = 'Forecast Parameters';
    submenuText1.textContent = 'Upper Air Heights';
    submenuText1.style.fontSize = ''; // Change the font size to desired value
    submenuText2.textContent = 'Upper Air Moisture';
    submenuText2.style.fontSize = ''; // Change the font size to desired value
    submenuText3.textContent = 'Surface';
    submenuText3.style.fontSize = ''; // Change the font size to desired value
    submenuText4.textContent = 'Milti-Parameter';
    submenuText4.style.fontSize = ''; // Change the font size to desired value

  }
}
