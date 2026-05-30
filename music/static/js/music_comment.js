/* ================================================= */
/* ===== MUSIC COMMENT ======= */
/* ================================================= */

if (!window.musicCommentsInitialized) {
window.musicCommentsInitialized = true;

/* =========================
   REPLY CLICK
========================= */
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

    /* =========================
       CANCEL REPLY
    ========================= */
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

    /* =========================
       SAFE INJECTION (NO DUPES)
    ========================= */
    function injectWithAnimation(container, html) {
        const temp = document.createElement('div');
        temp.innerHTML = html;

        Array.from(temp.children).forEach(item => {

            if (item.id && document.getElementById(item.id)) {
                return; // prevent duplicates
            }

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

    /* =========================
       GLOBAL SUBMIT GUARD
       (THIS FIXES YOUR ENTER BUG)
    ========================= */
    let isSubmitting = false;

    const postForm = document.querySelector('.vn-comment-form');

    if (postForm) {

        postForm.addEventListener('submit', function(e) {

            // 🚨 BLOCK MULTIPLE ENTER / DOUBLE SUBMIT
            if (isSubmitting) {
                e.preventDefault();
                return;
            }

            isSubmitting = true;

            const btn = this.querySelector('.vn-comment-submit');

            if (btn) {
                btn.disabled = true; // IMPORTANT (better than pointerEvents)
                btn.innerHTML = '<span class="loading-spinner"></span> POSTING...';
                btn.style.opacity = '0.7';
            }

            // SAFETY RESET (prevents permanent dead button)
            setTimeout(() => {
                isSubmitting = false;
                if (btn) {
                    btn.disabled = false;
                    btn.style.opacity = '1';
                }
            }, 8000);
        });
    }

    /* =========================
       LOAD MORE COMMENTS
    ========================= */
    const mainBtn = document.getElementById('load-more-comments-btn');

    if (mainBtn) {
        mainBtn.addEventListener('click', function() {

            if (this.dataset.loading === 'true') return;
            this.dataset.loading = 'true';

            const container = document.getElementById('main-comments-container');

            const offset = container.querySelectorAll(':scope > .comment-item').length;

            this.innerHTML = '<span class="loading-spinner"></span> LOADING...';
            this.disabled = true;

            fetch(`${this.dataset.url}?offset=${offset}`)
                .then(res => res.json())
                .then(data => {

                    if (data.html) injectWithAnimation(container, data.html);

                    if (!data.has_more) {
                        this.remove();
                    } else {
                        this.innerHTML = "LOAD MORE COMMENTS";
                        this.disabled = false;
                    }
                })
                .catch(err => {
                    console.error(err);
                    this.innerHTML = "LOAD MORE COMMENTS";
                    this.disabled = false;
                })
                .finally(() => {
                    this.dataset.loading = 'false';
                });
        });
    }

    /* =========================
       LOAD MORE REPLIES
    ========================= */
    document.addEventListener('click', function(e) {

        const btn = e.target.closest('.load-more-replies-btn');
        if (!btn) return;

        if (btn.dataset.loading === 'true') return;
        btn.dataset.loading = 'true';

        const commentId = btn.dataset.commentId;

        const container = document.getElementById(`reply-container-${commentId}`);

        const offset = container.querySelectorAll('.reply-item').length;

        const fetchUrl = `${btn.dataset.url}?offset=${offset}`;

        btn.innerHTML = '<span class="loading-spinner"></span> LOADING...';
        btn.disabled = true;

        fetch(fetchUrl)
            .then(res => res.json())
            .then(data => {

                if (data.html) injectWithAnimation(container, data.html);

                if (!data.has_more) {
                    btn.remove();
                } else {
                    btn.innerHTML = "See More Replies";
                    btn.disabled = false;
                }
            })
            .catch(err => {
                console.error(err);
                btn.innerHTML = "Error Loading";
                btn.disabled = false;
            })
            .finally(() => {
                btn.dataset.loading = 'false';
            });
    });

});
}