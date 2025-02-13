export class FileApi {
  static baseUrl = "/api/upload";

  /**
   * 上傳檔案（如果需要）
   * @param {FormData} formData 檔案資料
   * @returns {Promise<any>}
   */
  static async uploadFile(formData) {
    try {
      const response = await $.ajax({
        url: `${this.baseUrl}/`,
        type: "POST",
        data: formData,
        contentType: false,
        processData: false,
      });

      return response;
    } catch (error) {
      console.error(error);
      throw error;
    }
  }
}

export class DocAPI {
  static baseUrl = "/api/doc";

  /**
   * 取得所有文件
   * @returns {Promise<Array>} 文件資料陣列
   */
  static async fetchDocs() {
    try {
      const data = await $.ajax({
        url: `${this.baseUrl}`,
        method: "GET"
      });
      return data;
    } catch (error) {
      console.error("Error fetching docs:", error);
      throw error;
    }
  }

  /**
   * 根據 id 取得單一文件
   * @param {string|number} id 文件 id
   * @returns {Promise<Object>} 文件資料
   */
  static async loadDoc(id) {
    try {
      const data = await $.ajax({
        url: `${this.baseUrl}/${id}`,
        method: "GET"
      });
      return data;
    } catch (error) {
      console.error("Error loading doc:", error);
      throw error;
    }
  }

  /**
   * 新增文件
   * @param {Object} payload 文件內容，包含 title、content 與 updated_at
   * @returns {Promise<Object>} 新增後的文件資料
   */
  static async createDoc(payload) {
    try {
      const data = await $.ajax({
        url: `${this.baseUrl}/`,
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify(payload)
      });
      return data;
    } catch (error) {
      console.error("Error creating doc:", error);
      throw error;
    }
  }

  /**
   * 更新文件
   * @param {Object} updatePayload 文件更新內容，須包含 id、title、content 與 updated_at
   * @returns {Promise<Object>} 更新後的文件資料
   */
  static async updateDoc(updatePayload) {
    try {
      const data = await $.ajax({
        url: `${this.baseUrl}/`,
        method: "PUT",
        contentType: "application/json",
        data: JSON.stringify(updatePayload)
      });
      return data;
    } catch (error) {
      console.error("Error updating doc:", error);
      throw error;
    }
  }

  static async deleteDoc(docId) {
    try {
      const response = await $.ajax({
        url: `${this.baseUrl}/${docId}`,
        method: "DELETE"
      });
      return response;
    } catch (error) {
      console.error("Error deleting doc:", error);
      throw error;
    }
  }
}
