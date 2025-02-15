import { triggerFileUpload, triggerUploadFile } from "./upload.js";
import { openChatbot, closeChatbot } from "./ui.js";
import { fetchDocs, deleteDoc, loadDocFromURL, toggleTitleEdit, resetToNewMeeting, triggerLanguageSelect, saveDoc } from "./document.js";
import { chat } from "./chatbot.js";
import { getDocIdFromURL } from "./utils.js";
import { triggerMicButton } from "./audio.js";
import "./transcript.js";
import "./editor.js";

function initDeleteButton() {
  const $btn = $("#delete-btn");
  const docId = getDocIdFromURL();
  $btn.off("click");
  if (docId) {
    $btn.removeClass("d-none");
    $btn.on("click", () => deleteDoc(docId));
  } else {
    $btn.addClass("d-none");
  }
}

$(document).ready(function () {
  $("#upload-btn").click(triggerFileUpload);
  $("#file-input").change(triggerUploadFile);
  $("#language-select").change( e => triggerLanguageSelect(e.target.value));
  $("#edit-title-btn").click(toggleTitleEdit);
  $("#meeting-title-input").on("keypress", e => {
    if (e.which === 13) {
      toggleTitleEdit();
    }
  });
  $("#open-chatbot").click(openChatbot);
  $("#close-chatbot").click(closeChatbot);
  $("#chat-input").on("keypress", e => {
    if (e.which === 13) {
      chat($("#chat-input").val());
    }
  });
  // $("#transcript_area").on("input", debouncedInputContent);
  $("#doc-list").on("click", "li:first", resetToNewMeeting);
  $("#save-btn").on("click", saveDoc);
  $("#mic-btn").click(triggerMicButton);

  initDeleteButton();
  fetchDocs();
  loadDocFromURL();
});

(function(history) {
  const pushState = history.pushState;
  const replaceState = history.replaceState;

  history.pushState = function(...args) {
    const result = pushState.apply(history, args);
    window.dispatchEvent(new Event("locationchange"));
    return result;
  };

  history.replaceState = function(...args) {
    const result = replaceState.apply(history, args);
    window.dispatchEvent(new Event("locationchange"));
    return result;
  };

  window.addEventListener("popstate", () => {
    window.dispatchEvent(new Event("locationchange"));
  });
})(window.history);

window.addEventListener("locationchange", () => {
  initDeleteButton();
  fetchDocs();
  loadDocFromURL();
});