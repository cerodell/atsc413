
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

try {
  if (typeof loc !== 'undefined') {
    var loc = "high_level"
    localStorage.setItem("loc", loc);
  } else {
  }
} catch (error) {
  console.log("false");
}

try {
  if (typeof int !== 'undefined') {
    var int = "20190516Z00"
    localStorage.setItem("int", int);
  } else {
  }
} catch (error) {
  console.log("false");
}

try {
  if (typeof valid !== 'undefined') {
    var valid = "20190516Z00"
    localStorage.setItem("valid", valid);
  } else {
  }
} catch (error) {
  console.log("false");
}

try {
  if (typeof varname !== 'undefined') {

    var varname = "50kPa"
    localStorage.setItem("varname", varname);
  } else {
  }
} catch (error) {
  console.log("false");
}
// Retrieve the cached variable
var loc = localStorage.getItem("loc");
var int = localStorage.getItem("int");
var valid = localStorage.getItem("valid");
var varname = localStorage.getItem("varname");
showImage(loc, int, valid, varname);


function toggleDropdown() {
  const dropdownContainer = document.getElementById('dropdownContainer');
  dropdownContainer.classList.toggle('open');
}



var currentIndex = 0; // Initialize the current index of the date range

function showImage(loc, int, valid, varname) {
  var varname = localStorage.getItem("varname");

  if (isDateInPast(parseDateTime(valid), parseDateTime(int))) {
    var valid = int
    localStorage.setItem("valid", valid);
  } else {
  }
  console.log(loc);
  console.log(localStorage.getItem("loc", loc));
  if (loc === localStorage.getItem("loc", loc)) {
    console.log("Same location");
  } else {
    var valid = int
    localStorage.setItem("valid", valid);
    console.log("NEW Same location");
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
      var loc = localStorage.getItem("loc");
      var int = localStorage.getItem("int");
      var valid = localStorage.getItem("valid");
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
