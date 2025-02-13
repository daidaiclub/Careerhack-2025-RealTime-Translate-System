import { setUploadIcon } from './ui.js';
import { FileApi } from './api/document-api.js';

export function triggerFileUpload() {
  console.log("triggerFileUpload");
  $('#file-input').click();
}

export function triggerUploadFile() {
  var file = $('#file-input')[0].files[0];
  if (file) {
    if (file.type === 'audio/wav') {
      uploadFile(file);
      setUploadIcon('loading');
    }
  } else {
    alert('只能上傳 WAV 檔案');
  }
}

export function uploadFile(file) {
  var formData = new FormData();
  formData.append('file', file);

  FileApi.uploadFile(formData);
}