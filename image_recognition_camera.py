from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import cv2
import time
import math
from numpy import float32



def floatToString(floatnumber:float32) -> str:
    stringNumber:str = ""
    whole:int = math.floor(floatnumber)
    frac:int = 0
    digits:float = float(floatnumber % 1)
    digitsTimes100:float = float(digits) * float(100.0)
    if digitsTimes100 is not None:
        frac = math.floor(digitsTimes100)
    stringNumber = str(whole)+"."+str(frac)
    return stringNumber

def recognition():
    model=load_model("imagemodel.h5")
    cap = cv2.VideoCapture(0)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    
    data_classes = ["Enoshima", "Fujisaki", "Fukawa", "Ikusaba", "Kirigiri", "Ludenberg", "Togami"]

    # Capture frame-by-frame
    ret, frame = cap.read()
    
    img_name = "image_recognition_photos/image_recognition_{}.jpg".format(timestr)
    try:
        cv2.imwrite(img_name, frame)
        print("Log: {} written!".format(img_name))
    except:
        print("Log: {} could not be written.".format(img_name))
    
    cap.release()
    cv2.destroyAllWindows()
    #aoi_img = "resources/identifycos/test/cos_aoi/aoi_test_001.jpg"
    #toko_img = "resources/identifycos/test/cos_toko/toko_test_004.jpg"
    
    img=image.load_img(img_name,target_size=(224,224))
    x=image.img_to_array(img)
    x=np.expand_dims(x,axis=0)
    images=np.vstack([x])
    pred=model.predict(images,batch_size=1) 
    
    for i in range(len(pred)):
        for j in range(len(pred[i])):
            print(data_classes[j], pred[i][j])
           
    maximum_index = np.where(pred == np.amax(pred))
    maximum_index_val = sum(maximum_index[1])
    
    #print('Returned tuple of arrays :', maximum_index)
    #print('List of Indices of maximum element :', maximum_index_val)
    
    print("Log: Recognized as:", data_classes[maximum_index_val])
    return data_classes[maximum_index_val]