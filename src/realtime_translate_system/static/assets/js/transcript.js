// assets/js/transcript.js
import { audioSocket } from "./socket.js";
import { setUploadIcon } from "./ui.js";
import { transcriptState } from "./transcriptState.js";
import { renderTranscripts } from "./renderTranscripts.js";

function transformFormat(data) {
  const text = data.text
  console.log(text)
  return {
    status: data.status,
    text: {
      chinese: text["Traditional Chinese"],
      english: text["English"],
      german: text["German"],
      japanese: text["Japanese"]
    }
  };
}

/**
 * 當收到逐句翻譯資料時：
 * 資料格式預期為 { status: "continue", text: { chinese: "…", english: "…", german: "…", japanese: "…" } }
 */
audioSocket.on("transcript", (data) => {
  if (data.status === "continue") {
    data = transformFormat(data);
    setUploadIcon("success");
    for (let lang in data.text) {
      transcriptState[lang] += data.text[lang] + "\n";
    }
    renderTranscripts();
  } else {
    setUploadIcon("default");
  }
});

/**
 * 串流更新資料同上
 */
audioSocket.on("transcript_stream", (data) => {
  data = transformFormat(data);
  for (let lang in data.text) {
    transcriptState[lang] += data.text[lang] + "\n";
  }
  renderTranscripts();
});
