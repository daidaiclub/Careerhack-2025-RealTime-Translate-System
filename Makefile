# Makefile
CONDA_NAME=careerhack

.PHONY: setup download

download:
	@echo "Downloading data..."
	gcloud cp gs://careerhack2025-icsd-resource-bucket/Training.zip dataset/
	unzip dataset/Training.zip -d dataset/
	rm dataset/Training.zip

setup:
	@echo "Installing dependencies with Pixi..."
	pixi install

	@echo "Finding Conda envs directory..."
	ENV_DIR=$$(conda config --show envs_dirs | awk '/-/ {print $$2; exit}'); \
	echo "Using Conda envs directory: $$ENV_DIR"

	@echo "Creating symbolic link for Conda environment..."
	ln -sf $(shell pwd)/.pixi/envs/default $$ENV_DIR/$(CONDA_NAME)

	@echo "Setup completed. Conda environment linked as $(CONDA_NAME)."
	conda activate $(CONDA_NAME)