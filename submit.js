document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('survey-form');
    const submitButton = document.getElementById('submit-button');

    // Function to validate if all fields are filled
    function validateForm() {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value) {
                isValid = false;
                input.style.borderColor = 'red'; // Highlight empty required fields
            } else {
                input.style.borderColor = ''; // Reset border color
            }
        });

        return isValid;
    }

    // Function to handle form submission
    function handleFormSubmission() {
        if (!validateForm()) {
            alert('Vui lòng điền đầy đủ tất cả các trường yêu cầu!');
            return;
        }

        const formData = new FormData(form);
        const data = {};

        formData.forEach((value, key) => {
            if (!data[key]) {
                data[key] = [];
            }
            data[key].push(value);
        });

        // Save the data to localStorage
        localStorage.setItem('surveyData', JSON.stringify(data));

        // Redirect to preview page
        window.location.href = 'preview.html';
    }

    // Event listener for the submit button
    submitButton.addEventListener('click', handleFormSubmission);

    // Handle the display of other input field based on the selection
    document.getElementById('question11').addEventListener('change', (event) => {
        const otherField = document.getElementById('question11_other');
        if (event.target.value === 'Khác') {
            otherField.style.display = 'inline';
        } else {
            otherField.style.display = 'none';
        }
    });
});
