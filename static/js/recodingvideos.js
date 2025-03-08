// 문서가 로드되면 비디오를 가져오는 함수 호출
document.addEventListener("DOMContentLoaded", function() {
    fetchVideos();
});

// 비디오 데이터를 가져오는 함수
function fetchVideos() {
    fetch('/api/videos')
        .then(response => {
            if (!response.ok) {
                throw new Error('네트워크 응답이 올바르지 않습니다');
            }
            return response.json();
        })
        .then(data => updateTable(data))
        .catch(error => console.error('fetch 작업에서 문제가 발생했습니다:', error));
}

// 테이블을 업데이트하는 함수
function updateTable(videos) {
    const tbody = document.querySelector("tbody");
    tbody.innerHTML = ""; // 기존 테이블 행 제거

    videos.forEach(video => {
        const row = document.createElement("tr");
        const dateCell = document.createElement("td");
        const timeCell = document.createElement("td");
        const videoCell = document.createElement("td");
        const videoLink = document.createElement("a");

        dateCell.textContent = video.date;
        timeCell.textContent = video.time;
        videoLink.href = video.url;
        videoLink.textContent = "Watch Video";

        videoCell.appendChild(videoLink);
        row.appendChild(dateCell);
        row.appendChild(timeCell);
        row.appendChild(videoCell);

        tbody.appendChild(row);
    });
}

// 페이지 이동을 위한 함수
function navigateTo(page) {
    window.location.href = page;
}
