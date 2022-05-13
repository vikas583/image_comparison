# from crypt import methods
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from flask import Flask, request, jsonify
import json
from PIL import Image, ImageChops, ImageDraw
import cv2
import imutils  
import numpy as np
import argparse
from skimage.metrics import structural_similarity as compare_ssim




app = Flask(__name__)
MIN_AREA = 200

@app.route('/')
def index():
  return 'Server Works!'
  
@app.route('/greet')
def say_hello():
  return 'Hello from Server'

@app.route('/api/task', methods=['POST'])
def create_task():
    
    options = webdriver.ChromeOptions()
    options.headless = True
    webdriver.DesiredCapabilities.CHROME['acceptSslCerts'] = True
    driver = webdriver.Chrome(executable_path='./chromedriver.exe',options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source":
            "const newProto = navigator.__proto__;"
            "delete newProto.webdriver;"
            "navigator.__proto__ = newProto;"
    })
    URL = request.form.get('website_url')
    driver.get(URL)
    S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
    driver.set_window_size(S('Width'),S('Height')) # May need manual adjustment                                                                                                                
    
    driver.find_element_by_tag_name('body').screenshot('./screenshots/'+time.strftime("%Y%m%d-%H%M%S")+'.png')
    driver.quit()
    return jsonify({"status": True, 'message': "Snapshot captured successfully!"})


@app.route('/api/spot-the-difference', methods=['GET'])
def sportTheDifferenceBetweenImages():

    #get the images you want to compare.
    original = cv2.imread("./screenshots/20220513-125747.png")
    new = cv2.imread("./screenshots/20220513-131152.png")


    diff = original.copy()
    cv2.absdiff(original, new, diff)

    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
  
    #increasing the size of differences after that we can capture them all
    for i in range(0, 3):
        dilated = cv2.dilate(gray.copy(), None, iterations= i+ 1)

    (T, thresh) = cv2.threshold(dilated, 3, 255, cv2.THRESH_BINARY)
  
    # now we have to find contours in the binarized image
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    for c in cnts:
     # nicely fiting a bounding box to the contour
    #  print(c)
     (x, y, w, h) = cv2.boundingRect(c)
    #  print(w*h)
     if w*h > MIN_AREA:
      cv2.rectangle(new, (x, y), (x + w, y + h), (0, 255, 0), 2)

    #remove comments from below 2 lines if you want to
    #for viewing the image press any key to continue
    #simply write the identified changes to the disk
    cv2.imwrite("./screenshots/difference.png", new)

    return jsonify({"status": True, 'message': "Snapshot captured successfully!"})


@app.route('/api/spot-the-difference-2', methods=['GET'])
def sportTheDifferenceBetweenImagesMethod2():
    #get the images you want to compare.
    original = r"./screenshots/20220512-160000.png"
    new = r"./screenshots/20220512-160800.png"

    data1 = Image.open(original)
    data2 = Image.open(new)
    data3 = data1.convert("L")
    data4 = data2.convert("L")

    raw1 = data3.getdata()
    raw2 = data4.getdata()

    #Subtracting pixels
    diff_pix = np.subtract(raw1,raw2)

    #Creating a new image with only the different pixels
    img_final = Image.new("L",(602,756))
    img_final.putdata(diff_pix)

    #Calculating box coordinates
    c=0
    for i in diff_pix:
        if i > 25:
            break
        else:
            c+=1

    x10 = c%602
    y10 = c//602

    #Drawing the box
    x1,y1,x2,y2 = x10-30, y10-20, x10+30, y10+20
    Drawer = ImageDraw.Draw(data2)
    Drawer.rectangle((x1, y1, x2, y2), outline="red", width=3)

    #Saving the image with box
    f3 = r'./screenshots/macfd3.bmp'
    data2.show()
    data2.save(f3)

@app.route('/api/spot-the-diference-method-3', methods=['GET'])
def sportTheDifferenceBetweenImagesMethod3():
  # load the two input images
  imageA = cv2.imread("./screenshots/20220512-160000.png")
  imageB = cv2.imread("./screenshots/20220512-160800.png")
  # convert the images to grayscale
  grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
  grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

  # compute the Structural Similarity Index (SSIM) between the two
  # images, ensuring that the difference image is returned
  (score, diff) = compare_ssim(grayA, grayB, full=True)
  diff = (diff * 255).astype("uint8")
  print("SSIM: {}".format(score))
  # threshold the difference image, followed by finding contours to
  # obtain the regions of the two input images that differ
  thresh = cv2.threshold(diff, 0, 255,
	cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
  cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
  cnts = imutils.grab_contours(cnts)
  # loop over the contours
  for c in cnts:
      # compute the bounding box of the contour and then draw the
      # bounding box on both input images to represent where the two
      # images differ
      (x, y, w, h) = cv2.boundingRect(c)
      cv2.rectangle(imageA, (x, y), (x + w, y + h), (0, 0, 255), 2)
      cv2.rectangle(imageB, (x, y), (x + w, y + h), (0, 0, 255), 2)
  # show the output images
  cv2.imshow("Original", imageA)
  cv2.imshow("Modified", imageB)
  cv2.imshow("Diff", diff)
  cv2.imshow("Thresh", thresh)
  cv2.waitKey(0)

app.run(port=5000)


