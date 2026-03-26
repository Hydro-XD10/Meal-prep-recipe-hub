document.addEventListener("DOMContentLoaded", () => {
    const actionForms = document.querySelectorAll(".js-recipe-action");

    const updateButtonState = (form, actionType, isActive) => {
        const button = form.querySelector('[data-role="action-button"]');
        if (!button) {
            return;
        }

        if (actionType === "favourite") {
            button.textContent = isActive ? "♥ Unfavourite" : "♡ Favourite";
            button.className = `btn w-100 ${isActive ? "btn-danger" : "btn-outline-danger"}`;
        } else if (actionType === "like") {
            button.textContent = isActive ? "👍 Unlike" : "👍 Like";
            button.className = `btn w-100 ${isActive ? "btn-primary" : "btn-outline-primary"}`;
        }
    };

    actionForms.forEach((form) => {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const csrfTokenInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
            const csrfToken = csrfTokenInput ? csrfTokenInput.value : "";
            const actionType = form.dataset.actionType;

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest",
                    },
                });

                if (!response.ok) {
                    throw new Error(`Request failed with status ${response.status}`);
                }

                const data = await response.json();
                const isActive = data.active;

                form.dataset.active = String(isActive);
                form.action = isActive ? form.dataset.removeUrl : form.dataset.addUrl;
                updateButtonState(form, actionType, isActive);

                const favouriteCount = document.getElementById("favourite-count");
                const likeCount = document.getElementById("like-count");

                if (favouriteCount) {
                    favouriteCount.textContent = data.favourite_count;
                }

                if (likeCount) {
                    likeCount.textContent = data.like_count;
                }
            } catch (_error) {
                form.submit();
            }
        });
    });
});
