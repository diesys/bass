let tracklist = document.querySelector('#tracklist')

// sets the custom (if set) theme (dark/light)
if (typeof theme !== 'undefined') {
    document.querySelector('body').classList.remove('dark');
    document.querySelector('body').classList.remove('light');
    document.querySelector('body').classList.add(theme);
}

// sets the custom (if set) numbering to track list order
if (typeof first_track !== 'undefined') {
    tracklist.setAttribute('start', first_track);
}

// array contains everything needed
album.forEach(function (track) {
    let li = document.createElement('li');
    li.innerHTML += track.title;
    li.classList.add('track');
    li.setAttribute('data-audiosrc', track.path);
    tracklist.appendChild(li);
});

// Pure JS simple click (entry) and play (audiosrc) player UI
function playTrack(entry) {
    document.querySelectorAll('.track').forEach(element => {
        element.classList.remove('active');
    }); entry.classList.add('active');

    var player = document.querySelector('#player>audio');
    var playing = document.querySelector('#player>#now_playing');

    player.setAttribute('src', entry.getAttribute('data-audiosrc'));
    player.play();
    playing.innerHTML = entry.innerHTML;
}

// binds click on tracks title to the function above
document.querySelectorAll('.track').forEach(element => {
    element.addEventListener('click', function() {
        playTrack(element);
    });
});