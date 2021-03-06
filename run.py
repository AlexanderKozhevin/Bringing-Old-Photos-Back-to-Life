# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import argparse
import shutil

import json
import urllib.request

import cv2
import imageio
import os
import numpy as np
from PIL import Image
import scipy.misc
from PIL import ImageFont
from PIL import ImageDraw 
import urllib.request
import threading
import datetime
from google.cloud import storage
import requests
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/content/drive/My Drive/colorize_space/googlekey.json"
file_name = ""
sub_folder = ""

storage_client = storage.Client()
bucket_name = 'colorize_jobs'

def upload_blob(source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    
    
if __name__ == "__main__":
    
    r = requests.post("https://colorize.cc/worker/get_photo_tasks_good", data={'token': 'k2ljkljfls;adjflwlkj43jflk3jqflkGenius'})

    data = json.loads(r.text)
    if (len(data)>0):
      name = data[0]["name"]
      file_name = name
      print(data[0]["email"])
      print(data[0]["img_source"] + "/"  + data[0]["name"])
      sub_folder = data[0]["img_source"]
      link = 'https://storage.googleapis.com/colorize_jobs/' + data[0]["img_source"] + "/"  + data[0]["name"]
      print(link)
      try:
        urllib.request.urlretrieve(link, '/content/photo_restoration/test_images/old/'+name)
        print(link)
        myimage = cv2.imread("/content/photo_restoration/test_images/old/"+ name)
        height = myimage.shape[0]
        wid = myimage.shape[1]
        print("xui pizda")
        print(height)
        print(wid)
        print(height >= 1200)

        if height >= 1200:
          print("resize suka")
          ratioon = height/1300
          h2 = int(myimage.shape[0] / ratioon)
          w2 = int(myimage.shape[1] / ratioon)
          dimmm = (w2, h2)
          print("matrix size")
          print(w2 * h2)
          resized = cv2.resize(myimage, dimmm, interpolation = cv2.INTER_AREA)
          cv2.imwrite("/content/photo_restoration/test_images/old/"+name,resized)
          print("saved dick resize")

        myimage = cv2.imread("/content/photo_restoration/test_images/old/"+ name)
        height = myimage.shape[0]
        wid = myimage.shape[1]

        if wid >= 2000:
          print("resize suka")
          ratioon = wid/2000
          h2 = int(myimage.shape[0] / ratioon)
          w2 = int(myimage.shape[1] / ratioon)
          dimmm = (w2, h2)
          print("matrix size")
          print(w2 * h2)
          resized = cv2.resize(myimage, dimmm, interpolation = cv2.INTER_AREA)
          cv2.imwrite("/content/photo_restoration/test_images/old/"+name,resized)
          print("saved dick resize")

        myimage = cv2.imread("/content/photo_restoration/test_images/old/"+ name)
        print("FINAL SIEZE #################")
        print("FINAL SIEZE #################")
        print("FINAL SIEZE #################")
        print("FINAL SIEZE #################")
        height = myimage.shape[0]
        wid = myimage.shape[1]  
        print(wid)
        print(height)
        print("FINAL SIEZE #################")




        parser = argparse.ArgumentParser()
        parser.add_argument("--input_folder", type=str, default="", help="Test images")
        parser.add_argument(
            "--output_folder",
            type=str,
            default="/home/jingliao/ziyuwan/workspace/codes/PAMI/outputs",
            help="Restored images, please use the absolute path",
        )
        parser.add_argument("--GPU", type=str, default="6,7", help="0,1,2")
        parser.add_argument(
            "--checkpoint_name", type=str, default="Setting_9_epoch_100", help="choose which checkpoint"
        )
        parser.add_argument("--with_scratch", action="store_true")
        opts = parser.parse_args()

        gpu1 = opts.GPU

        if not os.path.exists(opts.output_folder):
            os.makedirs(opts.output_folder)




        main_environment = os.getcwd()

        ## Stage 1: Overall Quality Improve
        print("Running Stage 1: Overall restoration")
        os.chdir("./Global")
        stage_1_input_dir = opts.input_folder
        stage_1_output_dir = os.path.join(opts.output_folder, "stage_1_restore_output")
        if not os.path.exists(stage_1_output_dir):
            os.makedirs(stage_1_output_dir)

        if not opts.with_scratch:
            stage_1_command = (
                "python test.py --test_mode Full --Quality_restore --test_input "
                + stage_1_input_dir
                + " --outputs_dir "
                + stage_1_output_dir
                + " --gpu_ids "
                + gpu1
            )
            os.system(stage_1_command)
        else:

            mask_dir = os.path.join(stage_1_output_dir, "masks")
            new_input = os.path.join(mask_dir, "input")
            new_mask = os.path.join(mask_dir, "mask")
            stage_1_command_1 = (
                "python detection.py --test_path "
                + stage_1_input_dir
                + " --output_dir "
                + mask_dir
                + " --input_size full_size"
            )
            stage_1_command_2 = (
                "python test.py --Scratch_and_Quality_restore --test_input "
                + new_input
                + " --test_mask "
                + new_mask
                + " --outputs_dir "
                + stage_1_output_dir
            )

            os.system(stage_1_command_1)
            os.system(stage_1_command_2)

        ## Solve the case when there is no face in the old photo
        stage_1_results = os.path.join(stage_1_output_dir, "restored_image")
        stage_4_output_dir = os.path.join(opts.output_folder, "final_output")
        if not os.path.exists(stage_4_output_dir):
            os.makedirs(stage_4_output_dir)
        for x in os.listdir(stage_1_results):
            img_dir = os.path.join(stage_1_results, x)
            shutil.copy(img_dir, stage_4_output_dir)

        print("Finish Stage 1 ...")
        print("\n")

        ## Stage 2: Face Detection

        print("Running Stage 2: Face Detection")
        os.chdir(".././Face_Detection")
        stage_2_input_dir = os.path.join(stage_1_output_dir, "restored_image")
        stage_2_output_dir = os.path.join(opts.output_folder, "stage_2_detection_output")
        if not os.path.exists(stage_2_output_dir):
            os.makedirs(stage_2_output_dir)
        stage_2_command = (
            "python detect_all_dlib.py --url " + stage_2_input_dir + " --save_url " + stage_2_output_dir
        )
        os.system(stage_2_command)
        print("Finish Stage 2 ...")
        print("\n")

        ## Stage 3: Face Restore
        print("Running Stage 3: Face Enhancement")
        os.chdir(".././Face_Enhancement")
        stage_3_input_mask = "./"
        stage_3_input_face = stage_2_output_dir
        stage_3_output_dir = os.path.join(opts.output_folder, "stage_3_face_output")
        if not os.path.exists(stage_3_output_dir):
            os.makedirs(stage_3_output_dir)
        stage_3_command = (
            "python test_face.py --old_face_folder "
            + stage_3_input_face
            + " --old_face_label_folder "
            + stage_3_input_mask
            + " --tensorboard_log --name "
            + opts.checkpoint_name
            + " --gpu_ids "
            + gpu1
            + " --load_size 256 --label_nc 18 --no_instance --preprocess_mode resize --batchSize 4 --results_dir "
            + stage_3_output_dir
            + " --no_parsing_map"
        )
        os.system(stage_3_command)
        print("Finish Stage 3 ...")
        print("\n")

        ## Stage 4: Warp back
        print("Running Stage 4: Blending")
        os.chdir(".././Face_Detection")
        stage_4_input_image_dir = os.path.join(stage_1_output_dir, "restored_image")
        stage_4_input_face_dir = os.path.join(stage_3_output_dir, "each_img")
        stage_4_output_dir = os.path.join(opts.output_folder, "final_output")
        if not os.path.exists(stage_4_output_dir):
            os.makedirs(stage_4_output_dir)
        stage_4_command = (
            "python align_warp_back_multiple_dlib.py --origin_url "
            + stage_4_input_image_dir
            + " --replace_url "
            + stage_4_input_face_dir
            + " --save_url "
            + stage_4_output_dir
        )
        os.system(stage_4_command)
        print("Finish Stage 4 ...")
        print("\n")

        print("All the processing is done. Please check the results.")
        finalname = file_name.replace(".jpg", ".png")
        #finalname2 = file_name



        is_good = os.path.isfile('/content/photo_restoration/test_images/output/final_output/' + finalname)
        print(is_good)
        if (is_good):
            link3 = 'https://storage.googleapis.com/colorize_jobs/' + data[0]["img_source"] + "/stage_"  + data[0]["name"]
            print(link3)
            im = Image.open('/content/photo_restoration/test_images/output/final_output/' + finalname)
            rgb_im = im.convert('RGB')
            rgb_im.save('/content/photo_restoration/test_images/output/final_output/' + file_name)          
            upload_blob('/content/photo_restoration/test_images/output/final_output/' + file_name, sub_folder + "/" + "stage_" +file_name)
            r4 = requests.post("https://colorize.cc/worker/stage2_job_done", data={'token': 'k2ljkljfls;adjflwlkj43jflk3jqflkGenius', 'name': file_name})
        else:
            r3 = requests.post("https://colorize.cc/worker/stage2_job_fail", data={'token': 'k2ljkljfls;adjflwlkj43jflk3jqflkGenius', 'name': file_name})
        print("FINAL PART")
        print(is_good)
      except Exception as e:
        r333 = requests.post("https://colorize.cc/worker/stage2_job_fail", data={'token': 'k2ljkljfls;adjflwlkj43jflk3jqflkGenius', 'name': file_name})
        print(' - - - - - cant process the image')
        ssss = str(e)
        print(ssss)

