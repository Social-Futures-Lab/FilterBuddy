

window.addEventListener('load', function () {
    var _ = dfc;
    getVideos().then(function (videosResp) {
        console.log(videosResp);
        if (videosResp.video.length === 0) {
            document.body.appendChild(_('div', {}, [_('', 'You have no videos :(')]));
        } else {
            videosResp.video.forEach(function (video) {
                var videoLink = _('a', {'href': 
                    'https://www.youtube.com/watch?v=' + video.videoId
                }, [_('', video.title)]);
                document.body.appendChild(_('div', {}, [videoLink]));
            });
        }
    })
});

function getVideos() {
    return fetch('/get_videos').then(function (resp) {
        return resp.json();
    });
}

function makeApiRequest(request) {
    return fetch('/api', {
        'method': 'POST',
        'body': JSON.stringify(request),
        'headers': {
            'Content-Type': 'application/json'
        }
    }).then(function (resp) {
        return resp.json();
    });
}
