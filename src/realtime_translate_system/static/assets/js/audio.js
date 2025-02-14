import { audioSocket } from "./socket.js";
import { toggleMicButton as uiToggleMicButton, showGlobalAlert } from "./ui.js";

// 內部狀態：錄音相關
let audioContext = null;
let mediaStream = null;
let workletNode = null;

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
    
    await audioContext.audioWorklet.addModule("./assets/js/pcmWorker.js");
    
    workletNode = new AudioWorkletNode(audioContext, "pcm-worker", {
      outputChannelCount: [1]
    });
    
    const source = audioContext.createMediaStreamSource(mediaStream);
    source.connect(workletNode);
    
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

export function triggerMicButton() {
  if (!audioContext) {
    startRecording();
  } else {
    stopRecording();
  }
}