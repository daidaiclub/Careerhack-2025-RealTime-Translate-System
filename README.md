# Realtime Audio Translate System

## Introduction

企業溝通無國界翻譯系統 - 建立多語言的即時語音翻譯

## Features

1. Real-Time Speech to Text Translation
2. Company-Specific Terminology Detector
3. Clerk of Meetings

## File Structure

```plaintext
├── src              # Source Code Directory
├── dataset          # Dataset Folder (including CareerHack Dataset)
├── Dockerfile       # Docker Configuration File
├── environment.yaml # Conda Environment File
├── Makefile         # Makefile for Setup and Commands
├── README.md        # Project Documentation
├── requirements.txt # Python Requirements File
└── ui               # User Interface Code (Experimental)
```

## Usage

### Linux

#### Prerequisites

0. Linux / MacOS is recommended.
1. Python 3.13+
2. Install Conda or Mamba, see [Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) or [Mamba](https://github.com/conda-forge/miniforge?tab=readme-ov-file#install)

#### Virtual Environment

1. Create a virtual environment and activate it

```bash
# or use mamba
conda env create -f environment.yml
conda activate careerhack
```

If you operating system is Linux or MacOS, you can run the following command to quickly setup the **ALL** environment:

```bash
make setup
```

#### Gcloud Setup

1. Set up the `gcloud`

```bash
gcloud init
# Login with the CareerHack account
```

2. Dataset download (Optional)

```bash
gcloud cp gs://careerhack2025-icsd-resource-bucket/Training.zip dataset/
unzip dataset/Training.zip -d dataset/
# or
make download
```

### Docker Development

1. Build the Docker Image

```bash
docker build -t realtime-translate-system .
```

2. Run the Docker Container without GPU in powershell

`grp-secret.json` is the Google Cloud Service Account Key.

```bash
docker run -it --name rt -p 5000:5000 --rm `
  -v ${PWD}\grp-secret.json:/app/grp-secret.json:ro `
  -v ${PWD}\src\realtime_translate_system:/app/realtime_translate_system `
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/grp-secret.json" `
  -e GOOGLE_CLOUD_PROJECT="tsmccareerhack2025-icsd-grp1" `
  realtime-translate-system flask run --debug
```

### Windows

#### Virtual Environment

1. Create a virtual environment and activate it

```bash
conda create --name careerhack python=3.13.1 -y
conda activate careerhack
```

2. Install the required packages

```bash
pip install -r requirements.txt
```

#### Gcloud Setup

1. Set up the `gcloud` **by powershell**

```powershell
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")

& $env:Temp\GoogleCloudSDKInstaller.exe
```

2. Add the `.env` file and add the following content

```plaintext
GOOGLE_CLOUD_PROJECT = tsmccareerhack2025-icsd-grp1
```

3. Login to Google Cloud

```powershell
gcloud auth application-default login
```

#### ffmpeg

1. Download the ffmpeg from [ffmpeg](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z) and install it.

2. Set the environment variable
   Add the environment variable `C:\Program Files\[ffmpeg-name]\bin`

### K8s Deployment

```bash
kubectl apply -f namespace.yaml
base64 -w 0 grp-secret.json > grp-secret.json.base64
kubectl create secret generic grp-secret --from-file=grp-secret.json=grp-secret.json.base64 -n careerhack

# Set the SSL Certificate
sudo certbot certonly \                        
  --dns-cloudflare \
  --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d example.com

# Apply the SSL Certificate
kubectl create secret tls careerhack-tls \
  --cert=/etc/letsencrypt/live/example.com/fullchain.pem \
  --key=/etc/letsencrypt/live/example.com/privkey.pem \
  --namespace careerhack

kubectl apply -d k8s.yaml
```