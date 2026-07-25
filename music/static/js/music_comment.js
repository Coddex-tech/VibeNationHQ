/* ================================================= */
/* ===== VIBENATION MUSIC COMMENT ENGINE =========== */
/* ================================================= */
const csrfToken = getCSRFToken();

function getCSRFToken() {
    return document
        .querySelector(
            'meta[name="csrf-token"]'
        )
        ?.content;
}

if (!window.musicCommentsInitialized) {

    window.musicCommentsInitialized = true;

    function handleReplyClick(id, name) {

        const parentInput = document.getElementById("parent_id");
        const replyingInput = document.getElementById("replying_to_name");
        const textarea = document.getElementById("comment-content");
        const cancelBtn = document.getElementById("cancel-reply-btn");

        if (!textarea) return;

        if (parentInput) {
            parentInput.value = id;
        }

        if (replyingInput) {
            replyingInput.value = name;
        }

        textarea.placeholder = `Replying to @${name}...`;

        if (cancelBtn) {
            cancelBtn.style.display = "inline-block";
        }

        textarea.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

        setTimeout(() => {

            textarea.focus();

            textarea.style.boxShadow =
                "0 0 15px rgba(29,191,115,.4)";

            setTimeout(() => {
                textarea.style.boxShadow = "";
            }, 1200);

        }, 300);

    }

    document.addEventListener("click", function (e) {

        /* Reply button */

        const replyBtn = e.target.closest(".reply-btn");

        if (replyBtn) {

            e.preventDefault();

            handleReplyClick(
                replyBtn.dataset.id,
                replyBtn.dataset.name
            );

            return;

        }

        /* Cancel reply */

        if (!e.target.matches("#cancel-reply-btn")) {
            return;
        }

        e.preventDefault();

        const parentInput = document.getElementById("parent_id");
        const replyingInput = document.getElementById("replying_to_name");
        const textarea = document.getElementById("comment-content");

        if (parentInput) {
            parentInput.value = "";
        }

        if (replyingInput) {
            replyingInput.value = "";
        }

        if (textarea) {
            textarea.placeholder = "Write your comment...";
        }

        e.target.style.display = "none";

    });


    function startLoading(btn) {

        if (!btn) return "";

        const original = btn.innerHTML;

        btn.disabled = true;

        btn.innerHTML =
            `<span class="loading-spinner"></span> POSTING...`;

        return original;

    }


    function stopLoading(btn, original) {

        if (!btn) return;

        btn.disabled = false;
        btn.innerHTML = original;

    }


    document.addEventListener("submit", async function (e) {

        const form = e.target.closest(".vn-comment-form");

        if (!form) return;

        e.preventDefault();

        const btn = form.querySelector(".vn-comment-submit");
        const original = startLoading(btn);

        try {

            const action =
                form.getAttribute("action") || window.location.href;
            const response = await fetch(action, {

                method: "POST",

                body: new FormData(form),

                credentials: "same-origin",

                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": csrfToken,
                }

            });

            let data = {};

            try {

                data = await response.json();

            }

            catch {

                data = {};

            }

            if (!response.ok) {

                throw new Error(
                    data.message || "Unable to post."
                );

            }

            document.dispatchEvent(

                new CustomEvent("music-comment-posted", {
                    detail: data
                })

            );

            const savedName = data.commenter_name;

            form.reset();

            if (savedName) {

                const input =
                    form.querySelector("#comment-name");

                if (input) {
                    input.value = savedName;
                }

            }

            const parentInput =
                document.getElementById("parent_id");

            const replyingInput =
                document.getElementById("replying_to_name");

            const textarea =
                document.getElementById("comment-content");

            const cancelBtn =
                document.getElementById("cancel-reply-btn");

            if (parentInput) {
                parentInput.value = "";
            }

            if (replyingInput) {
                replyingInput.value = "";
            }

            if (textarea) {
                textarea.placeholder = "Write your comment...";
            }

            if (cancelBtn) {
                cancelBtn.style.display = "none";
            }

        }

        catch (err) {

            console.error(err);

            alert(err.message || "Unable to post your comment.");

        }

        finally {

            stopLoading(btn, original);

        }

    });

}