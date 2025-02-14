/**
 * 設置上傳按鈕圖示
 * @param {string} status - "loading", "success", "default"
 */
export function setUploadIcon(status) {
  var icon = $("#upload-btn i");

  if (status === "loading") {
    icon.removeClass().addClass("fas fa-spinner fa-spin");
    $("#upload-btn").prop("disabled", true);
  } else if (status === "success") {
    icon.removeClass().addClass("fas fa-check text-success");
    $("#upload-btn").prop("disabled", true);
  } else {
    icon.removeClass().addClass("fas fa-cloud-upload-alt");
    $("#upload-btn").prop("disabled", false);
  }
}

export function toggleTitleEdit() {
  const $title = $("#meeting-title");
  const $btn = $("#edit-title-btn");
  const $input = $("#meeting-title-input");

  $input.toggleClass("d-none");
  $btn.toggleClass("d-none");
  $title.toggleClass("d-none");
}

export function openChatbot() {
  $("#chatbot").removeClass("d-none");
  $("#open-chatbot").addClass("d-none");
  $("#close-chatbot").removeClass("d-none");
  $('.chatbot').css('right', '0');
  $('.content').css('width', 'calc(85% - 450px)');
}

export function closeChatbot() {
  $("#chatbot").addClass("d-none");
  $("#open-chatbot").removeClass("d-none");
  $("#close-chatbot").addClass("d-none");
  $('.chatbot').css('right', '-450px');
  $('.content').css('width', '85%');
}

export function toggleMicButton() {
  const $icon = $("#mic-btn i");

  if ($icon.hasClass("fa-microphone")) {
    $icon.removeClass().addClass("fa-solid fa-circle text-danger");
  } else {
    $icon.removeClass().addClass("fa-solid fa-microphone");
  }
}

export function showGlobalAlert(message, type = "success", timeout = 3000) {
  const alertId = `alert-${Date.now()}`;
  const alertHtml = `
    <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show text-center shadow-lg" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>`;

  $("#global-alert-container").append(alertHtml);

  // 設定自動消失
  setTimeout(() => {
    $(`#${alertId}`).alert("close");
  }, timeout);
}
