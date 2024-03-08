
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

  // HERE
  function load_zoom() {

    if(document.getElementById('word_view_content') != null) {
        const stored_zoom = localStorage.getItem('zoom');
        const shouldZoomIn = stored_zoom === 'out';
        const contentDiv = document.getElementsByClassName('note_text_p')[0];
        if (shouldZoomIn) {
            contentDiv.classList.toggle('large-font');
            }
        }
  }

  function make_text_big() {
    const fontToggleBtn = document.getElementById('toggle-zoom');
    const contentDiv = document.getElementsByClassName('note_text_p')[0];


    fontToggleBtn.addEventListener('click', () => {
        const ZoomedIn = contentDiv.classList.contains('large-font'); // True or False

        // When you click it, it'll change between Zoom in and Zoom out
        contentDiv.classList.toggle('large-font');
        // Change the local storage value also
        localStorage.setItem('zoom', ZoomedIn ? 'in' : 'out');
        console.log(ZoomedIn);
    });
  }

  function task_add() {
    $('#task_add_form').submit(function(event) {
        event.preventDefault(); // Prevent default form submission
        task_submit("new");
    });
  }

  function task_submit(action = "new", task_id=null) {

    console.log(action + ". " + task_id)

        if(action == "new") {
            // Get task data from the form
            taskData = {
                id: null,
                task: $('#add_task_task').val(),
                due: $('#add_task_due').val(),
                category: $('#add_task_category').val(),
                status: action
            };
        } 
        if(action == "done") {
            // Get task data from the form
            taskData = {
                id: task_id,
                task: null,
                due: null,
                category: null,
                status: action
            };
        } 
        if(action == "delete") {
            // Get task data from the form
            taskData = {
                id: task_id,
                task: null,
                due: null,
                category: null,
                status: action
            };
        } 
      
        // Send AJAX request
        $.ajax({
          url: '/words/tasks',
          method: 'POST',
          contentType: 'application/json',
          data: JSON.stringify(taskData),
          success: function(response) {
            // Handle successful response (e.g., update UI)
            updateTaskList(response);
          },
          error: function(error) {
            console.error('Error:', error);
            // Handle errors (e.g., display error message to user)
          }
        });
        const task_input_task = document.getElementById('add_task_task');
        const task_input_due_date = document.getElementById('add_task_due');
        task_input_task.value = '';
        task_input_due_date.value = '';
  }


  function updateTaskList(tasks) {
    $('#task-list').empty(); // Clear existing tasks
  
    const table = $('<table>'); // Create a table element
    table.addClass('table tasks_table'); // Add Bootstrap class for styling (optional)
  
    const thead = $('<thead>'); // Create table header
    const tr = $('<tr>'); // Create header row
  
    // Add headers for task information
    tr.append($('<th>').text('').addClass('w-10'));
    tr.append($('<th>').text('Task').addClass('w-40'));
    tr.append($('<th>').text('Category').addClass('w-10'));
    tr.append($('<th>').text('Due Date').addClass('w-10'));
    tr.append($('<th>').text('Elapsed').addClass('w-10'));
    tr.append($('<th>').text('').addClass('w-10'));
    // Add more headers as needed
  
    thead.append(tr);
    table.append(thead); // Add header to table
  
    const tbody = $('<tbody>'); // Create table body
    tasks = sort_tasks(tasks);
    tasks.forEach(function(task) {
      const tr = $('<tr>'); // Create table row
    
      
      // Create checkbox element
      const done_button = $('<input>').attr({
        type: 'button',
        value: '✓',
        class: 'task_tick_button',
        id: 'task-'+task.id, // Unique ID for each checkbox
      }).on('click', function(event) {
        const taskId = $(this).attr('id').split('-')[1];  // Extract task ID
        task_submit("done", taskId);  // Call the function with task ID
    });

      const remove_button = $('<input>').attr({
        type: 'button',
        value: '-',
        class: 'task_remove_button',
        id: 'task-'+task.id, // Unique ID for each checkbox
      }).on('click', function(event) {
        const taskId = $(this).attr('id').split('-')[1];  // Extract task ID
        task_submit("delete", taskId);  // Call the function with task ID
    });
  
    elapsed_days=daysBetween(task.date_added)
    
      // Create table cells for each task property
      const tdCheckbox = $('<td>').append(done_button);
      const tdTask = $('<td>').text(task.task);
      const tdCategory = $('<td>').text(task.category);
      const tdDueDate = $('<td>').text(task.date_due);
      const tdElapsed = $('<td>').text(elapsed_days + " days");
      const tdRemove = $('<td>').append(remove_button);
      // Add more table cells as needed
  
    if(task.status == "done") {
        tr.attr({ class: 'task_row_done'});
        tr.append($('<td>'));
      }
    if(task.status != "done") {
        tr.append(tdCheckbox); // Add cells to the row
      }
      
      tr.append(tdTask);
      tr.append(tdCategory);
      tr.append(tdDueDate);
    if(task.status == "done") {
        tr.append($('<td>'));
    } else {
        tr.append(tdElapsed);
    }
      tr.append(tdRemove);
      // Append more cells as needed
      tbody.append(tr); // Add row to table body
    });
  
    table.append(tbody); // Add body to table
    $('#task-list').append(table); // Append table to the target element
    tasks_filter(tasks);
  }

function tasks_filter(tasks) {
    // get the unique values of the task categories
    const categories = [...new Set(tasks.map(item => item["category"]))];
    const taskOptionsDiv = document.getElementById("task_options"); // Assuming the div has this ID

    categories.forEach(category => {
        const button = document.createElement("button");
        button.addClass = "task_filter_button";
        button.textContent = category;
        button.addEventListener("click", () => filter_tasks_table(category)); // Add event listener for filtering
            taskOptionsDiv.appendChild(button);
        });
}

function filter_tasks_table(category) {

    var table = document.getElementsByClassName("tasks_table")[0];
    var rows = table.getElementsByTagName("tr");

    for (var i = 1; i < rows.length; i++) {
        var cells = rows[i].getElementsByTagName("td");
        var cellText = cells[2].textContent;  // Get the text content of the cell

        console.log(cells[2])
        // for each cell in a row
        if(cellText == category) {
            rows[i].style.display = "table-row";
        } else {
            // ...else hide it
            rows[i].style.display = "none";
        }
    }
}

function sort_tasks(tasks) {
 
    return tasks.slice().sort((a, b) => {
        // Sort by "new" tasks appearing first
        if (a.status === "new" && b.status === "done") {
          return -1;
        } else if (a.status === "done" && b.status === "new") {
          return 1;
        } else {
          // If statuses are the same, maintain original order
          return 0;
        }
      });
}
    

function daysBetween(dateString, seconddate = null) {
    // Parse the first date string
    const firstDate = new Date(dateString);
    if(seconddate) {
        seconddate = seconddate;
    } else {
        seconddate = new Date();
    }
    // Check if the first date is after today (negative difference would result)
    if (firstDate > seconddate) {
      return 0; // Handle future dates (return 0 days difference)
    }
    // Calculate the time difference in milliseconds
    const timeDiff = seconddate.getTime() - firstDate.getTime();
    // Convert milliseconds to days and round down to whole days
    const daysDiff = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
    return daysDiff;
  }
  

$(document).ready(function() {
    load_theme();
    load_zoom();
    words_view_dropdown();
    update_left_hand_words_panel();
    updateCategories();
    words_app_history_buttons();
    updateCategoriesButtons();
    hideColumnsForThoughts("Meeting");
    checkWidthAndTogglePanel();
    make_image_big();
    make_text_big();
    task_add();
});

