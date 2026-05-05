// IMAGE LOADING PLACEHOLDER
document.addEventListener("DOMContentLoaded", function () {
  const images = document.querySelectorAll('img');
  images.forEach(img => {
    if (img.complete) {
      img.classList.add('loaded');
    } else {
      img.addEventListener('load', () => img.classList.add('loaded'));
      img.addEventListener('error', () => img.classList.add('loaded'));
    }
  });
});

// backtotop.js
window.onscroll = function() {
  const btn = document.getElementById("backToTop");
  if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
    btn.style.display = "block";
  } else {
    btn.style.display = "none";
  }
};

document.addEventListener("DOMContentLoaded", function() {
  const btn = document.getElementById("backToTop");
  if (btn) {
    btn.addEventListener("click", function(e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
});

// footer ads slide down
function closeFooterAd() {
  const ad = document.getElementById('sticky-footer-ad');
  ad.style.transform = 'translateY(100%)'; // slides down
}