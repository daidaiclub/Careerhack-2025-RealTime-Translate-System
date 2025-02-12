let audioContext = null;
let mediaStream = null;
let workletNode = null;

async function startRecording() {
  try {
    // 建立 AudioContext
    let sampleRate = 16000;
    audioContext = new AudioContext({ sampleRate });

    // 取得麥克風
    mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        deviceId: "default",
        sampleRate: sampleRate,
        sampleSize: 16,
        channelCount: 1
      },
      video: false
    });

    // 建立 WorkletNode
    await audioContext.audioWorklet.addModule("./pcmWorker.js");
    workletNode = new AudioWorkletNode(audioContext, "pcm-worker", {
      outputChannelCount: [1],
    });

    // 建立 MediaStreamSource，接到 workletNode
    const source = audioContext.createMediaStreamSource(mediaStream);
    source.connect(workletNode);

    // 從 worklet 接收音訊，送給後端
    workletNode.port.onmessage = function (event) {
      socket.emit("audio_stream", event.data);
      // stopRecording();
    };

    $("#mic-btn i").removeClass().addClass("fa-solid fa-circle text-danger");
    workletNode.port.start();
  } catch (error) {
    console.error("錄音發生錯誤:", error);
  }
}

function cleanUpAudio() {
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
}

function stopRecording() {
  cleanUpAudio();
  $("#mic-btn i").removeClass().addClass("fa-solid fa-microphone");
}

$("#mic-btn").click(async function () {
  if (!audioContext) {
    startRecording();
  } else {
    stopRecording();
  }
});