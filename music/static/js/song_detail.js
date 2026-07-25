/* ==========================================================
   VIBENATION MUSIC DETAIL PAGE
========================================================== */

const defaultCover = "/static/images/Media_cover_placeholder.webp";

const MusicPage = {

    commentsNextOffset: 0,

    hasMoreComments: false,

    payload: null,

    detail: null,

    isDJ: false,

    slug: null,

    apiURL: null,

    async init() {

        this.slug = this.getSlug();

        this.isDJ = window.location.pathname.includes("/mixtape/");

        this.apiURL = this.isDJ
            ? `/api/music/dj/${this.slug}/`
            : `/api/music/song/${this.slug}/`;

        try {

            const response = await fetch(this.apiURL);

            if (!response.ok) {
                throw new Error("Unable to load this page.");
            }

            this.payload = await response.json();



            this.detail = this.payload.detail;

            this.render();

        }

        catch (err) {

            console.error(err);

            this.renderError();

        }

    },

    getSlug() {

        const parts = window.location.pathname
            .split("/")
            .filter(Boolean);

        return parts[parts.length - 1];

    },

    render() {

        this.renderHeader();

        this.renderMidAd();

        this.renderCover();

        this.renderMeta();

        this.renderAudio();

        this.renderDownloadButton();

        this.renderSidebar();

        this.renderTags();

        this.renderArtists();

        this.renderRelatedSongs();

        this.renderInlineAd();

        this.renderLatestMusic();

        this.renderInlineAd();

        this.renderTrendingSongs();

        this.renderInlineAd();

        this.renderComments();

    },

    renderHeader() {

        const music = this.detail;

        const title = music.title;

        const artists = (music.artists || [])
            .map(artist => artist.name)
            .join(", ");

        const page = document.getElementById("music-detail-page");

        page.innerHTML = `
        <div class="song-detail-container">

            <div class="song-detail-content">

                <header class="song-header">

                    <h1 class="song-main-title">

                        ${title}

                        ${artists ? `
                            <span class="artist-sep"> - </span>

                            <span class="artist-list">
                                ${artists}
                            </span>
                        ` : ""}

                    </h1>

                    <p class="post-date">

                        <strong>

                            Posted ${music.friendly_date}

                        </strong>

                    </p>

                </header>

            </div>

        </div>
    `;

    },

    renderMidAd() {

        document.querySelector(".song-detail-content")
            .insertAdjacentHTML(
                "beforeend",
                `
            <div class="mid-ad">

            </div>
            `
            );

    },

    renderCover() {

        const music = this.detail;

        const image = music.media?.url || defaultCover;

        const alt = music.media?.alt || music.title;

        const container = document.querySelector(".song-detail-content");

        container.insertAdjacentHTML(
            "beforeend",
            `
        <div class="song-cover-wrapper">

            <img
                src="${image}"
                alt="${alt}"
                class="vibe-cover"
                loading="lazy"
            >

        </div>
        `
        );

    },

    renderMeta() {

        const music = this.detail;

        const artists = (music.artists || [])
            .map(artist => artist.name)
            .join(", ") || "VibeNation Artist";

        const genres = (music.genres || [])
            .map(genre => genre.name)
            .join(", ");

        document.querySelector(".song-detail-content")
            .insertAdjacentHTML(
                "beforeend",
                `
            <section class="song-info-meta">

                ${music.description ? `
                    <div class="song-description">
                        <p>${music.description}</p>
                    </div>
                ` : ""}

                <div class="metadata-grid">

                    <h4 class="action-call">
                        Listen and Download Below
                    </h4>

                    <p class="meta-row">
                        <span>Title:</span>
                        <strong>${music.title}</strong>
                    </p>

                    <p class="meta-row">
                        <span>Artist:</span>
                        <strong>${artists}</strong>
                    </p>

                    ${genres ? `
                        <p class="meta-row">
                            <span>Genre:</span>
                            <strong>${genres}</strong>
                        </p>
                    ` : ""}

                    <p class="meta-row">
                        <span>Duration:</span>
                        <strong>${music.duration || "N/A"}</strong>
                    </p>

                </div>

            </section>
            `
            );

    },

    renderAudio() {

        const music = this.detail;

        document.querySelector(".song-detail-content")
            .insertAdjacentHTML(
                "beforeend",
                `
            <div class="audio-player-vibe">

                ${music.audio
                    ? `
                        <audio controls class="vibe-audio">
                            <source src="${music.audio.url}" type="audio/mpeg">
                        </audio>
                        `
                    : `
                        <p class="no-audio">
                            Audio currently unavailable.
                        </p>
                        `
                }

            </div>
            `
            );

    },

    renderDownloadButton() {

        const music = this.detail;

        document.querySelector(".song-detail-content")
            .insertAdjacentHTML(
                "beforeend",
                `
            <div class="download-btn-container">

                <a
                    href="${music.download_url}"
                    class="vibe-download-btn"
                    download
                >
                    Download MP3
                </a>

            </div>
            `
            );

    },

    renderSidebar() { },

    renderTags() {

        const music = this.detail;

        const tags = music.tags || [];

        let html = `
        <div class="song-tags">

            <h3 style="color: teal;">Related topics:</h3>
    `;

        if (tags.length) {

            html += tags.map(tag => `
            <a href="${tag.url}" class="tag">
                ${tag.name}
            </a>
        `).join("");

        } else {

            html += `
            <p style="color: teal; text-decoration: none;">
                No related topic yet.
            </p>
        `;

        }

        html += `</div>`;

        document
            .getElementById("music-detail-page")
            .insertAdjacentHTML("beforeend", html);

    },

    renderArtists() {

        const artists = this.detail.artists || [];

        if (!artists.length) return;

        let html = `
        <div class="artist-section">

            <h3>
                ${this.isDJ ? "DJ Artist Info" : "Artist Info"}
            </h3>
    `;

        artists.forEach(artist => {

            html += `
            <div class="artist-bio" style="margin-bottom:15px;">

                <h3>${artist.name}</h3>

                <p class="paragraphs">
                    ${artist.bio || "No bio available"}
                </p>

            </div>
        `;

        });

        html += `</div>`;

        document
            .getElementById("music-detail-page")
            .insertAdjacentHTML("beforeend", html);

    },


    // ====================================
    // HELPER FOR ALL MUSIC CARD SECTIONS
    // ====================================
    renderMusicCards(title, items) {

        if (!items || !items.length) {
            return;
        }

        let html = `
        <h2 style="margin-top:30px;">
            ${title}
        </h2>

        <div class="card-container-grid">
    `;

        items.forEach(item => {

            const image = item.media?.url || defaultCover;

            const artists = (item.artists || [])
                .map(artist => artist.name)
                .join(", ");

            html += `
            <a class="card-link" href="${item.page_url}">

                <div class="card-thumb">

                    <img
                        loading="lazy"
                        src="${image}"
                        alt="${item.title}"
                    >

                </div>

                <div class="card-body">

                    <span class="tag-pill">

                        ${item.is_dj ? "Mixtape" : "Music"}

                    </span>

                    <h2 class="card-title">

                        ${item.title}

                        ${artists ? ` - ${artists}` : ""}

                    </h2>

                </div>

            </a>
        `;

        });

        html += `
        </div>
    `;

        document
            .getElementById("music-detail-page")
            .insertAdjacentHTML("beforeend", html);

    },

    renderRelatedSongs() {

        this.renderMusicCards(
            "RELATED SONGS",
            this.payload.related_songs
        );

    },

    renderInlineAd() { },

    renderLatestMusic() {

        const latest = [
            ...(this.payload.latest_songs || []),
            ...(this.payload.latest_mixtapes || [])
        ];

        latest.sort((a, b) => new Date(b.date) - new Date(a.date));

        this.renderMusicCards(
            "LATEST JAM",
            latest
        );

    },

    renderTrendingSongs() {

        this.renderMusicCards(
            "TRENDING SONGS",
            this.payload.trending_songs
        );

    },

    renderComments() {

        document
            .getElementById("music-detail-page")
            .insertAdjacentHTML(
                "beforeend",
                `
            <div class="comments-wrapper">

                <h3
                    class="vn-comments-title"
                    id="comments-title"
                >
                    Comments
                </h3>

                <form
                    method="post"
                    action="/api/music/${this.slug}/comment/"
                    class="vn-comment-form"
                >

                    <input
                        type="hidden"
                        id="parent_id"
                        name="parent_id"
                    >

                    <input
                        type="hidden"
                        id="replying_to_name"
                        name="replying_to_name"
                    >

                    <div class="form-group">

                        <label>Name</label>

                        <input
                            type="text"
                            name="name"
                            id="comment-name"
                        >

                    </div>

                    <div class="form-group">

                        <div
                            class="vn-hidden-field"
                            style="display:none !important;"
                        >
                            <input
                                type="text"
                                name="user_website"
                                autocomplete="off"
                                tabindex="-1"
                            >
                        </div>

                        <label>Comment</label>

                        <textarea
                            name="content"
                            id="comment-content"
                        ></textarea>

                    </div>

                    <div class="vn-form-actions">

                        <button
                            class="vn-comment-submit"
                            type="submit"
                        >
                            Post
                        </button>

                        <a
                            href="javascript:void(0)"
                            id="cancel-reply-btn"
                            class="vn-cancel-btn"
                            style="display:none;"
                        >
                            ✕ CANCEL REPLY
                        </a>

                    </div>

                </form>

                <div
                    class="vn-comments-list music-comments-list"
                    id="main-comments-container"
                >

                    <h3 class="vn-comments-title">
                        All Comments
                    </h3>

                </div>

                <div
                    id="load-more-comments-wrapper"
                    style="margin-top:20px;text-align:center;"
                ></div>

            </div>
            `
            );

        this.loadComments();

    },

    async loadComments(offset = 0) {

        const url =
            offset === 0
                ? `/api/music/${this.slug}/comments/`
                : `/api/music/${this.slug}/comments/?offset=${offset}`;

        const response = await fetch(url);

        if (!response.ok) {
            return;
        }

        const data = await response.json();

        const title = document.getElementById("comments-title");

        if (title && data.total_comments_count !== undefined) {

            title.textContent = `Comments (${data.total_comments_count})`;

        }

        const container =
            document.getElementById("main-comments-container");

        for (const comment of data.results) {

            if (document.getElementById(`comment-${comment.id}`)) {
                continue;
            }

            container.insertAdjacentHTML(
                "beforeend",
                this.renderSingleComment(comment)
            );

        }

        this.commentsNextOffset += data.results.length;

        this.hasMoreComments = data.has_more;

        const wrapper =
            document.getElementById(
                "load-more-comments-wrapper"
            );

        wrapper.innerHTML = "";

        if (data.has_more) {

            wrapper.innerHTML = `
            <button
                id="load-more-comments-btn"
                class="vn-comment-submit"
            >
                LOAD MORE COMMENTS
            </button>
        `;

            document
                .getElementById("load-more-comments-btn")
                .onclick = () => {

                    this.loadComments(
                        this.commentsNextOffset
                    );

                };

        }

    },

    renderSingleComment(comment) {

        const avatar = comment.is_verified_staff
            ? "VN"
            : comment.display_name.charAt(0).toUpperCase();

        const remainingReplies =
            comment.total_replies_count - (comment.replies?.length || 0);

        return `
        <div class="comment-item ${comment.is_verified_staff ? "staff-entry" : ""}" id="comment-${comment.id}">

            <div class="comment-left">

                <div class="comment-avatar ${comment.is_verified_staff ? "staff-avatar" : ""}">
                    ${avatar}
                </div>

            </div>

            <div class="comment-center">

                <p class="comment-author">

                    ${comment.display_name.toUpperCase()}

                    ${comment.is_verified_staff ? `
                        <span class="badge-crew">

                            <svg style="width:11px;height:11px;display:inline;margin-right:3px;vertical-align:middle;"
                                viewBox="0 0 24 24"
                                fill="currentColor">

                                <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>

                            </svg>

                            STAFF

                        </span>
                    ` : ""}

                </p>

                <p class="comment-text">
                    ${comment.content}
                </p>

                <div class="comment-meta">

                    <span>${comment.friendly_date}</span>

                    <a
                        href="javascript:void(0)"
                        class="reply-btn"
                        data-id="${comment.id}"
                        data-name="${comment.display_name}"
                    >
                        Reply
                    </a>

                </div>

                ${comment.total_replies_count
                ? `
                    <div
                        class="reply-count"
                        id="reply-count-${comment.id}"
                    >
                        ${comment.total_replies_count}
                        ${comment.total_replies_count === 1 ? "Reply" : "Replies"}
                    </div>
                    `
                : ""
            }

                <div class="comment-replies">

                    <div id="reply-container-${comment.id}" class="vn-comment-replies-list">
                        ${(comment.replies || [])
                .map(reply => this.renderSingleReply(reply))
                .join("")}
                    </div>

                    ${remainingReplies > 0
                ? `
                        <button
                            class="load-more-replies-btn"
                            data-comment-id="${comment.id}"
                        >
                            See More Replies (${remainingReplies})
                        </button>
                        `
                : ""
            }

                </div>

            </div>

        </div>
        `;
    },

    renderSingleReply(reply) {

        const avatar = reply.is_verified_staff
            ? "VN"
            : reply.display_name.charAt(0).toUpperCase();

        return `
    <div class="reply-item ${reply.is_verified_staff ? "staff-entry" : ""}" id="reply-${reply.id}">

        <div class="comment-left">

            <div class="comment-avatar ${reply.is_verified_staff ? "staff-avatar" : ""}">
                ${avatar}
            </div>

        </div>

        <div class="comment-center">

            <p class="comment-author">

                ${reply.display_name.toUpperCase()}

                ${reply.is_verified_staff ? `
                    <span class="badge-crew">

                        <svg
                            style="width:11px;height:11px;display:inline;margin-right:3px;vertical-align:middle;"
                            viewBox="0 0 24 24"
                            fill="currentColor">

                            <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>

                        </svg>

                        STAFF

                    </span>
                ` : ""}

            </p>

            ${reply.replying_to ? `
                <p class="reply-label">
                    Replying to
                    <span class="replying-to">
                        @${reply.replying_to.toUpperCase()}
                    </span>
                </p>
            ` : ""}

            <p class="comment-text">
                ${reply.content}
            </p>

            <div class="comment-meta">

                <span>${reply.friendly_date}</span>

                <a
                    href="javascript:void(0)"
                    class="reply-btn"
                    data-id="${reply.id}"
                    data-name="${reply.display_name}"
                >
                    Reply
                </a>

            </div>

        </div>

    </div>
    `;

    },

    async loadMoreReplies(commentId, btn) {

        const container =
            document.getElementById(`reply-container-${commentId}`);

        if (!container) return;

        const offset = container.children.length;
        const originalText = btn.textContent

        btn.disabled = true;
        btn.textContent = "Loading...";

        try {

            const response = await fetch(
                `/api/music/comments/${commentId}/replies/?offset=${offset}`
            );

            if (!response.ok) {
                throw new Error();
            }

            const data = await response.json();

            data.results.forEach(reply => {

                container.insertAdjacentHTML(
                    "beforeend",
                    this.renderSingleReply(reply)
                );

            });

            if (data.has_more) {

                btn.disabled = false;

                btn.textContent =
                    `See More Replies (${data.remaining_count})`;

            } else {

                btn.remove();

            }

        }

        catch {

            btn.disabled = false;
            btn.textContent = originalText;

        }

    },

    renderError() {

        document.body.innerHTML = `
            <div class="music-error">
                <h2>Unable to load this page.</h2>
            </div>
        `;

    }

};

document.addEventListener("DOMContentLoaded", () => {

    MusicPage.init();

    document.addEventListener("click", e => {

        const btn = e.target.closest(".load-more-replies-btn");

        if (!btn) return;

        MusicPage.loadMoreReplies(
            btn.dataset.commentId,
            btn
        );

    });

    document.addEventListener("music-comment-posted", () => {

        const container =
            document.getElementById("main-comments-container");

        const wrapper =
            document.getElementById("load-more-comments-wrapper");

        if (container) {

            container.innerHTML = '';

        }

        if (wrapper) {
            wrapper.innerHTML = "";
        }

        MusicPage.commentsNextOffset = 0;
        MusicPage.hasMoreComments = false;

        MusicPage.loadComments();

    });

});