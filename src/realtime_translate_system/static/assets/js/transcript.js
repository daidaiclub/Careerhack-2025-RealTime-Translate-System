// assets/js/transcript.js
import { audioSocket } from "./socket.js";
import { setUploadIcon } from "./ui.js";
import { transcriptState, currentLanguage } from "./transcriptState.js";
import { insertTranscript } from "./renderTranscripts.js";

function transformFormat(data) {
  const text = data.text
  return {
    status: data.status,
    text: {
      chinese: text["Traditional Chinese"]["value"],
      english: text["English"]["value"],
      german: text["German"]["value"],
      japanese: text["Japanese"]["value"]
    },
    explains: {
      chinese: text["Traditional Chinese"]["explains"],
      english: text["English"]["explains"],
      german: text["German"]["explains"],
      japanese: text["Japanese"]["explains"]
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
    // 如果目前顯示的語言有更新，就只在尾端插入新內容
    console.log(data)
    insertTranscript(data.text[currentLanguage] + "\n", data.explains[currentLanguage]);
  } else {
    setUploadIcon("default");
  }
});

/**
 * 串流更新資料：同上
 */
audioSocket.on("transcript_stream", (data) => {
  data = transformFormat(data);
  for (let lang in data.text) {
    transcriptState[lang] += data.text[lang] + "\n";
  }
  insertTranscript(data.text[currentLanguage] + "\n", data.explains[currentLanguage]);
});
