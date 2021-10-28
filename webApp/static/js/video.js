var video = document.getElementById("headervid");
var image = document.getElementById("headerimg");

video.addEventListener('ended', function(){
  video.style.display = "none";
  image.style.display = "block";
});




//Get the button
var mybutton = document.getElementById("upbutton");

// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function() {scrollFunction()};

function scrollFunction() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    mybutton.style.display = "inline-flex";
  } else {
    mybutton.style.display = "none";
  }
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}
