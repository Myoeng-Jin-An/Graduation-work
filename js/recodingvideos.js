function navigateTo(page) {
    window.location.href = page;
}

document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/videos') // Assuming there's an endpoint providing video data
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('videoTable').getElementsByTagName('tbody')[0];
            data.forEach(video => {
                const row = tableBody.insertRow();
                const dateCell = row.insertCell(0);
                const timeCell = row.insertCell(1);
                const videoCell = row.insertCell(2);

                dateCell.textContent = video.date; // Assuming video.date exists
                timeCell.textContent = video.time; // Assuming video.time exists
                videoCell.innerHTML = `<video controls src="${video.url}"></video>`; // Assuming video.url exists
            });
        })
        .catch(err => console.error('Error fetching video data:', err));
});

function navigateTo(page) {
    window.location.href = page;
}
