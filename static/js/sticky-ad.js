document.addEventListener('DOMContentLoaded', () => {

  // ----- Header Ad (scrolls with page) -----
  const headerAd = document.getElementById('header-ad');
  const closeHeader = document.getElementById('close-header-ad');
  if (headerAd && closeHeader) {
    closeHeader.addEventListener('click', () => {
      headerAd.style.transform = 'translateY(-100%)'; // slide up
      setTimeout(() => { headerAd.style.display = 'none'; }, 500); // match CSS transition
    });
  }

  // ----- Footer Ad (sticky) -----
  const footerAd = document.getElementById('footer-ad');
  const closeFooter = document.getElementById('close-footer-ad');
  if (footerAd && closeFooter) {
    closeFooter.addEventListener('click', () => {
      footerAd.style.transform = 'translateY(100%)'; // slide down
      setTimeout(() => {
        footerAd.style.display = 'none';
        const main = document.getElementById('main-content');
        if(main) main.style.paddingBottom = '0'; // remove extra padding
      }, 500);
    });
  }

});
