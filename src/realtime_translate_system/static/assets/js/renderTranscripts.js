// assets/js/renderTranscripts.js
import { transcriptState, currentLanguage } from "./transcriptState.js";

export function renderTranscripts() {
  const $textarea = $("#transcript_area");
  const cursorPos = $textarea.prop("selectionStart");
  const scrollPos = $textarea.scrollTop();
  
  // 用全域 transcriptState 中目前語言的內容更新 textarea
  $textarea.val(transcriptState[currentLanguage]);
  
  // 還原游標與捲動位置
  $textarea.prop("selectionStart", cursorPos);
  $textarea.prop("selectionEnd", cursorPos);
  $textarea.scrollTop(scrollPos);
}
