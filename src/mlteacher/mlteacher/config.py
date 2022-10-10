import os
from dotenv import load_dotenv

load_dotenv()

class TrainConfig:
    fileshare_connection_string = os.environ.get("FS_CONN_STRING")    
    fileshare_name = os.environ.get("FS_NAME")
    learning_rate = 0.003
    batch_size = 128
    hidden_size = 512
    num_train_steps = 100
    decode_frequency = 500
    max_len_query_digit = 3
    workdir = "."
