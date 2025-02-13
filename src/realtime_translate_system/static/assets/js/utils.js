import { showGlobalAlert } from './ui.js';

export function getDocIdFromURL() {
  const path = window.location.pathname;
  if (path === "/" || path === "") {
    return null;
  }
  const docId = path.substring(1);
  if (!docId || isNaN(Number(docId))) {
    console.warn("網址格式不正確，無法取得文件 ID");
    showGlobalAlert('網址格式不正確', 'danger');
    window.history.pushState({}, '', '/');
    return;
  }
  return docId;
}