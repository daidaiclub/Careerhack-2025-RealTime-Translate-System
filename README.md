# Realtime Audio Translate System

## Introduction

企業溝通無國界翻譯系統 - 建立多語言的即時語音翻譯

## Features

1. Real-Time Speech to Text Translation
2. Company-Specific Terminology Detector
3. Clerk of Meetings

## File Structure

```plaintext
├── src            # Backend Source Code
├── dataset        # CareerHack Dataset (including training and knowledge dataset)
├── dataset.ipynb  # Preprocessing Dataset Notebook
├── pyproject.toml # Python Project Configuration
└── README.md
```

## Usage

### Prerequisites

0. Linux / MacOS is recommended.
1. Python 3.13+
2. Install Conda or Mamba, see [Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) or [Mamba](https://github.com/conda-forge/miniforge?tab=readme-ov-file#install)
2. Install the python packages mananger `pixi` by running the following command:
```bash
# Linux / MacOS
curl -fsSL https://pixi.sh/install.sh | bash
# Windows
powershell -ExecutionPolicy ByPass -c "irm -useb https://pixi.sh/install.ps1 | iex"
```

### Virtual Environment

```bash
pixi install
# Check the environment directory
conda config --show envs_dirs
# replace the path and conda-name like `careerhack`
ln -s /path/to/project/.pixi/envs/default /path/to/conda/bash/envs/conda-name
```

If you operating system is Linux or MacOS, you can run the following command to quickly setup the **ALL** environment:
```bash
make setup
```

### Gcloud Setup

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