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
    function injectWithAnimation(container, html, isReply = false) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;

        const newItems = Array.from(tempDiv.children);

        newItems.forEach(item => {
            // prevent duplicates
            if (item.id && document.getElementById(item.id)) return;

            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';

            if (isReply) {
                // For nested comment threads, append natively to the bottom
                container.appendChild(item);
            } else {
                const titleHeading = container.querySelector('.vn-comments-title');
                if (titleHeading) {
                    titleHeading.insertAdjacentElement('afterend', item);
                } else {
                    container.prepend(item);
                }
            }
            
            item.offsetHeight; // Force browser layout execution to trigger transitions cleanly

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

                    // Pagination appends older items down to the bottom loop feed safely
                    if (data.html) injectWithAnimation(container, data.html, true);

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
        const offset = container ? container.querySelectorAll('.reply-item').length : 0;

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

                if (data.html && container) {
                    injectWithAnimation(container, data.html, true);
                }

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

    /* ================= DYNAMIC ASYNC POST (NO REFRESH / NO SPLASH) ================= */
    const postForm = document.querySelector('.vn-comment-form');

    if (postForm) {
        postForm.addEventListener('submit', function(e) {
            e.preventDefault(); 

            const btn = this.querySelector('.vn-comment-submit');
            if (!btn) return;

            if (btn.dataset.submitting === 'true') return;
            btn.dataset.submitting = 'true';

            const originalBtnHtml = btn.innerHTML;
            btn.innerHTML = '<span class="loading-spinner"></span> POSTING...';
            btn.style.pointerEvents = 'none';
            btn.style.opacity = '0.7';

            const formData = new FormData(this);
            const actionUrl = this.getAttribute('action') || window.location.pathname;

            fetch(actionUrl, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json().then(data => ({ status: response.status, body: data })))
            .then(res => {
                if (res.status === 200 && res.body.status === "success") {
                    
                    let targetContainer;
                    const isReply = !!res.body.parent_id;

                    if (isReply) {

                        // Root parent comment container
                        targetContainer = document.getElementById(
                            `reply-container-${res.body.root_comment_id}`
                        );

                        // First reply ever under this thread
                        if (!targetContainer) {

                            const rootCommentBlock = document.getElementById(
                                `comment-${res.body.root_comment_id}`
                            );

                            if (rootCommentBlock) {

                                let repliesWrapper =
                                    rootCommentBlock.querySelector('.comment-replies');

                                if (!repliesWrapper) {
                                    repliesWrapper = document.createElement('div');
                                    repliesWrapper.className = 'comment-replies';
                                    rootCommentBlock.appendChild(repliesWrapper);
                                }

                                targetContainer = document.createElement('div');
                                targetContainer.id =
                                    `reply-container-${res.body.root_comment_id}`;

                                repliesWrapper.appendChild(targetContainer);
                            }
                        }

                        // Emergency fallback
                        if (!targetContainer) {
                            targetContainer =
                                document.getElementById('main-comments-container');
                        }
                    } else {
                        targetContainer = document.getElementById('main-comments-container');
                    }

                    if (targetContainer) {
                        // Clear out the "No comments yet" message if it exists
                        const emptyMsg = targetContainer.querySelector('.no-comments-msg');
                        if (emptyMsg) emptyMsg.remove();

                        // Inject the new comment HTML cleanly using our fixed function
                        if (res.body.html) {
                            injectWithAnimation(targetContainer, res.body.html, isReply);
                        }
                    }
                    
                    // Capture incoming background signature state before running form clear
                    const newCommenterName = res.body.commenter_name;
                    const nameInput = postForm.querySelector('input[name="name"]') || postForm.querySelector('#id_name');
                    const internalParentInput = document.getElementById('parent_id');
                    const internalTextArea = postForm.querySelector('textarea');
                    const internalCancelBtn = document.getElementById('cancel-reply-btn');

                    // Reset form and UI states
                    postForm.reset(); 
                    if (internalParentInput) internalParentInput.value = "";
                    if (internalTextArea) internalTextArea.placeholder = "Write your comment...";
                    if (internalCancelBtn) internalCancelBtn.style.display = 'none';

                    // Force input assignment outside the browser's form reset thread loop
                    if (nameInput && newCommenterName) {
                        setTimeout(() => {
                            nameInput.setAttribute('value', newCommenterName);
                            nameInput.value = newCommenterName;
                        }, 10);
                    }

                } else {
                    alert(res.body.message || "Submission parameter failure.");
                }
            })
            .catch(err => {
                console.error("Comment submission execution error:", err);
                alert("Network communication drop encountered. Please try again.");
            })
            .finally(() => {
                btn.dataset.submitting = 'false';
                btn.innerHTML = originalBtnHtml;
                btn.style.pointerEvents = 'auto';
                btn.style.opacity = '';
            });
        });
    }

});
}