document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('survey-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(form);
        const params = new URLSearchParams();

        formData.forEach((value, key) => {
            if (key === 'question16' && formData.get('question16') === 'Khác') {
                value = formData.get('question16_other') || value;
            }
            params.append(key, value);
        });

        // Redirect to preview.html with query parameters
        window.location.href = `preview.html?${params.toString()}`;
    });
});
