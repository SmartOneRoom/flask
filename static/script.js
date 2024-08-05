document.addEventListener('DOMContentLoaded', function() {
    const searchButton = document.getElementById('searchButton');
    const result = document.getElementById('result');
    const webcamFeed = document.getElementById('webcamFeed');
    const segmentation = document.getElementById('segmentation');

    // 웹캠 피드 URL 설정
    webcamFeed.src = '/video_feed';

    // 초기 세그멘테이션 이미지 숨기기
    segmentation.style.display = 'none';

    searchButton.addEventListener('click', startSegmentation);

    function startSegmentation() {
        // 세그멘테이션 시작 메시지 표시
        result.innerHTML = "세그멘테이션을 시작합니다...";
        
        // 서버로 세그멘테이션 시작 요청 보내기
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: "box" }), // 고정된 텍스트 "box" 사용
        })
        .then(response => response.json())
        .then(data => {
            // 검색 결과 표시
            result.innerHTML = data.result;
            
            // 세그멘테이션 이미지 표시
            segmentation.src = '/segmentation_feed';
            segmentation.style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            result.innerHTML = "세그멘테이션 중 오류가 발생했습니다.";
            segmentation.style.display = 'none';
        });
    }
});