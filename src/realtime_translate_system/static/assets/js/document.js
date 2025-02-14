// assets/js/document.js
import { DocAPI } from "./api/document-api.js";
import { toggleTitleEdit as uiToggleTitleEdit, showGlobalAlert } from "./ui.js";
import { getDocIdFromURL } from "./utils.js";
import { debounce } from "./debounce.js";
import { transcriptState, currentLanguage, setCurrentLanguage, state } from "./transcriptState.js";
import { renderTranscripts } from "./renderTranscripts.js";

// DOM 參考
const dom = {
  $meetingTitle: $("#meeting-title"),
  $meetingTitleInput: $("#meeting-title-input"),
  $transcriptArea: $("#transcript_area"),
  $docList: $("#doc-list")
};

/**
 * 根據文件 id 讀取文件內容並更新 UI
 * 後端資料應包含 transcript_chinese, transcript_english, transcript_german, transcript_japanese
 */
async function loadDoc(id) {
  try {
    const data = await DocAPI.loadDoc(id);
    state.docId = data.id;
    state.currentTitle = data.title;
    // 從後端載入各國語言內容，並存入 transcriptState
    transcriptState.chinese = data.transcript_chinese;
    transcriptState.english = data.transcript_english;
    transcriptState.german = data.transcript_german;
    transcriptState.japanese = data.transcript_japanese;
    dom.$meetingTitle.text(state.currentTitle);
    // 更新 textarea 內容（以當前選定語言顯示）
    dom.$transcriptArea.val(transcriptState[currentLanguage]);
  } catch (error) {
    throw error;
  }
}

/**
 * 切換標題編輯模式，更新標題並儲存文件
 */
export function toggleTitleEdit() {
  uiToggleTitleEdit();
  if (!dom.$meetingTitle.hasClass("d-none")) {
    // 離開編輯模式，更新標題
    const newTitle = dom.$meetingTitleInput.val();
    dom.$meetingTitle.text(newTitle);
    state.currentTitle = newTitle;
    saveDoc();
  } else {
    // 進入編輯模式，填入目前標題並 focus
    dom.$meetingTitleInput.val(dom.$meetingTitle.text()).focus();
  }
}

/**
 * 當使用者編輯筆記時，將目前 textarea 內容存入 transcriptState，並儲存文件
 */
export function inputContent() {
  transcriptState[currentLanguage] = dom.$transcriptArea.val();
}

/**
 * 取得文件列表並更新文件清單 UI
 */
export async function fetchDocs() {
  try {
    const docs = await DocAPI.fetchDocs();
    dom.$docList.find("li:not(:first)").remove();
    docs.forEach(doc => {
      const li = $("<li>")
        .text(doc.title)
        .attr("data-doc-id", doc.id)
        .css("cursor", "pointer")
        .on("click", function () {
          loadDoc(doc.id);
          window.history.pushState({}, "", "/" + doc.id);
        });
      dom.$docList.append(li);
    });
  } catch (error) {
    console.error(error);
  }
}

/**
 * 根據網址自動載入文件（若網址為 "/" 則表示新文件）
 */
export async function loadDocFromURL() {
  const docIdFromURL = getDocIdFromURL();
  if (!docIdFromURL) return;
  try {
    await loadDoc(docIdFromURL);
  } catch (error) {
    window.history.pushState({}, "", "/");
    showGlobalAlert("文件不存在", "danger");
    console.error(error);
  }
}

/**
 * 儲存文件：若 state.docId 為 null 則新增文件，否則更新文件
 * 傳送 payload 時包含四國語言內容
 */
export async function saveDoc() {
  if (state.isSaving) return;
  state.isSaving = true;
  console.log("Saving doc...");

  const payload = {
    title: state.currentTitle,
    transcript_chinese: transcriptState.chinese,
    transcript_english: transcriptState.english,
    transcript_german: transcriptState.german,
    transcript_japanese: transcriptState.japanese,
    updated_at: new Date().toISOString()
  };

  try {
    if (!state.docId) {
      const data = await DocAPI.createDoc(payload);
      state.docId = data.id;
      window.history.pushState({}, "", "/" + state.docId);
    } else {
      const updatePayload = { id: state.docId, ...payload };
      await DocAPI.updateDoc(updatePayload);
    }
    fetchDocs();
  } catch (error) {
    console.error(error);
  } finally {
    state.isSaving = false;
  }
}

/**
 * 重設為新文件，清空所有語言的筆記內容
 */
export function resetToNewMeeting() {
  state.docId = null;
  state.currentTitle = "新會議";
  transcriptState.chinese = "";
  transcriptState.english = "";
  transcriptState.german = "";
  transcriptState.japanese = "";
  dom.$meetingTitle.text(state.currentTitle);
  dom.$transcriptArea.val("");
  window.history.pushState({}, "", "/");
}

/**
 * 刪除文件：根據傳入的文件 id 進行刪除
 */
export async function deleteDoc(id) {
  if (confirm("確認刪除這份文件？刪除後無法復原！")) {
    try {
      await DocAPI.deleteDoc(id);
      resetToNewMeeting();
    } catch (error) {
      console.error("刪除文件失敗：", error);
      showGlobalAlert("刪除文件失敗", "danger");
    }
  }
}

/**
 * Debounced 版本的 inputContent，延遲 500 毫秒後觸發
 */
export const debouncedInputContent = debounce(inputContent, 500);

/**
 * 切換語言：
 * 1. 將目前 textarea 內容存回 transcriptState（保留使用者手動修改）
 * 2. 切換 currentLanguage，並更新 textarea 顯示對應語言內容
 */
export function triggerLanguageSelect(newLang) {
  // 儲存目前語言的內容
  transcriptState[currentLanguage] = dom.$transcriptArea.val();
  // 切換語言
  setCurrentLanguage(newLang);
  // 更新 textarea
  dom.$transcriptArea.val(transcriptState[newLang]);

  // 更新 textarea 的 placeholder
  const placeholders = {
    chinese: "開啟會議記錄...",
    english: "Start meeting notes...",
    german: "Besprechungsnotizen starten...",
    japanese: "会議記録を開始..."
  };
  dom.$transcriptArea.attr("placeholder", placeholders[newLang]);

  renderTranscripts();
}


/**
 * 監聽 transcriptState 的變化，若有變化儲存到文件
 */
export function initAutoSave() {
  window.autoSaveHandler = debounce(saveDoc, 500);
  console.log("AutoSave initialized.");
}