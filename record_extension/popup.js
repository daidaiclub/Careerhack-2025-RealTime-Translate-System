document.addEventListener("DOMContentLoaded", function () {
    $('#mic-btn').click(function () {
        toggleMicButton();
    });
});

// 內部狀態：錄音相關
let audioContext = null;
let mediaStream = null;
let workletNode = null;
const audioSocket = io("127.0.0.1:5000/audio_stream", { path: "/socket.io" });
/**
 * 開始錄音：
 * 1. 建立 AudioContext（設定採樣率 16000）
 * 2. 取得麥克風權限並建立 MediaStream
 * 3. 載入 AudioWorklet 模組並建立 WorkletNode
 * 4. 連接來源、設定 worklet message handler 將音訊資料透過 socket 傳送至後端
 * 5. 更新麥克風按鈕圖示為錄音中
 */
async function startRecording() {
  try {
    const sampleRate = 16000;
    audioContext = new AudioContext({ sampleRate });
    mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        deviceId: "default",
        sampleRate: sampleRate,
        sampleSize: 16,
        channelCount: 1,
        noiseSuppression: true,
        echoCancellation: true
      },
      video: false
    });

    // **Create Noise Suppression Filters**
    const highPassFilter = audioContext.createBiquadFilter();
    highPassFilter.type = "highpass";
    highPassFilter.frequency.value = 100; // Remove low-frequency noise

    const lowPassFilter = audioContext.createBiquadFilter();
    lowPassFilter.type = "lowpass";
    lowPassFilter.frequency.value = 4000; // Remove high-frequency noise

    // Create an AudioWorklet to handle PCM processing
    await audioContext.audioWorklet.addModule("./assets/js/pcmWorker.js");
    workletNode = new AudioWorkletNode(audioContext, "pcm-worker", {
      outputChannelCount: [1]
    });

    const source = audioContext.createMediaStreamSource(mediaStream);

    // **Connect filters to the source and the worklet node**
    source.connect(highPassFilter);
    highPassFilter.connect(lowPassFilter);
    lowPassFilter.connect(workletNode); // Direct output to the worklet node

    // Handle audio data from the worklet node
    workletNode.port.onmessage = (event) => {
      audioSocket.emit("audio_stream", event.data);
    };

    uiToggleMicButton();
    workletNode.port.start();
  } catch (error) {
    showGlobalAlert("錄音功能無法使用，請確認麥克風設定與瀏覽器權限。", "danger");
    console.error("錄音發生錯誤:", error);
  }
}

/**
 * 停止錄音，清理所有相關資源並還原 UI 狀態
 */
function stopRecording() {
  if (workletNode) {
    workletNode.disconnect();
    workletNode = null;
  }
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop());
    mediaStream = null;
  }
  if (audioContext) {
    audioContext.close();
    audioContext = null;
  }

  uiToggleMicButton();
}

function triggerMicButton() {
  if (!audioContext) {
    startRecording();
  } else {
    stopRecording();
  }
}

function toggleMicButton() {
  const $icon = $("#mic-btn i");

  if ($icon.hasClass("fa-microphone")) {
    $icon.removeClass().addClass("fa-solid fa-circle text-danger");
  } else {
    $icon.removeClass().addClass("fa-solid fa-microphone");
  }
}
