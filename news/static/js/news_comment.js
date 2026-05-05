/* ================================================= */
/* ===== VIBENATION FINAL INTERACTIVE JS ======= */
/* ================================================= */

function handleReplyClick(id, name) {
    const parentInput = document.getElementById('parent_id');
    const textArea = document.querySelector('.vn-comment-form textarea');
    const cancelBtn = document.getElementById('cancel-reply-btn'); // Found it!
    
    if (parentInput && textArea) {
        parentInput.value = id;
        textArea.placeholder = `Replying to @${name.toUpperCase()}...`;
        
        // 1. Show the cancel button when reply is clicked
        if (cancelBtn) cancelBtn.style.display = 'inline-block';

        textArea.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });

        setTimeout(() => {
            textArea.focus();
            textArea.style.boxShadow = '0 0 15px rgba(29, 191, 115, 0.4)';
            textArea.style.transition = 'box-shadow 0.3s ease';
            setTimeout(() => {
                textArea.style.boxShadow = '';
            }, 1500);
        }, 600); 
    }
}

document.addEventListener('DOMContentLoaded', function() {
    
    // --- CANCEL REPLY LOGIC ---
    const cancelBtn = document.getElementById('cancel-reply-btn');
    const parentInput = document.getElementById('parent_id');
    const textArea = document.querySelector('.vn-comment-form textarea');

    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            // Reset the form state
            if (parentInput) parentInput.value = ""; 
            if (textArea) textArea.placeholder = "Write your comment...";
            // Hide the cancel button again
            this.style.display = 'none';
        });
    }

    function injectWithAnimation(container, html) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        const newItems = Array.from(tempDiv.children);
        
        newItems.forEach(item => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            container.appendChild(item);
            item.offsetHeight; 

            requestAnimationFrame(() => {
                item.classList.add('new-comment-reveal');
                item.style.opacity = '';
                item.style.transform = '';
            });
        });
    }

    const postForm = document.querySelector('.vn-comment-form');
    if (postForm) {
        postForm.addEventListener('submit', function() {
            const btn = this.querySelector('.vn-comment-submit');
            btn.innerHTML = '<span class="loading-spinner"></span> POSTING...';
            btn.style.pointerEvents = 'none';
            btn.style.opacity = '0.7';
        });
    }

    const mainBtn = document.getElementById('load-more-comments-btn');
    if (mainBtn) {
        mainBtn.addEventListener('click', function() {
            const container = document.getElementById('main-comments-container');
            const offset = container.querySelectorAll(':scope > .comment-item').length;
            
            this.innerHTML = '<span class="loading-spinner"></span> LOADING...';
            this.style.pointerEvents = 'none';

            fetch(`${this.dataset.url}?offset=${offset}`)
                .then(res => res.json())
                .then(data => {
                    if (data.html) injectWithAnimation(container, data.html);
                    this.innerHTML = "Load More Comments";
                    this.style.pointerEvents = 'auto';
                    if (!data.has_more) this.remove();
                });
        });
    }

    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('load-more-replies-btn')) {
            const btn = e.target;
            const commentId = btn.dataset.commentId;
            const container = document.getElementById(`reply-container-${commentId}`);
            const offset = container.querySelectorAll('.reply-item').length;

            btn.innerHTML = '<span class="loading-spinner"></span> LOADING...';
            btn.style.pointerEvents = 'none';

            // Check if button has a specific data-url, otherwise use default
            const url = btn.dataset.url ? `${btn.dataset.url}?offset=${offset}` : `/load-more-replies/${commentId}/?offset=${offset}`;

            fetch(url)
                .then(res => res.json())
                .then(data => {
                    if (data.html) injectWithAnimation(container, data.html);
                    btn.innerHTML = "See More Replies";
                    btn.style.pointerEvents = 'auto';
                    if (!data.has_more) btn.remove();
                });
        }
    });
});