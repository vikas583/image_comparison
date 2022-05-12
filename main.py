import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from flask import Flask, request, jsonify
import json
from PIL import Image, ImageChops
import cv2
import imutils  


app = Flask(__name__)


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
    driver = webdriver.Chrome(executable_path='./chromedriver.exe',options=options)
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
    original = cv2.imread("./screenshots/20220512-160000.png")
    new = cv2.imread("./screenshots/20220512-160800.png")


    diff = original.copy()
    cv2.absdiff(original, new, diff)

    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
  
    #increasing the size of differences after that we can capture them all
    for i in range(0, 3):
        dilated = cv2.dilate(gray.copy(), None, iterations= i+ 1)

    (T, thresh) = cv2.threshold(dilated, 3, 255, cv2.THRESH_BINARY)
  
    # now we have to find contours in the binarized image
    cnts = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    for c in cnts:
     # nicely fiting a bounding box to the contour
     (x, y, w, h) = cv2.boundingRect(c)
     cv2.rectangle(new, (x, y), (x + w, y + h), (0, 255, 0), 2)
  
    #remove comments from below 2 lines if you want to
    #for viewing the image press any key to continue
    #simply write the identified changes to the disk
    cv2.imwrite("./screenshots/difference.png", new)

    return jsonify({"status": True, 'message': "Snapshot captured successfully!"})

app.run(port=5000)


