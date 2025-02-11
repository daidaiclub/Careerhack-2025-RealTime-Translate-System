from google.cloud import storage

def upload_to_gcs(bucket_name: str, destination_blob_name: str, text: str):
    """
    將逐字稿上傳到 Google Cloud Storage (GCS)
    :param bucket_name: GCS Bucket 名稱 (tsmccareerhack2025-icsd-grp1-bucket)
    :param destination_blob_name: 檔案完整路徑 (例如 transcript/meeting_transcript.txt)
    :param text: 逐字稿內容
    """
    # 初始化 GCS 客戶端
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # 將文字內容存入 GCS
    blob.upload_from_string(text, content_type="text/plain")

    print(f"✅ 逐字稿已成功上傳至 gs://{bucket_name}/{destination_blob_name}")

def download_from_gcs(bucket_name: str, blob_name: str):
    """
    從 GCS 下載逐字稿並印出內容
    
    :param bucket_name: GCS 儲存桶名稱 (tsmccareerhack2025-icsd-grp1-bucket)
    :param blob_name: GCS 內的檔案名稱 (例如 transcript/meeting_transcript.txt)
    """
    # 初始化 GCS 客戶端
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # 下載內容
    content = blob.download_as_text()

    # 印出逐字稿
    print("📂 逐字稿內容：\n")
    print(content)

    return content  # 也可以返回內容，方便後續處理

# # 測試上傳
# upload_to_gcs(
#     "tsmccareerhack2025-icsd-grp1-bucket",  # 你的 GCS Bucket 名稱
#     "transcript/meeting_transcript.txt",   # 逐字稿存放位置
#     "這是一份測試逐字稿內容"                # 逐字稿內容
# )

# # 測試下載
# download_from_gcs(
#     "tsmccareerhack2025-icsd-grp1-bucket",  # 你的 GCS Bucket 名稱
#     "transcript/meeting_transcript.txt"    # 逐字稿存放位置
# )
