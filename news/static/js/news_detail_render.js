/**
 * VibeNation Decoupled Engine - News Detail Hydrator
 */
document.addEventListener('DOMContentLoaded', () => {
    const pathParts = window.location.pathname.split('/').filter(Boolean);
    const currentSlug = pathParts[pathParts.length - 1];

    if (!currentSlug) {
        console.error("Could not parse a valid slug from the current URL routing path.");
        return;
    }

    hydrateArticleContent(currentSlug);
    hydrateSidebarData();
    hydrateRecentSongs();
    setupCommentFormInterception(currentSlug);
});

function hydrateArticleContent(slug) {
    fetch(`/api/news/${slug}/`)
        .then(res => {
            if (!res.ok) throw new Error("Article data communication drop.");
            return res.json();
        })
        .then(data => {
            document.title = `${data.title} | VibeNation`;
            const metaHook = document.getElementById('meta-title-hook');
            if (metaHook) metaHook.textContent = data.title;
            
            document.getElementById('article-headline').textContent = data.title;
            document.getElementById('article-author').textContent = data.author.first_name ? `${data.author.first_name} ${data.author.last_name}` : data.author.username;
            document.getElementById('article-date').textContent = data.friendly_date;
            document.getElementById('article-core-body').innerHTML = data.article_content;

            const mainImg = document.getElementById('article-main-image');
            if (data.thumbnail_url) {
                mainImg.src = data.thumbnail_url;
                mainImg.alt = data.title;
                mainImg.style.display = 'block';
            }
            if (data.image_caption) {
                document.getElementById('article-image-caption').textContent = data.image_caption;
            }

            if (data.is_sponsored) {
                document.getElementById('sponsored-badge-shell').style.display = 'block';
            }

            const categoryBox = document.getElementById('detail-category-bar-box');
            if (data.category && data.category.length > 0) {
                categoryBox.innerHTML = data.category.map(cat => `
                    <a href="/news/category/${cat.slug}/" class="main-cat-pill">${cat.name.toUpperCase()}</a>
                `).join('');
            }

            const tagsBox = document.getElementById('article-tags-box');
            if (data.tags && data.tags.length > 0) {
                tagsBox.innerHTML = data.tags.map(tag => `
                    <a href="/news/tags/${tag.toLowerCase().replace(/\s+/g, '-')}/" class="tag">${tag}</a>
                `).join('');
            } else {
                tagsBox.innerHTML = `<p style="color: teal;">No related topics yet.</p>`;
            }

            hydrateCommentsSection(data.comments, data.total_comments, slug);
            buildShareRail(data.title);
        })
        .catch(err => {
            console.error("Hydration execution error:", err);
            document.getElementById('article-core-body').innerHTML = `
                <p style="color: red; text-align: center;">Failed to render article. Please check your network connection.</p>
            `;
        });
}

function buildCommentElementHtml(item, isReply = false) {
    const isStaff = item.is_verified_staff === true;
    const name = item.display_name || "Anonymous Fan";
    const initials = name.charAt(0).toUpperCase();
    
    const staffEntryClass = isStaff ? 'staff-entry' : '';
    const staffAvatarClass = isStaff ? 'staff-avatar' : '';
    const staffBadge = isStaff ? '<span class="badge-crew">STAFF</span>' : '';

    const parentAuthorName = item.replying_to || "";
    const mentionHtml = (isReply && parentAuthorName) 
        ? `<span class="reply-mention" style="color: #1dbf73; font-weight: 600; margin-right: 4px;">@${parentAuthorName}</span>` 
        : '';

    const replyTrigger = `href="javascript:void(0)" class="vn-reply-trigger-btn" onclick="window.handleReplyClick(${item.id}, '${name}')"`;

    if (isReply) {
        return `
            <div class="reply-item ${staffEntryClass}" id="reply-node-${item.id}">
                <div class="comment-left">
                    <div class="comment-avatar ${staffAvatarClass}">${initials}</div>
                </div>
                <div class="comment-center">
                    <div class="reply-label">REPLY</div>
                    <strong class="comment-author">${name} ${staffBadge}</strong>
                    <p class="comment-text">${mentionHtml}${item.content}</p>
                    <div class="comment-meta">
                        <span>${item.friendly_date || 'Just now'}</span>
                        <a ${replyTrigger}><i class="fa-solid fa-reply"></i> Reply</a>
                    </div>
                </div>
            </div>
        `;
    } else {
        const totalReplies = parseInt(item.total_replies_count) || 0;
        const initialRepliesLoaded = item.replies ? item.replies.length : 0;
        const remainingOnInitialLoad = totalReplies - initialRepliesLoaded;
        const hasMoreReplies = remainingOnInitialLoad > 0;

        const seeMoreBtnHtml = hasMoreReplies ? `
            <button class="load-more-replies-btn" data-comment-id="${item.id}" style="margin: 10px 0 10px 55px; background: none; border: none; color: #1dbf73; font-weight: 600; cursor: pointer;">
                See More Replies (${remainingOnInitialLoad})
            </button>
        ` : '';

        return `
            <div class="comment-item ${staffEntryClass}" id="comment-node-${item.id}">
                <div class="comment-left">
                    <div class="comment-avatar ${staffAvatarClass}">${initials}</div>
                </div>
                <div class="comment-center">
                    <strong class="comment-author">${name} ${staffBadge}</strong>
                    <p class="comment-text">${item.content}</p>
                    <div class="comment-meta">
                        <span>${item.friendly_date || 'Just now'}</span>
                        <a ${replyTrigger}><i class="fa-solid fa-reply"></i> Reply</a>
                    </div>
                    <div class="comment-replies" id="reply-container-${item.id}"></div>
                    ${seeMoreBtnHtml}
                </div>
            </div>
        `;
    }
}

function hydrateCommentsSection(comments, totalComments, slug) {
    const commentsContainer = document.getElementById('main-comments-container');
    const titleHeader = document.getElementById('main-comments-header-title');
    const mainPaginationWrapper = document.getElementById('load-more-comments-wrapper');
    const mainPaginationBtn = document.getElementById('load-more-comments-btn');

    if (!commentsContainer) return;

    if (comments && comments.length > 0) {
        if (titleHeader) titleHeader.textContent = `All Comments (${totalComments})`;
        commentsContainer.innerHTML = '';
        
        comments.forEach(comment => {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = buildCommentElementHtml(comment, false);
            const commentNode = tempDiv.firstElementChild;
            commentsContainer.appendChild(commentNode);

            if (comment.replies && comment.replies.length > 0) {
                const replyContainer = commentNode.querySelector(`#reply-container-${comment.id}`);
                if (replyContainer) {
                    comment.replies.forEach(reply => {
                        replyContainer.innerHTML += buildCommentElementHtml(reply, true);
                    });
                }
            }
        });

        if (mainPaginationBtn && mainPaginationWrapper) {
            mainPaginationBtn.setAttribute('data-url', `/news/${slug}/comments/`);
            mainPaginationWrapper.style.display = 'block';
        }
    } else {
        if (titleHeader) titleHeader.textContent = 'All Comments (0)';
        commentsContainer.innerHTML = `
            <div class="no-comments-msg">
                <p>No comments yet. Be the first to share your thoughts on this!</p>
            </div>
        `;
        if (mainPaginationWrapper) mainPaginationWrapper.style.display = 'none';
    }
}

function setReplyTarget(parentId, authorName) {
    const parentInput = document.getElementById('parent_id');
    const commentInput = document.getElementById('id_content');
    const cancelBtn = document.getElementById('cancel-reply-btn');

    if (parentInput && commentInput) {
        parentInput.value = parentId;
        commentInput.placeholder = `Replying to @${authorName}...`;
        if (cancelBtn) cancelBtn.style.display = 'inline-block';

        commentInput.scrollIntoView({ behavior: 'smooth', block: 'center' });

        setTimeout(() => {
            commentInput.focus();
        }, 600);
    }
}

function setupCommentFormInterception(currentSlug) {
    document.getElementById('cancel-reply-btn')?.addEventListener('click', function() {
        document.getElementById('parent_id').value = '';
        this.style.display = 'none';
        document.getElementById('id_content').placeholder = 'Write your comment...';
    });

    const form = document.getElementById('api-comment-form');
    if (!form) return;

    const newForm = form.cloneNode(true);
    form.parentNode.replaceChild(newForm, form);

    newForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const submitBtn = this.querySelector('.vn-comment-submit');
        if (submitBtn.disabled) return;

        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'POSTING...';
        submitBtn.disabled = true;

        const formData = new FormData(this);
        const actionUrl = this.getAttribute('action') || window.location.pathname;

        fetch(actionUrl, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => {
            if (!res.ok) throw new Error("Processing logic failed.");
            return res.json();
        })
        .then(data => {
            if (data.status === 'success' && data.comment_data) {
                const commentPayload = data.comment_data;

                this.reset();
                document.getElementById('parent_id').value = '';
                const cancelBtn = document.getElementById('cancel-reply-btn');
                if (cancelBtn) cancelBtn.style.display = 'none';
                document.getElementById('id_content').placeholder = 'Write your comment...';
                
                const emptyMsg = document.querySelector('.no-comments-msg');
                if (emptyMsg) emptyMsg.remove();

                const rawParentId = commentPayload.parent_id || commentPayload.parent;
                const isReply = !!rawParentId;

                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = buildCommentElementHtml(commentPayload, isReply);
                const newDomElement = tempDiv.firstElementChild;
                newDomElement.classList.add('new-comment-reveal');

                const commentsList = document.getElementById('main-comments-container');

                if (isReply) {
                    let rootCommentId = commentPayload.root_comment_id || commentPayload.root_id;
                    
                    if (!rootCommentId) {
                        const directParentNode = document.getElementById(`reply-node-${rawParentId}`) || document.getElementById(`comment-node-${rawParentId}`);
                        if (directParentNode) {
                            const rootBlock = directParentNode.closest('.comment-item') || directParentNode;
                            rootCommentId = rootBlock.id.replace('comment-node-', '');
                        } else {
                            rootCommentId = rawParentId;
                        }
                    }

                    let replyContainer = document.getElementById(`reply-container-${rootCommentId}`);
                    
                    if (!replyContainer) {
                        const rootBlock = document.getElementById(`comment-node-${rootCommentId}`);
                        if (rootBlock) {
                            replyContainer = document.createElement('div');
                            replyContainer.className = 'comment-replies';
                            replyContainer.id = `reply-container-${rootCommentId}`;
                            rootBlock.querySelector('.comment-center').appendChild(replyContainer);
                        }
                    }
                    if (replyContainer) {
                        replyContainer.appendChild(newDomElement);
                    }
                } else {
                    if (commentsList) {
                        commentsList.prepend(newDomElement);
                    }
                }

                const titleHeader = document.getElementById('main-comments-header-title');
                if (commentsList && titleHeader) {
                    const currentTotalCount = commentsList.querySelectorAll('.comment-item').length;
                    titleHeader.textContent = `All Comments (${currentTotalCount})`;
                }

                const nameInput = this.querySelector('input[name="name"]') || this.querySelector('#id_name');
                if (nameInput && commentPayload.display_name) {
                    nameInput.value = commentPayload.display_name;
                }
            } else {
                alert(data.message || "Error saving comment.");
            }
        })
        .catch(err => {
            console.error(err);
            alert("Network error. Please try again.");
        })
        .finally(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    });
}

window.buildCommentElementHtml = buildCommentElementHtml;
window.setReplyTarget = setReplyTarget;

function hydrateSidebarData() {
    fetch('/api/news/layout/sidebar/')
        .then(res => res.json())
        .then(data => {
            const trendingBox = document.getElementById('sidebar-trending-box');
            if (data.trending_news && data.trending_news.length > 0) {
                trendingBox.innerHTML = data.trending_news.map((item, index) => `
                    <div class="trending-item">
                        <a href="${item.absolute_url}" class="trending-link">
                            <span class="rank-number">${index + 1}</span>
                            <div class="trending-text">
                                <h4>${item.title}</h4>
                            </div>
                            <div class="trending-img-container">
                                <img loading="lazy" src="${item.thumbnail_url || ''}" alt="${item.title}">
                            </div>
                        </a>
                    </div>
                `).join('');

                const tickerBox = document.getElementById('dynamic-ticker-box');
                if (tickerBox) {
                    tickerBox.innerHTML = data.trending_news.map(item => `
                        <a href="${item.absolute_url}" style="margin-right: 50px; color: #fff; text-decoration: none; font-weight: 500;">
                            ${item.title.toUpperCase()} •
                        </a>
                    `).join('');
                }
            } else {
                trendingBox.innerHTML = `
                <p> No popular stories this week </p>
                `
            }

            const categoriesBox = document.getElementById('sidebar-categories-box');
            if (data.all_categories && data.all_categories.length > 0) {
                categoriesBox.innerHTML = data.all_categories.map(cat => `
                    <a href="/news/category-list/${cat.slug}/" class="cat-tag">
                        ${cat.name} <span class="cat-count">${cat.news_count || 0}</span>
                    </a>
                `).join('');
            }
        })
        .catch(err => console.error(err));
}

function hydrateRecentSongs() {
    fetch('/api/news/layout/recent-songs/')
        .then(res => res.json())
        .then(songs => {
            const songGrid = document.getElementById('mini-song-grid-box');
            if (songs && songs.length > 0 && songGrid) {
                songGrid.innerHTML = songs.map(song => `
                    <a href="${song.absolute_url}" class="mini-song-card">
                        <img loading="lazy" src="${song.cover_url || '/static/images/default_cover.png'}" alt="${song.title}">
                        <span>${song.artists ? song.artists.join(', ') : 'VibeNation Artist'} - ${song.title}</span>
                    </a>
                `).join('');
            }
        })
        .catch(err => console.error(err));
}

function buildShareRail(title) {
    const encodedUrl = encodeURIComponent(window.location.href);
    const encodedTitle = encodeURIComponent(title);
    const rail = document.getElementById('dynamic-share-rail');
    if (!rail) return;

    rail.innerHTML = `
        <a href="https://api.whatsapp.com/send?text=${encodedTitle}%20${encodedUrl}" target="_blank" class="whatsapp" aria-label="Share on WhatsApp"><i class="fab fa-whatsapp"></i></a>
        <a href="https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}" target="_blank" class="twitter" aria-label="Share on X"><i class="fa-brands fa-x-twitter"></i></a>
        <a href="https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}" target="_blank" class="facebook" aria-label="Share on Facebook"><i class="fab fa-facebook-f"></i></a>
        <a href="https://t.me/share/url?url=${encodedUrl}" target="_blank" class="telegram" aria-label="Share on Telegram"><i class="fab fa-telegram-plane"></i></a>
    `;
}