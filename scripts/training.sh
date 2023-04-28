
#!/bin/bash -eo pipefail
echo [$(date)]: ">>>>>>>>>>>>>>>>>> TRAINING ENVIRONMENT SETUP >>>>>>>>>>>>>>>>>>"
echo [$(date)]: ">>>>>>>>>>>>>>>>>> Install Miniconda >>>>>>>>>>>>>>>>>>"
apt update
apt install wget
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 
export PATH="/root/miniconda3/bin:${PATH}"
echo "Running $(conda --version)"
conda init bash
. /root/.bashrc
conda update -n base -c defaults conda -y
echo [$(date)]: ">>>>>>>>>>>>>>>>>> Create Environment >>>>>>>>>>>>>>>>>>"
conda create -n myenv python=3.10 -y
echo [$(date)]: ">>>>>>>>>>>>>>>>>> Activate Environment >>>>>>>>>>>>>>>>>>"
conda activate myenv
echo [$(date)]: ">>>>>>>>>>>>>>>>>> Install Requirements >>>>>>>>>>>>>>>>>>"
pip install -r requirements.txt
echo [$(date)]: ">>>>>>>>>>>>>>>>>> Authenticate GCP >>>>>>>>>>>>>>>>>>"
echo $GCLOUD_SERVICE_KEY | gcloud auth activate-service-account --key-file=-
echo [$(date)]: ">>>>>>>>>>>>>>>>>> Project Folder Structure >>>>>>>>>>>>>>>>>>"
python template.py
echo [$(date)]: ">>>>>>>>>>>>>>>>>> Download data from Source >>>>>>>>>>>>>>>>>>"
python src/stage_01_get_data.py --config=configs/config.yaml
echo [$(date)]: ">>>>>>>>>>>>>>>>>> Prepare Model >>>>>>>>>>>>>>>>>>"
python src/stage_02_prepare_model.py --config=configs/config.yaml --params=params.yaml
echo [$(date)]: ">>>>>>>>>>>>>>>>>> Model Training and Evaluation >>>>>>>>>>>>>>>>>>"
python src/stage_03_train_evaluate.py --config=configs/config.yaml --params=params.yaml
echo [$(date)]: ">>>>>>>>>>>>>>>>>> Model blessing >>>>>>>>>>>>>>>>>>"
python src/stage_04_model_blessing.py --config=configs/config.yaml --params=params.yaml
echo [$(date)]: ">>>>>>>>>>>>>>>>>> TRAINING COMPLETED >>>>>>>>>>>>>>>>>>"