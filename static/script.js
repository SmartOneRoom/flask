document.addEventListener('DOMContentLoaded', function() {
    const searchButton = document.getElementById('searchButton');
    const sourceText = document.getElementById('sourceText');
    const result = document.getElementById('result');
    const webcamFeed = document.getElementById('webcamFeed');
    const segmentation = document.getElementById('segmentation');

    // 웹캠 피드 URL 설정
    webcamFeed.src = '/video_feed';

    // 초기 세그멘테이션 이미지 숨기기
    segmentation.style.display = 'none';

    searchButton.addEventListener('click', searchObject);

    function searchObject() {
        const text = sourceText.value;
        if (text) {
            // 검색 시작 메시지 표시
            result.innerHTML = `"${text}" 물체를 검색 중입니다...`;
            
            // 서버로 검색 요청 보내기
            fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text }),
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
                result.innerHTML = "검색 중 오류가 발생했습니다.";
                segmentation.style.display = 'none';
            });
        } else {
            result.innerHTML = "검색할 물체를 입력하세요.";
            segmentation.style.display = 'none';
        }
    }
});
