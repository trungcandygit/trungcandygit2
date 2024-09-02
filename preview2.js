document.addEventListener('DOMContentLoaded', () => {
    // Retrieve stored answers from localStorage
    const answers = JSON.parse(localStorage.getItem('answers'));

    if (answers) {
        const form = document.getElementById('answers-form');
        
        // List of questions and their selectors for displaying answers
        const questions = [
            { id: 'q1', type: 'text', label: '1. Doanh nghiệp của bạn có bao nhiêu nhân sự?' },
            { id: 'q2', type: 'text', label: '2. Doanh nghiệp của bạn đã đầu tư bao nhiêu tiền vào việc áp dụng mô hình kinh tế tuần hoàn trong năm qua?' },
            { id: 'q3', type: 'text', label: '3. Doanh nghiệp của bạn có bao nhiêu dự án liên quan đến mô hình kinh tế tuần hoàn?' },
            { id: 'q4', type: 'select', label: '4. Mức độ hài lòng của bạn với kết quả của việc áp dụng mô hình kinh tế tuần hoàn là gì?', otherId: 'q4_other' },
            { id: 'q5', type: 'text', label: '5. Tỷ lệ phần trăm doanh thu từ mô hình kinh tế tuần hoàn chiếm bao nhiêu?' },
            { id: 'q6', type: 'select', label: '6. Doanh nghiệp của bạn có kế hoạch mở rộng mô hình kinh tế tuần hoàn trong năm tới không?', otherId: 'q6_other' },
            { id: 'q7', type: 'text', label: '7. Doanh nghiệp của bạn có bao nhiêu nhân viên phụ trách việc áp dụng mô hình kinh tế tuần hoàn?' },
            { id: 'q8', type: 'text', label: '8. Chi phí đầu tư cho công nghệ mới liên quan đến mô hình kinh tế tuần hoàn là bao nhiêu?' },
            { id: 'q9', type: 'text', label: '9. Doanh nghiệp của bạn đã tổ chức bao nhiêu khóa đào tạo về mô hình kinh tế tuần hoàn?' },
            { id: 'q10', type: 'textarea', label: '10. Mức độ ảnh hưởng của mô hình kinh tế tuần hoàn đến sự hài lòng của khách hàng là gì?' },
            { id: 'q11', type: 'text', label: '11. Doanh nghiệp của bạn đã thực hiện bao nhiêu biện pháp để giảm lượng chất thải?' },
            { id: 'q12', type: 'text', label: '12. Tỷ lệ giảm thiểu chất thải từ mô hình kinh tế tuần hoàn so với năm trước là bao nhiêu?' },
            { id: 'q13', type: 'text', label: '13. Doanh nghiệp của bạn có bao nhiêu sản phẩm được thiết kế theo mô hình kinh tế tuần hoàn?' },
            { id: 'q14', type: 'text', label: '14. Doanh nghiệp của bạn đã đầu tư bao nhiêu vào nghiên cứu và phát triển mô hình kinh tế tuần hoàn?' },
            { id: 'q15', type: 'select', label: '15. Mức độ hiệu quả của mô hình kinh tế tuần hoàn đối với lợi nhuận doanh nghiệp là gì?', otherId: 'q15_other' },
            { id: 'q16', type: 'textarea', label: '16. Theo bạn, yếu tố nào là quan trọng nhất trong việc áp dụng mô hình kinh tế tuần hoàn?' },
            { id: 'q17', type: 'checkbox', label: '17. Doanh nghiệp của bạn đã thực hiện những biện pháp nào để giảm thiểu chất thải?', otherId: 'q17_other' },
            { id: 'q18', type: 'textarea', label: '18. Bạn nghĩ mô hình kinh tế tuần hoàn sẽ ảnh hưởng như thế nào đến thị trường trong 5 năm tới?' },
            { id: 'q19', type: 'textarea', label: '19. Doanh nghiệp của bạn có gặp khó khăn gì khi áp dụng mô hình kinh tế tuần hoàn không? Nếu có, vui lòng mô tả.' },
            { id: 'q20', type: 'textarea', label: '20. Đề xuất của bạn về cách cải thiện việc áp dụng mô hình kinh tế tuần hoàn trong doanh nghiệp là gì?' }
        ];

        questions.forEach((question, index) => {
            const answer = answers[index];
            const questionDiv = document.createElement('div');
            questionDiv.classList.add('form-group');
            
            // Create label for the question
            const label = document.createElement('label');
            label.textContent = question.label;
            questionDiv.appendChild(label);

            if (question.type === 'select') {
                const select = document.createElement('select');
                select.id = question.id;
                select.disabled = true;
                select.innerHTML = `
                    <option value="Rất hài lòng">Rất hài lòng</option>
                    <option value="Hài lòng">Hài lòng</option>
                    <option value="Bình thường">Bình thường</option>
                    <option value="Không hài lòng">Không hài lòng</option>
                    <option value="Rất không hài lòng">Rất không hài lòng</option>
                    <option value="Khác">Khác</option>
                `;
                select.value = answer[0];
                questionDiv.appendChild(select);

                if (answer[0] === 'Khác') {
                    const otherInput = document.createElement('input');
                    otherInput.type = 'text';
                    otherInput.id = question.otherId;
                    otherInput.classList.add('hidden');
                    otherInput.value = answer[1];
                    questionDiv.appendChild(otherInput);
                }
            } else if (question.type === 'checkbox') {
                const checkboxes = [
                    'Tái chế',
                    'Giảm thiểu',
                    'Tái sử dụng',
                    'Khác'
                ];

                checkboxes.forEach(value => {
                    const label = document.createElement('label');
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.disabled = true;
                    checkbox.value = value;
                    checkbox.checked = answer.includes(value);
                    label.appendChild(checkbox);
                    label.appendChild(document.createTextNode(value));
                    questionDiv.appendChild(label);
                });

                if (answer.includes('Khác')) {
                    const otherInput = document.createElement('input');
                    otherInput.type = 'text';
                    otherInput.id = question.otherId;
                    otherInput.classList.add('hidden');
                    otherInput.value = answer[answer.length - 1];
                    questionDiv.appendChild(otherInput);
                }
            } else if (question.type === 'textarea') {
                const textarea = document.createElement('textarea');
                textarea.id = question.id;
                textarea.disabled = true;
                textarea.rows = 4;
                textarea.value = answer;
                questionDiv.appendChild(textarea);
            } else {
                const input = document.createElement('input');
                input.type = question.type;
                input.id = question.id;
                input.disabled = true;
                input.value = answer;
                questionDiv.appendChild(input);
            }

            form.appendChild(questionDiv);
        });
    }
});
