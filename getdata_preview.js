document.addEventListener('DOMContentLoaded', function() {
    const params = new URLSearchParams(window.location.search);
    const tableBody = document.querySelector('#preview-table tbody');
    let fileContent = '';
    let emailBody = '';

    // Define questions and keys
    const questions = {
        'question1': 'Doanh nghiệp của bạn có bao nhiêu nhân sự?',
        'question2': 'Doanh nghiệp của bạn đã đầu tư bao nhiêu tiền vào việc áp dụng mô hình kinh tế tuần hoàn trong năm qua?',
        'question3': 'Doanh nghiệp của bạn có bao nhiêu dự án liên quan đến mô hình kinh tế tuần hoàn?',
        'question4': 'Mức độ hài lòng của bạn với kết quả của việc áp dụng mô hình kinh tế tuần hoàn là gì?',
        'question5': 'Tỷ lệ phần trăm doanh thu từ mô hình kinh tế tuần hoàn chiếm bao nhiêu?',
        'question6': 'Doanh nghiệp của bạn có kế hoạch mở rộng mô hình kinh tế tuần hoàn trong năm tới không?',
        'question7': 'Doanh nghiệp của bạn có bao nhiêu nhân viên phụ trách việc áp dụng mô hình kinh tế tuần hoàn?',
        'question8': 'Chi phí đầu tư cho công nghệ mới liên quan đến mô hình kinh tế tuần hoàn là bao nhiêu?',
        'question9': 'Doanh nghiệp của bạn đã tổ chức bao nhiêu khóa đào tạo về mô hình kinh tế tuần hoàn?',
        'question10': 'Mức độ ảnh hưởng của mô hình kinh tế tuần hoàn đến sự hài lòng của khách hàng là gì?',
        'question11': 'Doanh nghiệp của bạn đã thực hiện bao nhiêu biện pháp để giảm lượng chất thải?',
        'question12': 'Tỷ lệ giảm thiểu chất thải từ mô hình kinh tế tuần hoàn so với năm trước là bao nhiêu?',
        'question13': 'Doanh nghiệp của bạn có bao nhiêu sản phẩm được thiết kế theo mô hình kinh tế tuần hoàn?',
        'question14': 'Doanh nghiệp của bạn đã đầu tư bao nhiêu vào nghiên cứu và phát triển mô hình kinh tế tuần hoàn?',
        'question15': 'Mức độ hiệu quả của mô hình kinh tế tuần hoàn đối với lợi nhuận doanh nghiệp là gì?',
        'question16': 'Theo bạn, yếu tố nào là quan trọng nhất trong việc áp dụng mô hình kinh tế tuần hoàn?',
        'question17': 'Doanh nghiệp của bạn đã thực hiện những biện pháp nào để giảm thiểu chất thải?',
        'question18': 'Bạn nghĩ mô hình kinh tế tuần hoàn sẽ ảnh hưởng như thế nào đến thị trường trong 5 năm tới?',
        'question19': 'Các khó khăn chính mà doanh nghiệp của bạn gặp phải khi áp dụng mô hình kinh tế tuần hoàn là gì?',
        'question20': 'Theo bạn, có những hỗ trợ nào từ chính phủ hoặc tổ chức khác để khuyến khích áp dụng mô hình kinh tế tuần hoàn?'
    };

    // Populate the table and fileContent
    for (const [key, question] of Object.entries(questions)) {
        const answer = params.get(key);
        if (answer) {
            // Add to table
            const row = document.createElement('tr');
            const questionCell = document.createElement('td');
            const answerCell = document.createElement('td');
            questionCell.textContent = question;
            answerCell.textContent = answer;
            row.appendChild(questionCell);
            row.appendChild(answerCell);
            tableBody.appendChild(row);

            // Add to file content
            fileContent += `${question}\n${answer}\n\n`;
            emailBody += `<tr><td>${question}</td><td>${answer}</td></tr>`;
        }
    }

    // Add closing tags for email body
    emailBody = `
        <h1>Kết quả Khảo sát</h1>
        <table border="1" cellspacing="0" cellpadding="5">
            <tr><th>Câu Hỏi</th><th>Câu Trả Lời</th></tr>
            ${emailBody}
        </table>
    `;

    // Download file
    document.getElementById('download-file').addEventListener('click', function() {
        const blob = new Blob([fileContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'answers.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });

    // Open email client
    document.getElementById('send-email').addEventListener('click', function() {
        const subject = encodeURIComponent('Kết quả Khảo sát');
        const body = encodeURIComponent(`Dưới đây là kết quả khảo sát:\n\n${fileContent}`);
        window.location.href = `mailto:trungxcpro@gmail.com?subject=${subject}&body=${body}`;
    });
});
