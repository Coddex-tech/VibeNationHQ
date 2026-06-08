/* ================================================= */
/* ===== VIBENATION MUSIC COMMENT PIPELINE ENGINE == */
/* ================================================= */

if (!window.musicCommentsInitialized) {
    window.musicCommentsInitialized = true;

    /* ==============================================
       REPLY OPERATION TRIGGER HOOK
    ============================================== */
    window.handleReplyClick = function(id, name) {
        const parentInput = document.getElementById('parent_id');
        const replyingToInput = document.getElementById('replying_to_name'); // Target the new field
        const textArea = document.querySelector('.vn-comment-form textarea') || document.querySelector('.vn-comment-form [name="content"]');
        const cancelBtn = document.getElementById('cancel-reply-btn');

        if (parentInput && textArea) {
            parentInput.value = id;
            if (replyingToInput) replyingToInput.value = name; // Store the exact name clicked
            
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
    };

    document.addEventListener('DOMContentLoaded', function() {

        /* ==============================================
           CANCEL REPLY PIPELINE DE-ESCALATION
        ============================================== */
        const cancelBtn = document.getElementById('cancel-reply-btn');
        const parentInput = document.getElementById('parent_id');
        const replyingToInput = document.getElementById('replying_to_name');
        const textArea = document.querySelector('.vn-comment-form textarea') || document.querySelector('.vn-comment-form [name="content"]');

        if (cancelBtn) {
            cancelBtn.addEventListener('click', function() {
                if (parentInput) parentInput.value = "";
                if (replyingToInput) replyingToInput.value = "";
                if (textArea) textArea.placeholder = "Write your comment...";
                this.style.display = 'none';
            });
        }

        /* ==============================================
           ANIMATED DOM INJECTION ARCHITECTURE (NO DUPES)
        ============================================== */
        function injectWithAnimation(container, html, isReply = false) {
            const temp = document.createElement('div');
            temp.innerHTML = html;

            Array.from(temp.children).forEach(item => {
                if (item.id && document.getElementById(item.id)) {
                    return; 
                }

                item.style.opacity = '0';
                item.style.transform = 'translateY(20px)';

                if (isReply) {
                    container.appendChild(item);
                } else {
                    const titleHeading = container.querySelector('.vn-comments-title');
                    if (titleHeading) {
                        titleHeading.insertAdjacentElement('afterend', item);
                    } else {
                        container.prepend(item);
                    }
                }

                item.offsetHeight; 

                requestAnimationFrame(() => {
                    item.classList.add('new-comment-reveal');
                    item.style.opacity = '';
                    item.style.transform = '';
                });
            });
        }

        /* ==============================================
           DYNAMIC ASYNC POST FORM INTERCEPTOR (AJAX)
        ============================================== */
        let isSubmitting = false;
        const postForm = document.querySelector('.vn-comment-form');

        if (postForm) {
            postForm.addEventListener('submit', function(e) {
                e.preventDefault(); 

                if (isSubmitting) return;
                isSubmitting = true;

                const btn = this.querySelector('.vn-comment-submit');
                const originalBtnHtml = btn ? btn.innerHTML : 'Post';

                if (btn) {
                    btn.disabled = true; 
                    btn.innerHTML = '<span class="loading-spinner"></span> POSTING...';
                    btn.style.opacity = '0.7';
                }

                const formData = new FormData(this);
                const actionUrl = this.getAttribute('action') || window.location.pathname;
                const csrfTokenElement = this.querySelector('[name=csrfmiddlewaretoken]');
                const csrfToken = csrfTokenElement ? csrfTokenElement.value : '';

                fetch(actionUrl, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": csrfToken
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(errData => {
                            throw new Error(errData.message || `Server error status: ${response.status}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === "success") {
                        let targetContainer;
                        const isReply = !!data.parent_id;

                        if (isReply) {
                            targetContainer = document.getElementById(`reply-container-${data.parent_id}`);
                            
                            if (!targetContainer) {
                                const parentCommentBlock = document.getElementById(`comment-${data.parent_id}`);
                                if (parentCommentBlock) {
                                    targetContainer = document.createElement('div');
                                    targetContainer.id = `reply-container-${data.parent_id}`;
                                    targetContainer.className = 'vn-comment-replies-list';
                                    parentCommentBlock.appendChild(targetContainer);
                                } else {
                                    targetContainer = document.getElementById('main-comments-container');
                                }
                            }
                        } else {
                            targetContainer = document.getElementById('main-comments-container');
                        }

                        if (targetContainer) {
                            const emptyMsg = targetContainer.querySelector('.no-comments-msg') || 
                                             (targetContainer.parentNode ? targetContainer.parentNode.querySelector('.no-comments-msg') : null);
                            if (emptyMsg) emptyMsg.remove();

                            if (isReply) {
                                const rootId = data.parent_id;

                                fetch(`${window.location.origin}/music/load-more-replies/${rootId}?offset=0`)
                                    .then(res => res.json())
                                    .then(replyData => {
                                        const container = document.getElementById(`reply-container-${rootId}`);

                                        if (container && replyData.html) {
                                            container.innerHTML = "";
                                            container.insertAdjacentHTML("beforeend", replyData.html);
                                        }
                                    })
                                    .catch(err => console.error("Reply refresh failed:", err));

                            } else {
                                injectWithAnimation(targetContainer, data.html, false);
                            }
                        }

                        // Capture identity requirements before executing reset
                        const newCommenterName = data.commenter_name;
                        const nameInput = postForm.querySelector('input[name="name"]') || postForm.querySelector('#id_name');

                        postForm.reset();
                        if (parentInput) parentInput.value = "";
                        if (replyingToInput) replyingToInput.value = "";
                        if (textArea) textArea.placeholder = "Write your comment...";
                        if (cancelBtn) cancelBtn.style.display = 'none';

                        // Force input override assignment outside the native form reset microtask sequence
                        if (nameInput && newCommenterName) {
                            setTimeout(() => {
                                nameInput.setAttribute('value', newCommenterName);
                                nameInput.value = newCommenterName;
                            }, 10);
                        }

                    } else {
                        alert(data.message || "Submission validation failure.");
                    }
                })
                .catch(err => {
                    console.error("Music comment post pipeline exception:", err);
                    alert(err.message || "Network communication issue. Please check your connection.");
                })
                .finally(() => {
                    isSubmitting = false;
                    if (btn) {
                        btn.disabled = false;
                        btn.innerHTML = originalBtnHtml;
                        btn.style.opacity = '1';
                    }
                });
            });
        }

        /* ==============================================
           LOAD MORE ROOT PAYLOAD COMMENTS 
        ============================================== */
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
                        if (data.html) injectWithAnimation(container, data.html, false);

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

        /* ==============================================
           DYNAMIC EVENT DELEGATION: LOAD MORE REPLIES
        ============================================== */
        document.addEventListener('click', function(e) {
            const btn = e.target.closest('.load-more-replies-btn');
            if (!btn) return;

            if (btn.dataset.loading === 'true') return;
            btn.dataset.loading = 'true';

            const commentId = btn.dataset.commentId;
            const container = document.getElementById(`reply-container-${commentId}`);
            const offset = container ? container.querySelectorAll('.reply-item').length : 0;

            const fetchUrl = `${btn.dataset.url}?offset=${offset}`;

            btn.innerHTML = '<span class="loading-spinner"></span> LOADING...';
            btn.disabled = true;

            fetch(fetchUrl)
                .then(res => res.json())
                .then(data => {
                    if (data.html && container) {
                        injectWithAnimation(container, data.html, true);
                    }

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