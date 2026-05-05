document.querySelectorAll('.slider-wrapper').forEach(wrapper => {
  const container = wrapper.querySelector('.slider-container');
  const prevBtn = wrapper.querySelector('.prev');
  const nextBtn = wrapper.querySelector('.next');

  const buttonScroll = 240; // scroll per button click
  const wheelSpeed = 100;      // trackpad speed multiplier
  const dragSpeed = 2;       // drag/touch speed multiplier

  // ===== Button navigation =====
  prevBtn.addEventListener('click', () => {
    container.scrollBy({ left: -buttonScroll, behavior: 'smooth' });
  });

  nextBtn.addEventListener('click', () => {
    container.scrollBy({ left: buttonScroll, behavior: 'smooth' });
  });

  // ===== Trackpad / mousewheel horizontal scrolling =====
  container.addEventListener('wheel', (e) => {
    // Only handle horizontal scroll (ignore vertical)
    if (e.deltaX === 0) return;
    e.preventDefault();
    container.scrollLeft += e.deltaX * wheelSpeed;
  }, { passive: false });

  // ===== Mouse drag / touch swipe =====
  let isDown = false;
  let startX;
  let scrollLeft;

  // Mouse drag
  container.addEventListener('mousedown', (e) => {
    isDown = true;
    startX = e.pageX - container.offsetLeft;
    scrollLeft = container.scrollLeft;
  });

  container.addEventListener('mouseleave', () => isDown = false);
  container.addEventListener('mouseup', () => isDown = false);

  container.addEventListener('mousemove', (e) => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - container.offsetLeft;
    const walk = (x - startX) * dragSpeed;
    container.scrollLeft = scrollLeft - walk;
  });

  // Touch swipe (for touchscreen)
  container.addEventListener('touchstart', (e) => {
    startX = e.touches[0].pageX - container.offsetLeft;
    scrollLeft = container.scrollLeft;
  });

  container.addEventListener('touchmove', (e) => {
    const x = e.touches[0].pageX - container.offsetLeft;
    const walk = (x - startX) * dragSpeed;
    container.scrollLeft = scrollLeft - walk;
  });
});
