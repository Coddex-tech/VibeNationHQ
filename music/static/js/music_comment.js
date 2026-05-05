/* ================================================= */
/* ===== DEDICATED MUSIC COMMENT JS ======= */
/* ================================================= */

function handleReplyClick(id, name) {
    const parentInput = document.getElementById('parent_id');
    const textArea = document.querySelector('.vn-comment-form textarea');
    const cancelBtn = document.getElementById('cancel-reply-btn');
    
    if (parentInput && textArea) {
        parentInput.value = id;
        textArea.placeholder = `Replying to @${name.toUpperCase()}...`;
        
        // 1. SHOW the cancel button
        if (cancelBtn) cancelBtn.style.display = 'inline-block';

        textArea.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(() => {
            textArea.focus();
            textArea.style.boxShadow = '0 0 15px rgba(29, 191, 115, 0.4)';
            setTimeout(() => { textArea.style.boxShadow = ''; }, 1500);
        }, 600);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    
    // --- 0. CANCEL REPLY LOGIC ---
    const cancelBtn = document.getElementById('cancel-reply-btn');
    const parentInput = document.getElementById('parent_id');
    const textArea = document.querySelector('.vn-comment-form textarea');

    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            // Reset hidden input so it's a normal comment again
            if (parentInput) parentInput.value = "";
            // Reset placeholder text
            if (textArea) textArea.placeholder = "Write your comment...";
            // Hide the cancel button
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

    // --- 1. MUSIC MAIN COMMENTS ---
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
                    this.innerHTML = "LOAD MORE COMMENTS";
                    this.style.pointerEvents = 'auto';
                    if (!data.has_more) this.remove();
                });
        });
    }

    // --- 2. MUSIC REPLIES ---
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('load-more-replies-btn')) {
            const btn = e.target;
            const commentId = btn.dataset.commentId;
            const container = document.getElementById(`reply-container-${commentId}`);
            const offset = container.querySelectorAll('.reply-item').length;
            
            const baseUrl = btn.dataset.url;
            const fetchUrl = `${baseUrl}?offset=${offset}`;

            btn.innerHTML = '<span class="loading-spinner"></span> LOADING...';
            btn.style.pointerEvents = 'none';

            fetch(fetchUrl)
                .then(res => {
                    if(!res.ok) throw new Error("Music URL not found");
                    return res.json();
                })
                .then(data => {
                    if (data.html) injectWithAnimation(container, data.html);
                    btn.innerHTML = "See More Replies";
                    btn.style.pointerEvents = 'auto';
                    if (!data.has_more) btn.remove();
                })
                .catch(err => {
                    console.error("Fetch error:", err);
                    btn.innerHTML = "Error Loading";
                    btn.style.pointerEvents = 'auto';
                });
        }
    });

    // --- 3. MUSIC POST SPINNER ---
    const postForm = document.querySelector('.vn-comment-form');
    if (postForm) {
        postForm.addEventListener('submit', function() {
            const btn = this.querySelector('.vn-comment-submit');
            if (btn) {
                // Injects the spinner and changes text to "POSTING..."
                btn.innerHTML = '<span class="loading-spinner"></span> POSTING...';
                btn.style.pointerEvents = 'none';
                btn.style.opacity = '0.7';
            }
        });
    }
});