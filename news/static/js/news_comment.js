/* ===== INTERACTIVE JS ======= */
if (!window.newsCommentsInitialized) {
window.newsCommentsInitialized = true;

function handleReplyClick(id, name) {
    const parentInput = document.getElementById('parent_id');
    const textArea = document.querySelector('.vn-comment-form textarea');
    const cancelBtn = document.getElementById('cancel-reply-btn');

    if (parentInput && textArea) {
        parentInput.value = id;
        textArea.placeholder = `Replying to @${name.toUpperCase()}...`;

        if (cancelBtn) cancelBtn.style.display = 'inline-block';

        textArea.scrollIntoView({ behavior: 'smooth', block: 'center' });

        setTimeout(() => {
            textArea.focus();
            textArea.style.boxShadow = '0 0 15px rgba(29, 191, 115, 0.4)';
            setTimeout(() => {
                textArea.style.boxShadow = '';
            }, 1500);
        }, 600);
    }
}

document.addEventListener('DOMContentLoaded', function() {

    /* ================= CANCEL REPLY ================= */
    const cancelBtn = document.getElementById('cancel-reply-btn');
    const parentInput = document.getElementById('parent_id');
    const textArea = document.querySelector('.vn-comment-form textarea');

    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            if (parentInput) parentInput.value = "";
            if (textArea) textArea.placeholder = "Write your comment...";
            this.style.display = 'none';
        });
    }

    /* ================= SAFE INJECT ================= */
    function injectWithAnimation(container, html) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;

        const newItems = Array.from(tempDiv.children);

        newItems.forEach(item => {

            // prevent duplicates
            if (item.id && document.getElementById(item.id)) return;

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

    /* ================= MAIN COMMENTS ================= */
    const mainBtn = document.getElementById('load-more-comments-btn');

    if (mainBtn) {
        mainBtn.addEventListener('click', function() {

            if (this.dataset.loading === 'true') return;
            this.dataset.loading = 'true';

            const container = document.getElementById('main-comments-container');
            const offset = container.querySelectorAll(':scope > .comment-item').length;

            this.innerHTML = '<span class="loading-spinner"></span> LOADING...';
            this.style.pointerEvents = 'none';

            fetch(`${this.dataset.url}?offset=${offset}`)
                .then(res => res.json())
                .then(data => {

                    if (data.html) injectWithAnimation(container, data.html);

                    if (!data.has_more) {
                        this.remove();
                    } else {
                        this.innerHTML = "Load More Comments";
                        this.style.pointerEvents = 'auto';
                    }
                })
                .catch(err => {
                    console.error(err);
                    this.innerHTML = "Load More Comments";
                    this.style.pointerEvents = 'auto';
                })
                .finally(() => {
                    this.dataset.loading = 'false';
                });
        });
    }

    /* ================= REPLIES ================= */
    document.addEventListener('click', function(e) {

        const btn = e.target.closest('.load-more-replies-btn');
        if (!btn) return;

        if (btn.dataset.loading === 'true') return;
        btn.dataset.loading = 'true';

        const commentId = btn.dataset.commentId;
        const container = document.getElementById(`reply-container-${commentId}`);
        const offset = container.querySelectorAll('.reply-item').length;

        const url = btn.dataset.url
            ? `${btn.dataset.url}?offset=${offset}`
            : `/load-more-replies/${commentId}/?offset=${offset}`;

        btn.innerHTML = '<span class="loading-spinner"></span> LOADING...';
        btn.style.pointerEvents = 'none';

        fetch(url)
            .then(res => {
                if (!res.ok) throw new Error("Request failed");
                return res.json();
            })
            .then(data => {

                if (data.html) injectWithAnimation(container, data.html);

                if (!data.has_more) {
                    btn.remove();
                } else {
                    btn.innerHTML = "See More Replies";
                    btn.style.pointerEvents = 'auto';
                }
            })
            .catch(err => {
                console.error("Reply error:", err);
                btn.innerHTML = "See More Replies";
                btn.style.pointerEvents = 'auto';
            })
            .finally(() => {
                btn.dataset.loading = 'false';
            });
    });

    /* ================= POST SPINNER ================= */
    const postForm = document.querySelector('.vn-comment-form');

    if (postForm) {
        postForm.addEventListener('submit', function(e) {

            const btn = this.querySelector('.vn-comment-submit');

            if (btn) {
                // prevent double submit (ENTER spam fix)
                if (btn.dataset.submitting === 'true') {
                    e.preventDefault();
                    return;
                }

                btn.dataset.submitting = 'true';

                btn.innerHTML = '<span class="loading-spinner"></span> POSTING...';
                btn.style.pointerEvents = 'none';
                btn.style.opacity = '0.7';
            }
        });
    }

});
}