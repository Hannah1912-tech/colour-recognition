document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    const colorName = document.getElementById('color_name');
    const colorPreview = document.getElementById('color_preview');
    const clearFocusButton = document.getElementById('clear_focus');

    // Access webcam
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
            return video.play();
        })
        .catch(err => {
            console.error("Error accessing webcam:", err);
            alert("Error accessing webcam. Please make sure you have a webcam connected and have granted permission to use it.");
        });

    video.addEventListener('click', function(e) {
        const rect = video.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Set canvas size to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Draw current video frame to canvas
        context.drawImage(video, 0, 0);
        
        // Get image data
        const imageData = canvas.toDataURL('image/jpeg');
        
        // Send to server for color detection
        fetch('/detect_color', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image: imageData,
                x: Math.round((x / rect.width) * video.videoWidth),
                y: Math.round((y / rect.height) * video.videoHeight)
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                colorName.textContent = 'Error: ' + data.error;
                return;
            }
            colorName.textContent = data.color_name;
            const [r, g, b] = data.rgb_color;
            colorPreview.style.backgroundColor = `rgb(${r},${g},${b})`;
        })
        .catch(error => {
            console.error('Error:', error);
            colorName.textContent = 'Error detecting color';
        });
    });

    clearFocusButton.addEventListener('click', function() {
        colorName.textContent = 'Click on video to detect color';
        colorPreview.style.backgroundColor = 'transparent';
    });
});