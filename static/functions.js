
// Function to update the Category dropdown based on the selected Type
function updateCategories() {
    const type_selected = document.getElementById('note_type');
    const categorySelect = document.getElementById('note_category');
    const selectedType = type_selected.value;

    // Clear existing options
    categorySelect.innerHTML = '';

    // Populate with options based on the selected type
    categories[selectedType].forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.text = category;
        categorySelect.add(option);
    });
}

// Initial call to populate categories based on the default selected type
updateCategories();