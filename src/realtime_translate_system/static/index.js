var socket = io("http://140.113.110.99:5000");
// socket.binaryType = "arraybuffer";
let mediaRecorder;
let language = "Traditional Chinese";

// 讓按鈕觸發檔案選擇
$("#upload-btn").click(function () {
  $("#file-input").click();
});

// 當用戶選擇檔案後，顯示檔名並自動上傳
$("#file-input").change(function () {
  var file = this.files[0];
  if (file) {
    if (file.type === "audio/wav") {
      $("#file-name").text(file.name);
      uploadFile(file);
    } else {
      alert("只能上傳 WAV 檔案");
    }
  }
});

$("#language-select").change(function () {
  language = $(this).val();
  renderTranscripts();
});

// 自動上傳檔案
function uploadFile(file) {
  var formData = new FormData();
  formData.append("file", file);
  setUploadIcon("loading");

  $.ajax({
    url: "http://140.113.110.99:5000/upload",
    type: "POST",
    data: formData,
    contentType: false,
    processData: false,
    error: function (error) {
      setUploadIcon("default");
      console.error(error);
    }
  });
}

// WebSocket 監聽進度
var transcripts = [];

// 當收到完整的翻譯內容，存進 transcripts 並重新渲染
socket.on("transcript", function (data) {
  setUploadIcon("success");
  transcripts.push(data);
  renderTranscripts();
});

// 當收到串流翻譯更新，更新 transcripts 最後一筆的指定語言內容，再重新渲染
socket.on("transcript_stream", function (data) {
  transcripts.push(data);
  renderTranscripts();
});

socket.on("complete", function () {
  setUploadIcon("default");
});

// 根據全域 transcripts 陣列和目前選擇的語言來渲染整個 transcript 區域
function renderTranscripts() {
  var textarea = $("#transcript_area");
  var content = "";
  transcripts.forEach(function (item) {
    // 假設 item 是個物件，且 key 為各國語言名稱
    if (item[language]) {
      content += item[language] + "\n";
    }
  });
  textarea.val(content);
  textarea.scrollTop(textarea[0].scrollHeight);
}


/**
 * 設置上傳按鈕圖示
 * @param {string} status - "loading", "success", "default"
 */
function setUploadIcon(status) {
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