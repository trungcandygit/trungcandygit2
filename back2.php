<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $to = 'trungxcpro@gmail.com';
    $subject = 'Khảo sát Nghiên cứu Khoa học - Kết quả';

    // Start building the email body
    $message = '<html><body>';
    $message .= '<h1>Kết quả Khảo sát</h1>';
    $message .= '<table border="1" cellspacing="0" cellpadding="5">';
    $message .= '<tr><th>Câu Hỏi</th><th>Câu Trả Lời</th></tr>';

    // Define the questions
    $questions = [
        'question1' => 'Doanh nghiệp của bạn có bao nhiêu nhân sự?',
        'question2' => 'Doanh nghiệp của bạn đã đầu tư bao nhiêu tiền vào việc áp dụng mô hình kinh tế tuần hoàn trong năm qua?',
        'question3' => 'Doanh nghiệp của bạn có bao nhiêu dự án liên quan đến mô hình kinh tế tuần hoàn?',
        'question4' => 'Mức độ hài lòng của bạn với kết quả của việc áp dụng mô hình kinh tế tuần hoàn là gì?',
        'question5' => 'Tỷ lệ phần trăm doanh thu từ mô hình kinh tế tuần hoàn chiếm bao nhiêu?',
        'question6' => 'Doanh nghiệp của bạn có kế hoạch mở rộng mô hình kinh tế tuần hoàn trong năm tới không?',
        'question7' => 'Doanh nghiệp của bạn có bao nhiêu nhân viên phụ trách việc áp dụng mô hình kinh tế tuần hoàn?',
        'question8' => 'Chi phí đầu tư cho công nghệ mới liên quan đến mô hình kinh tế tuần hoàn là bao nhiêu?',
        'question9' => 'Doanh nghiệp của bạn đã tổ chức bao nhiêu khóa đào tạo về mô hình kinh tế tuần hoàn?',
        'question10' => 'Mức độ ảnh hưởng của mô hình kinh tế tuần hoàn đến sự hài lòng của khách hàng là gì?',
        'question11' => 'Doanh nghiệp của bạn đã thực hiện bao nhiêu biện pháp để giảm lượng chất thải?',
        'question12' => 'Tỷ lệ giảm thiểu chất thải từ mô hình kinh tế tuần hoàn so với năm trước là bao nhiêu?',
        'question13' => 'Doanh nghiệp của bạn có bao nhiêu sản phẩm được thiết kế theo mô hình kinh tế tuần hoàn?',
        'question14' => 'Doanh nghiệp của bạn đã đầu tư bao nhiêu vào nghiên cứu và phát triển mô hình kinh tế tuần hoàn?',
        'question15' => 'Mức độ hiệu quả của mô hình kinh tế tuần hoàn đối với lợi nhuận doanh nghiệp là gì?',
        'question16' => 'Theo bạn, yếu tố nào là quan trọng nhất trong việc áp dụng mô hình kinh tế tuần hoàn?',
        'question17' => 'Doanh nghiệp của bạn đã thực hiện những biện pháp nào để giảm thiểu chất thải?',
        'question18' => 'Bạn nghĩ mô hình kinh tế tuần hoàn sẽ ảnh hưởng như thế nào đến thị trường trong 5 năm tới?',
        'question19' => 'Các khó khăn chính mà doanh nghiệp của bạn gặp phải khi áp dụng mô hình kinh tế tuần hoàn là gì?',
        'question20' => 'Theo bạn, có những hỗ trợ nào từ chính phủ hoặc tổ chức khác để khuyến khích áp dụng mô hình kinh tế tuần hoàn?'
    ];

    foreach ($questions as $key => $question) {
        if (isset($_POST[$key])) {
            $answer = htmlspecialchars($_POST[$key]);
            $message .= '<tr><td>' . $question . '</td><td>' . $answer . '</td></tr>';
        }
    }

    $message .= '</table>';
    $message .= '</body></html>';

    // To send HTML mail, the Content-type header must be set
    $headers = "MIME-Version: 1.0" . "\r\n";
    $headers .= "Content-type:text/html;charset=UTF-8" . "\r\n";

    // Additional headers
    $headers .= 'From: noreply@yourdomain.com' . "\r\n";

    if (mail($to, $subject, $message, $headers)) {
        echo 'Email sent successfully.';
    } else {
        echo 'Failed to send email.';
    }
}
?>
