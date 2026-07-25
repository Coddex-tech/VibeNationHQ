/* ===== INTERACTIVE CHUNKS PAGINATION ENGINE ======= */
if (!window.newsCommentsInitialized) {
window.newsCommentsInitialized = true;

window.handleReplyClick = function(id, name) {
    if (typeof window.setReplyTarget === 'function') {
        window.setReplyTarget(id, name);
    }
};

document.addEventListener('DOMContentLoaded', function() {

    // Internal robust injector tied directly to window.buildCommentElementHtml
    function injectReplyChunk(container, replyObject) {
        if (typeof window.buildCommentElementHtml !== 'function') return;
        
        // Match the true exact layout schema from news_detail_render.js
        const htmlContent = window.buildCommentElementHtml(replyObject, true);
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = htmlContent.trim();
        const itemNode = tempDiv.firstElementChild;

        // Verify it doesn't already exist in DOM to prevent duplicate renders
        if (itemNode && !document.getElementById(itemNode.id)) {
            itemNode.style.opacity = '0';
            itemNode.style.transform = 'translateY(10px)';
            itemNode.style.transition = 'all 0.3s ease-in-out';
            
            container.appendChild(itemNode);

            // Trigger animation frame layout render
            itemNode.offsetHeight; 
            requestAnimationFrame(() => {
                itemNode.style.opacity = '1';
                itemNode.style.transform = 'translateY(0)';
            });
        }
    }

    /* ================= MAIN COMMENTS CHUNK PAGINATION ================= */
    const mainBtn = document.getElementById('load-more-comments-btn');
    if (mainBtn) {
        mainBtn.addEventListener('click', function() {
            if (this.dataset.loading === 'true') return;
            this.dataset.loading = 'true';

            const container = document.getElementById('main-comments-container');
            const offset = container.querySelectorAll('.comment-item').length;
            const baseUrl = this.getAttribute('data-url');

            this.innerHTML = '<span class="loading-spinner"></span> LOADING...';
            
            fetch(`${baseUrl}?offset=${offset}`)
                .then(res => res.json())
                .then(data => {
                    const results = data.results || [];
                    results.forEach(comment => {
                        if (typeof window.buildCommentElementHtml === 'function') {
                            const html = window.buildCommentElementHtml(comment, false);
                            const tempDiv = document.createElement('div');
                            tempDiv.innerHTML = html.trim();
                            const commentNode = tempDiv.firstElementChild;
                            if (commentNode && !document.getElementById(commentNode.id)) {
                                container.appendChild(commentNode);
                            }
                        }
                    });

                    if (!data.has_more) {
                        const wrapper = document.getElementById('load-more-comments-wrapper');
                        if (wrapper) wrapper.remove();
                        this.remove();
                    } else {
                        this.textContent = "Load More Comments";
                    }
                })
                .catch(err => {
                    console.error("Comments chunk error:", err);
                    this.textContent = "Load More Comments";
                })
                .finally(() => { this.dataset.loading = 'false'; });
        });
    }

    /* ================= NESTED REPLIES CHUNK PAGINATION ================= */
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.load-more-replies-btn');
        if (!btn) return;

        if (btn.dataset.loading === 'true') return;
        btn.dataset.loading = 'true';

        const commentId = btn.dataset.commentId;
        const container = document.getElementById(`reply-container-${commentId}`);
        
        // This targets class="reply-item" elements exactly as returned by buildCommentElementHtml
        const offset = container ? container.querySelectorAll('.reply-item').length : 0;

        console.log(`[VibeNation Log] Fetching replies for comment ${commentId} starting from offset: ${offset}`);

        btn.innerHTML = '<span class="loading-spinner"></span> LOADING REPLIES...';

        fetch(`/comments/${commentId}/replies/?offset=${offset}`)
            .then(res => res.json())
            .then(data => {
                const results = data.results || [];
                
                if (container && results.length > 0) {
                    results.forEach(reply => {
                        injectReplyChunk(container, reply);
                    });
                }

                // Recalculate accurately based on the updated DOM query selection matching .reply-item
                const totalLoadedNow = container ? container.querySelectorAll('.reply-item').length : 0;
                const grandTotalOnServer = parseInt(data.total_count) || totalLoadedNow;
                const remainingCount = grandTotalOnServer - totalLoadedNow;

                console.log(`[VibeNation Log] Rendered: ${totalLoadedNow} Total: ${grandTotalOnServer} Remaining: ${remainingCount}`);

                if (!data.has_more || remainingCount <= 0) {
                    btn.remove();
                } else {
                    btn.textContent = `See More Replies (${remainingCount})`;
                }
            })
            .catch(err => {
                console.error("Replies chunk execution error:", err);
                btn.textContent = "See More Replies";
            })
            .finally(() => { btn.dataset.loading = 'false'; });
    });
});
}