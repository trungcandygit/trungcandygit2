document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('survey-form');

    function handleFormSubmission() {
        const formData = new FormData(form);
        const data = {};

        formData.forEach((value, key) => {
            // Handle multiple values for the same key (like checkboxes)
            if (!data[key]) {
                data[key] = [];
            }
            data[key].push(value);
        });

        // Save the data to localStorage
        localStorage.setItem('formData', JSON.stringify(data));

        // Redirect to preview page
        window.location.href = 'preview.html';
    }

    document.getElementById('submit-button').addEventListener('click', handleFormSubmission);
});
