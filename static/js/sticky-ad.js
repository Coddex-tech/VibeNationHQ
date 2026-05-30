document.addEventListener('DOMContentLoaded', () => {

  // ----- Header Ad -----
  const headerAd = document.getElementById('header-ad');
  const closeHeader = document.getElementById('close-header-ad');

  if (headerAd && closeHeader) {

    closeHeader.addEventListener('click', () => {

      headerAd.classList.add('closed');

      setTimeout(() => {
        headerAd.style.display = 'none';
      }, 550);

    });

  }

  // ----- Footer Ad -----
  const footerAd = document.getElementById('footer-ad');
  const closeFooter = document.getElementById('close-footer-ad');

  if (footerAd && closeFooter) {

    closeFooter.addEventListener('click', () => {

      footerAd.classList.add('closed');

      setTimeout(() => {

        footerAd.style.display = 'none';

        const main = document.getElementById('main-content');

        if (main) {
          main.style.paddingBottom = '0';
        }

      }, 550);

    });

  }

});