// The poster is a local image, so the page contacts YouTube only after you press play.
// Without JavaScript the poster is just a link to the video.
document.querySelectorAll(".video").forEach(function (box) {
  var link = box.querySelector(".video-play");
  link.addEventListener("click", function (e) {
    e.preventDefault();
    var frame = document.createElement("iframe");
    frame.src = "https://www.youtube-nocookie.com/embed/" + box.dataset.videoId + "?autoplay=1&rel=0";
    frame.title = "tokensaver in 10 seconds";
    frame.allow = "autoplay; encrypted-media; picture-in-picture";
    frame.allowFullscreen = true;
    box.replaceChild(frame, link);
  });
});
