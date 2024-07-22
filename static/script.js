document.addEventListener('DOMContentLoaded', function() {
    const searchButton = document.getElementById('searchButton');
    const sourceText = document.getElementById('sourceText');
    const result = document.getElementById('result');
    const webcamFeed = document.getElementById('webcamFeed');

    // 웹캠 피드 URL 설정
    webcamFeed.src = '/video_feed';  // Flask 라우트에 맞게 조정

    searchButton.addEventListener('click', searchObject);

    function searchObject() {
        const text = sourceText.value;
        if (text) {
            // 여기에 실제 API 호출이나 처리 로직이 들어갑니다.
            const searchResult = processSearch(text);
            result.innerHTML = searchResult;
        } else {
            result.innerHTML = "검색할 물체를 입력하세요.";
        }
    }

    function processSearch(text) {
        // 이 함수는 실제 검색 로직으로 대체되어야 합니다.
        // 현재는 단순히 웹캠 이미지를 반환합니다.
        return `<img src="/video_feed" width="1024" height="800">`;
    }
});