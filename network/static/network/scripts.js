document.addEventListener("DOMContentLoaded", () => {
  // =========================
  // Like (Instagram style)
  // =========================
document.querySelectorAll(".like-heart").forEach((heart) => {
    heart.onclick = () => {
        const container = heart.closest(".like-container");
        const postId = container.dataset.postId;
        const countSpan = container.querySelector(".like-count");

        fetch(`/api/posts/${postId}/like/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/json",
            },
            body: JSON.stringify({}),
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) return console.error(data.error);

            if (data.liked) {
                heart.classList.add("liked");
                heart.innerText = "♡";
            } else {
                heart.classList.remove("liked");
                heart.innerText = "♡";
            }

            countSpan.innerText = data.likes_count;
        })
        .catch(err => console.error(err));
    };
});



  // =========================
  // Edit/Save/Cancel
  // =========================
  document.querySelectorAll(".edit-btn").forEach((button) => {
    button.onclick = () => {
      const postDiv = button.closest("[data-post-id]");
      const contentDiv = postDiv.querySelector(".post-content");
      const saveBtn = postDiv.querySelector(".save-btn");
      const cancelBtn = postDiv.querySelector(".cancel-btn");

      const textarea = document.createElement("textarea");
      textarea.className = "form-control mb-2";
      textarea.value = contentDiv.innerText.trim();
      const originalContent = contentDiv.innerText.trim();
      contentDiv.replaceWith(textarea);

      button.classList.add("d-none");
      saveBtn.classList.remove("d-none");
      cancelBtn.classList.remove("d-none");

      cancelBtn.onclick = () => {
        textarea.replaceWith(contentDiv);
        contentDiv.innerText = originalContent;
        button.classList.remove("d-none");
        saveBtn.classList.add("d-none");
        cancelBtn.classList.add("d-none");
      };

      saveBtn.onclick = () => {
        const newContent = textarea.value.trim();
        fetch(`/post/${postDiv.dataset.postId}`, {
          method: "PUT",
          headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ content: newContent }),
        })
          .then((res) => res.json())
          .then((data) => {
            if (data.error) return console.error(data.error);
            textarea.replaceWith(contentDiv);
            contentDiv.innerText = newContent;
            button.classList.remove("d-none");
            saveBtn.classList.add("d-none");
            cancelBtn.classList.add("d-none");
          });
      };
    };
  });

  // =========================
  // Comment placeholder
  // =========================
  document.querySelectorAll(".comment-btn").forEach((button) => {
    button.onclick = () => {
      alert("اضغط هنا لإضافة نافذة التعليق لاحقًا!");
    };
  });
});

// =========================
// CSRF token helper
// =========================
function getCSRFToken() {
  const cookies = document.cookie.split(";").map((c) => c.trim());
  for (let c of cookies) {
    if (c.startsWith("csrftoken=")) return decodeURIComponent(c.substring(10));
  }
  return null;
}
