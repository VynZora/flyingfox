document.addEventListener("DOMContentLoaded", function () {
  const config = window.FLYING_FOX_CHATBOT || {};

  const chatbotToggle = document.getElementById("ffChatbotToggle");

  const chatbotWindow = document.getElementById("ffChatbotWindow");

  const chatbotClose = document.getElementById("ffChatbotClose");

  const chatbotForm = document.getElementById("ffChatbotForm");

  const chatbotInput = document.getElementById("ffChatbotInput");

  const chatbotSend = document.getElementById("ffChatbotSend");

  const chatbotMessages = document.getElementById("ffChatbotMessages");

  /* =========================================
   LANGUAGE OPTIONS
========================================= */

  const languageOptionsContainer = document.getElementById(
    "chatbotLanguageOptions",
  );

  const languageButtons = document.querySelectorAll(".chatbot-language-btn");

  const quickRepliesContainer = document.getElementById(
    "ffChatbotQuickReplies",
  );

  const quickReplyButtons = document.querySelectorAll(
    ".ff-chatbot-quick-button",
  );

  const notificationBadge = document.querySelector(".ff-chatbot-alert");

  let chatbotInitialized = false;

  if (
    !chatbotToggle ||
    !chatbotWindow ||
    !chatbotForm ||
    !chatbotInput ||
    !chatbotMessages
  ) {
    return;
  }

  /* =========================================
           CSRF COOKIE
        ========================================= */

  function getCookie(name) {
    const cookies = document.cookie.split(";").map(function (cookie) {
      return cookie.trim();
    });

    const targetCookie = cookies.find(function (cookie) {
      return cookie.startsWith(name + "=");
    });

    if (!targetCookie) {
      return "";
    }

    return decodeURIComponent(targetCookie.substring(name.length + 1));
  }

  /* =========================================
           SAFE HTML
        ========================================= */

  function escapeHtml(value) {
    const element = document.createElement("div");

    element.textContent = value == null ? "" : String(value);

    return element.innerHTML;
  }

  /* =========================================
           CURRENT TIME
        ========================================= */

  function getCurrentTime() {
    return new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  /* =========================================
           SCROLL TO LAST MESSAGE
        ========================================= */

  function scrollToBottom() {
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  }

  /* =========================================
           SHOW / HIDE QUICK REPLIES
        ========================================= */

  function setQuickRepliesVisible(visible) {
    if (!quickRepliesContainer) {
      return;
    }

    quickRepliesContainer.hidden = !visible;
  }

  /* =========================================
         SHOW / HIDE LANGUAGE OPTIONS
========================================= */

  function setLanguageOptionsVisible(visible) {
    if (!languageOptionsContainer) {
      return;
    }

    languageOptionsContainer.style.display = visible ? "grid" : "none";

    /*
     * User should not type until a
     * language has been selected.
     */
    chatbotInput.disabled = visible;

    if (chatbotSend) {
      chatbotSend.disabled = visible;
    }

    if (visible) {
      chatbotInput.placeholder = "Please select a language first";
    } else {
      chatbotInput.placeholder = "Type your message...";
    }
  }

  /* =========================================
           ADD MESSAGE
        ========================================= */

  function addMessage(message, sender, action, isError) {
    const wrapper = document.createElement("div");

    wrapper.className =
      "ff-chatbot-message " +
      (sender === "user" ? "ff-user-message" : "ff-bot-message");

    if (isError) {
      wrapper.classList.add("ff-chatbot-error");
    }

    let actionHtml = "";

    if (action && action.text && action.url) {
      actionHtml = `

                    <a
                        href="${escapeHtml(action.url)}"
                        class="ff-chatbot-action-button"
                    >
                        ${escapeHtml(action.text)}

                        <i class="fas fa-arrow-right"></i>
                    </a>
                `;
    }

    wrapper.innerHTML = `

                ${
                  sender === "bot"
                    ? `
                            <div class="ff-message-avatar">
                                <i class="fas fa-robot"></i>
                            </div>
                        `
                    : ""
                }

                <div class="ff-message-body">

                    <div class="ff-message-bubble">
                        ${escapeHtml(message)}
                    </div>

                    ${actionHtml}

                    <span class="ff-message-time">
                        ${getCurrentTime()}
                    </span>

                </div>
            `;

    chatbotMessages.appendChild(wrapper);

    scrollToBottom();
  }

  /* =========================================
           TYPING INDICATOR
        ========================================= */

  function showTypingIndicator() {
    removeTypingIndicator();

    const typing = document.createElement("div");

    typing.id = "ffChatbotTyping";

    typing.className = "ff-chatbot-message ff-bot-message";

    typing.innerHTML = `

                <div class="ff-message-avatar">
                    <i class="fas fa-paw"></i>
                </div>

                <div class="ff-message-body">

                    <div class="
                        ff-message-bubble
                        ff-chatbot-typing
                    ">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>

                </div>
            `;

    chatbotMessages.appendChild(typing);

    scrollToBottom();
  }

  function removeTypingIndicator() {
    const typing = document.getElementById("ffChatbotTyping");

    if (typing) {
      typing.remove();
    }
  }

  /* =========================================
           LOADING STATE
        ========================================= */

  function setLoading(isLoading) {
    chatbotInput.disabled = isLoading;

    if (chatbotSend) {
      chatbotSend.disabled = isLoading;
    }
  }

  async function selectChatbotLanguage(languageCode, languageName) {
    if (!config.messageUrl) {
      console.error("Chatbot message URL is missing.");
      return;
    }

    /*
     * Immediately hide the language buttons
     * so they cannot be clicked multiple times.
     */
    setLanguageOptionsVisible(false);

    /*
     * Show the selected language as a user message.
     */
    addMessage(languageName, "user");

    /*
     * Show bot typing animation.
     */
    showTypingIndicator();

    try {
      const response = await fetch(config.messageUrl, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest",
        },

        body: JSON.stringify({
          message: languageCode,
          language: languageCode,
        }),
      });

      const contentType = response.headers.get("content-type") || "";

      if (!contentType.includes("application/json")) {
        const htmlResponse = await response.text();

        console.error("Chatbot HTML response:", htmlResponse);

        throw new Error("Chatbot server returned an invalid response.");
      }

      const data = await response.json();

      removeTypingIndicator();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Unable to select language.");
      }

      /*
       * Display translated bot response.
       *
       * Example Malayalam:
       * "കൊള്ളാം! ആരംഭിക്കുന്നതിന് മുമ്പ്,
       * നിങ്ങളുടെ മുഴുവൻ പേര് അറിയാമോ?"
       */
      addMessage(data.response, "bot");

      /*
       * Django normally returns false here because
       * language selection has finished.
       */
      setLanguageOptionsVisible(data.show_language_options === true);

      /*
       * Quick replies stay hidden while collecting
       * name / phone / email.
       */
      setQuickRepliesVisible(data.show_quick_replies === true);

      /*
       * Enable the message box again.
       */
      chatbotInput.disabled = false;

      if (chatbotSend) {
        chatbotSend.disabled = false;
      }

      chatbotInput.placeholder = "Type your message...";

      /*
       * Put cursor in message input.
       */
      chatbotInput.focus();
    } catch (error) {
      removeTypingIndicator();

      console.error("Language selection error:", error);

      addMessage(
        error.message || "Unable to select language.",
        "bot",
        null,
        true,
      );

      /*
       * If selection failed,
       * show language buttons again.
       */
      setLanguageOptionsVisible(true);
    }
  }

  /* =========================================
           INITIALIZE CHATBOT
        ========================================= */

  async function initializeChatbot() {
    if (chatbotInitialized) {
      return;
    }

    if (!config.initializeUrl) {
      addMessage("Chatbot initialize URL is missing.", "bot", null, true);

      return;
    }

    showTypingIndicator();

    try {
      const response = await fetch(config.initializeUrl, {
        method: "GET",

        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      const contentType = response.headers.get("content-type") || "";

      if (!contentType.includes("application/json")) {
        const htmlResponse = await response.text();

        console.error("Chatbot HTML response:", htmlResponse);

        throw new Error(
          "Chatbot server returned HTML. " + "Check the Django terminal.",
        );
      }

      const data = await response.json();

      removeTypingIndicator();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Unable to start chatbot.");
      }

      /*
       * Remove the static welcome message
       * from the HTML.
       */
      chatbotMessages.innerHTML = "";

      /*
       * Show the welcome message returned
       * from Django.
       */
      addMessage(data.response, "bot");

      /*
       * Django tells JavaScript whether
       * language buttons should be visible.
       */
      setLanguageOptionsVisible(data.show_language_options === true);

      /*
       * Normal quick replies should remain
       * hidden during language selection.
       */
      setQuickRepliesVisible(data.show_quick_replies === true);

      chatbotInitialized = true;
    } catch (error) {
      removeTypingIndicator();

      console.error("Chatbot initialization error:", error);

      addMessage(
        error.message || "Unable to start chatbot.",
        "bot",
        null,
        true,
      );
    }
  }

  /* =========================================
           OPEN CHATBOT
        ========================================= */

  function openChatbot() {
    chatbotWindow.classList.add("is-open");

    chatbotToggle.classList.add("is-open");

    chatbotWindow.setAttribute("aria-hidden", "false");

    chatbotToggle.setAttribute("aria-expanded", "true");

    if (notificationBadge) {
      notificationBadge.style.display = "none";
    }

    initializeChatbot();

    setTimeout(function () {
      chatbotInput.focus();
    }, 250);
  }

  /* =========================================
           CLOSE CHATBOT
        ========================================= */

  function closeChatbot() {
    chatbotWindow.classList.remove("is-open");

    chatbotToggle.classList.remove("is-open");

    chatbotWindow.setAttribute("aria-hidden", "true");

    chatbotToggle.setAttribute("aria-expanded", "false");
  }

  /* =========================================
           SEND MESSAGE
        ========================================= */

  async function sendMessage(message) {
    const userMessage = String(message || "").trim();

    if (!userMessage) {
      return;
    }

    if (!config.messageUrl) {
      addMessage("Chatbot message URL is missing.", "bot", null, true);

      return;
    }

    addMessage(userMessage, "user");

    chatbotInput.value = "";

    setLoading(true);

    showTypingIndicator();

    try {
      const response = await fetch(config.messageUrl, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",

          "X-CSRFToken": getCookie("csrftoken"),

          "X-Requested-With": "XMLHttpRequest",
        },

        body: JSON.stringify({
          message: userMessage,
        }),
      });

      const contentType = response.headers.get("content-type") || "";

      if (!contentType.includes("application/json")) {
        const htmlResponse = await response.text();

        console.error("Django returned HTML:", htmlResponse);

        throw new Error(
          "The server returned an invalid " +
            "response. Check the Django terminal.",
        );
      }

      const data = await response.json();

      removeTypingIndicator();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Unable to send message.");
      }

      /*
       * Quick options remain hidden while
       * collecting name, phone and email.
       *
       * They appear after onboarding is
       * completed.
       */
      setQuickRepliesVisible(data.show_quick_replies === true);

      addMessage(data.response, "bot", data.action || null);
    } catch (error) {
      removeTypingIndicator();

      console.error("Flying Fox chatbot error:", error);

      addMessage(error.message || "Something went wrong.", "bot", null, true);
    } finally {
      setLoading(false);

      chatbotInput.focus();
    }
  }

  /* =========================================
           OPEN / CLOSE EVENTS
  ========================================= */

  chatbotToggle.addEventListener("click", function () {
    if (chatbotWindow.classList.contains("is-open")) {
      closeChatbot();
    } else {
      openChatbot();
    }
  });

  if (chatbotClose) {
    chatbotClose.addEventListener("click", closeChatbot);
  }

  /* =========================================
           FORM SUBMIT
  ========================================= */

  chatbotForm.addEventListener("submit", function (event) {
    event.preventDefault();

    /*
     * Do not allow normal message submission
     * while language selection is visible.
     */
    if (
      languageOptionsContainer &&
      languageOptionsContainer.style.display !== "none"
    ) {
      return;
    }

    sendMessage(chatbotInput.value);
  });

  /* =========================================
           LANGUAGE BUTTONS
  ========================================= */

  languageButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      /*
       * Example:
       *
       * data-language="ml"
       *
       * becomes:
       *
       * languageCode = "ml"
       */
      const languageCode = button.dataset.language;

      /*
       * Button text becomes the user message.
       *
       * Example:
       * English
       * മലയാളം
       * हिंदी
       * தமிழ்
       */
      const languageName = button.textContent.trim();

      /*
       * Safety check.
       */
      if (!languageCode) {
        console.error("Language code missing from button.");

        return;
      }

      /*
       * Prevent double clicking.
       */
      languageButtons.forEach(function (languageButton) {
        languageButton.disabled = true;
      });

      /*
       * Send selected language to Django.
       */
      selectChatbotLanguage(languageCode, languageName).finally(function () {
        /*
         * Enable buttons again.
         *
         * They will normally be hidden after
         * successful language selection.
         */
        languageButtons.forEach(function (languageButton) {
          languageButton.disabled = false;
        });
      });
    });
  });

  /* =========================================
           QUICK REPLY BUTTONS
  ========================================= */

  quickReplyButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      const message = button.dataset.message;

      if (!message) {
        return;
      }

      sendMessage(message);
    });
  });

  /* =========================================
           ESCAPE KEY
  ========================================= */

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && chatbotWindow.classList.contains("is-open")) {
      closeChatbot();
    }
  });
});