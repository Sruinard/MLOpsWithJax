MODEL_NAME=brain
docker run -t --rm -p 8501:8501 --mount type=bind,source=$PWD/models/$MODEL_NAME,target=/models/$MODEL_NAME/ -e MODEL_NAME=$MODEL_NAME -e --xla_cpu_compilation_enabled=true docker.io/tensorflow/serving:latest --xla_cpu_compilation_enabled=true &

curl -X POST -d @sample.json http://127.0.0.1:8501/v1/models/$MODEL_NAME:predict