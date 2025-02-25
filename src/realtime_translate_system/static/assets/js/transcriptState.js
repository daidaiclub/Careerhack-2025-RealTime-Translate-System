// assets/js/transcriptState.js
export const state = {
  docId: null,
  isSaving: false,
  currentTitle: "新會議"
};

const stateData = {
  chinese: "",
  english: "",
  german: "",
  japanese: ""
};

export let currentLanguage = "chinese";

/**
 * 切換目前選定語言
 * @param {string} newLang - "chinese", "english", "german", "japanese"
 */
export function setCurrentLanguage(newLang) {
  currentLanguage = newLang;
}

// 使用 Proxy 監聽 stateData 的修改，當有變更時呼叫 autoSaveHandler（若已設定）
export const transcriptState = new Proxy(stateData, {
  set(target, prop, value) {
    target[prop] = value;
    return true;
  }
});
