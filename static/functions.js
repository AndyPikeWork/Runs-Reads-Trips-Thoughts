
// Function to update the Category dropdown based on the selected Type
function updateCategories() {
    if (document.getElementById('note_type')!=null) {
        const type_selected = document.getElementById('note_type');
        const categorySelect = document.getElementById('note_category');
        const selectedType = type_selected.value;
        // Clear existing options
        categorySelect.innerHTML = '';
        console.log("Selected Value: " + selectedType)
        
        // For each Category and Type (in the list from app.py)
        for(i = 0; i < categories_list.length; i++) {
            // If the HTML selected Type matches the Type from app.py
            if(selectedType == categories_list[i].type) {
                // Go through each of the categories within that type
                for(j = 0; j < categories_list[i].categories.length; j++) {
                    // Select the occurence of that category
                    category = categories_list[i].categories[j]
                    const option = document.createElement('option');
                    option.value = category;
                    option.text = category;
                    if(existing_category == category) {
                        option.selected = true;
                    }
                    
                    categorySelect.add(option);
                }
            }
        }
    } else {
        // do nothing (i.e. pages that don't need to populate the drop-downs for the Categories)
    }
}

// creating buttons to filter the Words History page
function words_app_history_buttons() {

    if (document.getElementById("words_type_filter")!=null) {
        
        var container = document.getElementById("words_type_filter"); 
        
        for(i = 0; i < categories_list.length; i++) {
            // used "let" instead of "var" to ensure a block-scoped variable
            let type_filter = categories_list[i].type;
            var button = document.createElement("button");
            button.textContent = type_filter;
            button.className = "btn btn-outline-primary word_history_filter_button";
            button.addEventListener("click", function() {


                // check if the button has already been pressed (based on the active class)
                var prevSelectedButton = container.querySelector('.selected_cell');
                if (prevSelectedButton) {
                    prevSelectedButton.classList.remove('selected_cell');
                }
                button.classList.add('selected_cell');

                updateCategoriesButtons(type_filter); // Call your existing function with the button value
                filter_words_hitory(type_filter, "type");
                hideColumnsForThoughts(type_filter);

            });
            container.appendChild(button);
        } 
    } else {
        // do nothing
    }
}

// Adding buttons for the Categories underneath the Type buttons
function updateCategoriesButtons(selectedType){
    if (document.getElementById("words_categories_filter")!=null) {
        var container = document.getElementById("words_categories_filter"); 
        container.innerHTML = "";

        for(i = 0; i < categories_list.length; i++) {
            if(selectedType == categories_list[i].type) {
                for(j = 0; j < categories_list[i].categories.length; j++) {
                    let category_filter = categories_list[i].categories[j];
                    if(category_filter.length == 0) {
                        // do nothing because there are no categories for this Type
                    } else {
                        var button = document.createElement("button");
                        button.textContent = category_filter;
                        button.className = "btn btn-outline-info word_history_filter_button";
                        button.addEventListener("click", function() {
                            filter_words_hitory(category_filter, "category");
                        });
                        container.appendChild(button);
                    }
                }
            }
        }

    } else {
        // do nothing
    }
}


// Filtering the table to what button is clicked (between Type and Category)
// @index - The value selected (e.g. "Meeting" type or "NHS England" category) which will search the column for values
// @group - whether it's "Type" or "Category"
function filter_words_hitory(index, group) {
    var table = document.getElementById("words_history_tbl");
    var rows = table.getElementsByTagName("tr");

    for (var i = 0; i < rows.length; i++) {
        var cells = rows[i].getElementsByTagName("td");
        if(group == "type") {
            var index_cell = cells[3];
        } else if (group == "category") {
            var index_cell = cells[4];
        }
        

        if (index_cell) {
          var cell_contents = index_cell.textContent || index_cell.innerText;
            // If the value within the column matches the index (what the users has clicked on)
            if (cell_contents === index) {
                // ...show that row
                rows[i].style.display = "";
            } else {
                // ...else hide it
                rows[i].style.display = "none";
            }
        }
    }
}

function hideColumnsForThoughts(type_selected) {
    if (document.getElementsByClassName("not_thought_col") != null) {

        const toggleColsOff = document.getElementsByClassName("not_thought_col");
        const toggleColsOn = document.getElementsByClassName("thought_col");

        if (type_selected == "Thought") {
            for (let i = 0; i < toggleColsOff.length; i++) { toggleColsOff[i].style.display = "none"; }
            for (let i = 0; i < toggleColsOn.length; i++) { toggleColsOn[i].style.display = "table-cell"; }
        } 
        else {
            for (let i = 0; i < toggleColsOff.length; i++) { toggleColsOff[i].style.display = "table-cell";  }
            for (let i = 0; i < toggleColsOn.length; i++) { toggleColsOn[i].style.display = "none"; }
        }
    }
}

// Words - View: Switch on the Left Hand panel
function checkWidthAndTogglePanel() {
    if(document.getElementById('words_view_left_panel') != null) {
        if (window.innerWidth >= 1000) {
            document.getElementById('words_view_left_panel').style.display = 'block';
        } else {
            document.getElementById('words_view_left_panel').style.display = 'none';
        }
    }
}

window.addEventListener('resize', checkWidthAndTogglePanel);


// Populate the drop down options of categories
function words_view_dropdown() {
    if (document.getElementById("current_words_view_category") != null) {
        // what the page loads as the main category (not what is selected)
        var loaded_category = $("#current_words_view_category").val();
        var container = document.getElementById("words_view_drop_down"); 
        for(i = 0; i < categories_list.length; i++) {
            for(j = 0; j < categories_list[i].categories.length; j++) {
                type = categories_list[i].type
                category = categories_list[i].categories[j]
                const option = document.createElement('option');
                option.value = category;
                option.text = type + " > " + category;
                if(category == loaded_category) {
                    option.selected = true;
                }
                container.appendChild(option);
            }
        }
        update_left()
    }
}

// Update notes on the left hand panel after drop down option selected
function update_left_hand_words_panel() {
    $("#words_view_drop_down").change(function() {
        update_left();                    
    });
}

function update_left() {
    var selectedValue = $("#words_view_drop_down").val();
    $(".words_view_left_panel_link").hide();
    $(".words_view_left_panel_link").each(function() {
        var hiddenValue = $(this).find("input[type='hidden']").val();
        if (hiddenValue == selectedValue) {
            $(this).show();
        }
    });
}




function load_theme() {
    
    // In load_theme and toggleTheme:
    const body = document.body; 
    const toggleButton = document.getElementById('toggle-theme');
    const left_panel = document.getElementById('words_view_left_panel');
    on_words_view_page = false;
    if(document.getElementById('words_view_left_panel') != null) {
        on_words_view_page = true;
    }


    // Set initial theme based on local storage
    const storedTheme = localStorage.getItem('theme');
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)');
    const shouldUseDarkMode = storedTheme === 'dark' || prefersDarkMode.matches;
    if (shouldUseDarkMode) {
      body.classList.add('dark-mode');
      if(on_words_view_page) {
        left_panel.classList.toggle('black-mode');
      }
      
    }
    // Show the body element again (switched off in CSS)
    body.style.display = 'block';
    toggleButton.addEventListener('click', toggleTheme);
    
} 

function toggleTheme() {
    const body = document.body;
    const left_panel = document.getElementById('words_view_left_panel');
    if(document.getElementById('words_view_left_panel') != null) {
        on_words_view_page = true;
    }
    const isDarkMode = body.classList.contains('dark-mode');
    body.classList.toggle('dark-mode');
    if(on_words_view_page) {
        left_panel.classList.toggle('black-mode');
      }
    localStorage.setItem('theme', isDarkMode ? 'light' : 'dark');
  }

  function make_image_big() {
    $('.words_image').click(function(event) {
        // stops the image opening up in a new tab (keeps it within the current page)
        event.preventDefault();
        $(this).toggleClass('expanded-image');
      });
  }


$(document).ready(function() {
    load_theme();
    words_view_dropdown();
    update_left_hand_words_panel();
    updateCategories();
    words_app_history_buttons();
    updateCategoriesButtons();
    hideColumnsForThoughts("Meeting");
    checkWidthAndTogglePanel();
    make_image_big();
});

