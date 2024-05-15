import os
import subprocess
import uuid
import configparser
import psutil
import time
# from arq import Worker, BaseWorker, concurrent
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.post("/pyrmd/")
async def create_upload_files(met_file: UploadFile = File(...), compound_file: UploadFile = File(...)):
    start_time = time.time()
    user_id = str(uuid.uuid4())
    user_folder = f"/uploads/{user_id}"
    os.makedirs(user_folder, exist_ok=True)
    met_filename = f"{met_file.filename}"
    cleaned_db_filename = "clean_training_db.csv"
    compound_filename = f"{compound_file.filename}"
    predicted_actives_filename = "predicted_actives.smi"
    database_predictions_filename =  "database_predictions.csv"
    met_location = f"{user_folder}/{met_filename}"
    cleaned_db_location = f"{user_folder}/{cleaned_db_filename}"
    compound_location = f"{user_folder}/{compound_filename}"
    predicted_actives_location = f"{user_folder}/{predicted_actives_filename}"
    database_predictions =  f"{user_folder}/{database_predictions_filename}"
    with open(met_location, "wb+") as met_object:
        met_object.write(met_file.file.read())
    with open(compound_location, "wb+") as compound_object:
        compound_object.write(compound_file.file.read())
    config = configparser.ConfigParser()
    config.read('configuration_file.ini')
    # Update a value in the configuration file
    config['TRAINING_DATASETS']['chembl_file'] = met_location
    config['TRAINING_DATASETS']['cleaned_data'] = cleaned_db_location
    config['TRAINING_DATASETS']['predicted_actives'] = predicted_actives_location
    config['MODE']['db_to_screen'] = compound_location
    config['MODE']['screening_output'] = database_predictions
    # Write changes to the configuration file
    with open(f"{user_folder}/configuration_file.ini", 'w') as configfile:
        config.write(configfile)
    print("File updated")
    # run_pyRMD(f"{user_folder}/configuration_file.ini", user_folder)
    subprocess.run(["python", "pyrmd.py", f"{user_folder}/configuration_file.ini"])
    # Get memory usage and CPU usage
    process = psutil.Process(os.getpid())
    mem_usage = process.memory_info().rss / 1024 / 1024
    cpu_usage = process.cpu_percent()
    # Return the contents of the output file
    with open(database_predictions, "r") as output_file_object:
        output_file_contents = output_file_object.read()

        
    os.remove(met_location)
    os.remove(compound_location)
    os.remove(database_predictions)
    os.remove(cleaned_db_location)
    os.remove(predicted_actives_location)
    os.remove(f"{user_folder}/configuration_file.ini")
    os.rmdir(user_folder)
        
    end_time = time.time()
    return {"output_file_contents": output_file_contents, "elapsed_time": end_time - start_time, "memory_usage": mem_usage, "cpu_usage": cpu_usage}



