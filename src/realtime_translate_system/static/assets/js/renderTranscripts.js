// assets/js/renderTranscripts.js
import { transcriptState, currentLanguage } from "./transcriptState.js";
import { tiptapEditor } from "./editor.js"; // 假設 editorInstance.js export tiptapEditor

/**
 * 當後端載入文件或切換語言時，完全更新 editor 內容，
 * 同時記錄並還原游標與捲動位置。
 */
export function renderTranscriptsFull() {
  // 記錄目前選取範圍與捲動位置
  const { from, to } = tiptapEditor.state.selection;
  const scrollPos = tiptapEditor.view.dom.scrollTop;

  // 用 transcriptState[currentLanguage] 更新 editor
  tiptapEditor.commands.setContent(transcriptState[currentLanguage] || "", {
    parse: true
  });

  // 還原游標與捲動位置
  tiptapEditor.commands.setTextSelection({ from, to });
  tiptapEditor.view.dom.scrollTop = scrollPos;
}

// 將 value 內的 ==文字== 轉換成 mark 並注入對應的 explanation 至 data-d
function transformContent(value, explains) {
  let index = 0
  return value.replace(/==([^=]+)==/g, (match, p1) => {
    console.log(p1, value, explains);
    const explanation = explains[index++] || ''
    return `<mark data-d="${explanation}">${p1}</mark>`
  })
}

/**
 * 當 socket 回傳新資料時，僅在文件尾端插入新內容，
 * 並保持使用者游標不亂移動。
 */
export function insertTranscript(newText, explains) {
  // 取得目前文件尾端位置
  const endPos = tiptapEditor.state.doc.content.size;
  // 記錄使用者目前的選取範圍
  const { from, to } = tiptapEditor.state.selection;

  // 新資料包上 <p> 自動換行（依需求調整）
  // const newContent = `${newText}</p>`;
  const newContent = transformContent(newText.replace(/\n$/, ''), explains);
  console.log(newContent);
  tiptapEditor.commands.insertContentAt(endPos, newContent, { parse: true });

  // 還原使用者原先選取範圍
  tiptapEditor.commands.setTextSelection({ from, to });
}
