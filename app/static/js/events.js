addEvent('DOMContentLoaded', document, function() {
    var activityContainer = document.getElementById('activity-feed-container');

    if (!activityContainer) {
        console.error('Activity feed container not found!');
        return;
    }

    var statusText = document.createElement('p');
    statusText.textContent = 'Connecting to activity feed...';
    statusText.id = 'status-text';
    activityContainer.appendChild(statusText);
});