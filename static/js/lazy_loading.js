/* ================================================= */
/* ===== VIBENATION UNIVERSAL LAZY LOADER ======= */
/* ================================================= */

(function() {
    let imageObserver;

    // 1. Function to prepare and observe an image
    const applyLazyLoading = (img) => {
        // Skip if already processed or has no src
        if (img.classList.contains("lazy") || !img.src || img.src.startsWith('data:')) return;

        // Move current src to data-src
        img.dataset.src = img.src;

        // If it's below the immediate screen, swap with placeholder
        if (img.getBoundingClientRect().top > window.innerHeight) {
            img.src = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==";
        }

        img.classList.add("lazy");
        
        if (imageObserver) {
            imageObserver.observe(img);
        } else {
            // Fallback for very old browsers
            img.loading = "lazy";
            img.src = img.dataset.src;
        }
    };

    document.addEventListener("DOMContentLoaded", function() {
        // 2. Initialize the IntersectionObserver
        if ("IntersectionObserver" in window) {
            imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.classList.add("loaded"); // Useful for CSS fade-ins
                        }
                        observer.unobserve(img);
                    }
                });
            }, { rootMargin: "300px 0px" }); // Preload 300px before they appear
        }

        // 3. Process existing images on page load
        document.querySelectorAll("img[src]").forEach(applyLazyLoading);

        // 4. THE SECRET SAUCE: MutationObserver
        // This watches the entire page for new elements (like AJAX comments)
        const layoutObserver = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) { // If it's an element
                        // Check if the node itself is an image
                        if (node.tagName === "IMG") applyLazyLoading(node);
                        // Also check for images inside the new node (like inside a comment div)
                        node.querySelectorAll("img").forEach(applyLazyLoading);
                    }
                });
            });
        });

        layoutObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
})();