echo [$(date)]: "START SERVING SETUP"
echo [$(date)]: "Create project folder structure"
python3 template.py
echo [$(date)]: "Copy blessed model to serving"
python3 src/utils/download_blessed_model.py
cp artifacts/models/blessed_model.h5 model_serving/src/production_model/model.h5
echo [$(date)]: "Copy configuration to serving"
cp configs/config.yaml model_serving/src/configs/config.yaml
echo [$(date)]: "Copy params to serving"
cp params.yaml model_serving/src/params.yaml
echo [$(date)]: "copy common utils to serving"
cp src/utils/common.py model_serving/src/utils/common.py
echo [$(date)]: "Copy setup.py"
cp setup.py model_serving/setup.py
echo [$(date)]: "SERVING SETUP COMPLETED"