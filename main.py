import cv2 as cv
import numpy as np
import os
import pyautogui
import pytesseract
import time
from PIL import Image, ImageTk
import tkinter as tk

import itertools
import os
import shutil
import threading
import time
import sys
from pynput.keyboard import Key, Controller as kb
from pynput.mouse import Button, Controller as mousy
import pygetwindow as gw
import random
import math
from playsound import playsound


import win32gui, win32ui, win32con

hwnd = None
class WindowCapture:

    # properties
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

   
    # constructor
    def __init__(self, window_name=None):
        global hwnd

        # find the handle for the window we want to capture.
        # if no window name is given, capture the entire screen
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            if hwnd == None:
                windows = []
                def callback(hwnd, windows):
                    window_text = win32gui.GetWindowText(hwnd)
                    class_name = win32gui.GetClassName(hwnd)
                    if window_name in window_text or window_name in class_name:
                        windows.append((hwnd, window_text, class_name))

                win32gui.EnumWindows(callback, windows)
                for hwnd, window_text, class_name in windows:
                    print("Window Handle:", hwnd)
                    print("Window Title:", window_text)
                    print("Class Name:", class_name)
                    print()
                    self.hwnd = hwnd

                print(self.hwnd)

                if not self.hwnd:
                    raise Exception('Window not found: {}'.format(window_name))
            else:
                self.hwnd = hwnd

        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        if not window_name is None:
            # account for the window border and titlebar and cut them off
            border_pixels = 8
            titlebar_pixels = 30
            self.w = self.w - (border_pixels * 2)
            self.h = self.h - titlebar_pixels - border_pixels
            self.cropped_x = border_pixels
            self.cropped_y = titlebar_pixels

            # set the cropped coordinates offset so we can translate screenshot
            # images into actual screen positions
            self.offset_x = window_rect[0] + self.cropped_x
            self.offset_y = window_rect[1] + self.cropped_y

    def get_screenshot(self):

        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        #dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # drop the alpha channel, or cv.matchTemplate() will throw an error like:
        #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type() 
        #   && _img.dims() <= 2 in function 'cv::matchTemplate'
        img = img[...,:3]

        # make image C_CONTIGUOUS to avoid errors that look like:
        #   File ... in draw_rectangles
        #   TypeError: an integer is required (got type tuple)
        # see the discussion here:
        # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
        img = np.ascontiguousarray(img)

        return img

    # find the name of the window you're interested in.
    # once you have it, update window_capture()
    # https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
    @staticmethod
    def list_window_names():
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the __init__ constructor.
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)    

keyboard = kb()
mouse = mousy()
db_window = None
def sendHotkey(hotkey):
    global db_window
    if db_window == None:
        db_window = gw.getWindowsWithTitle('Dragon Ball Legend')[0]
    withSpin = False
    if hotkey == 'spin':
        withSpin = True

    if db_window:
        if hotkey == 'F3':
             hotkey = Key.f3
        elif hotkey == 'F5':
             hotkey = Key.f5
        elif hotkey == 'F11':
             hotkey = Key.f11
        elif hotkey =='F1':
             hotkey = Key.f1
        elif hotkey == 'F2':
             hotkey = Key.f2
        elif hotkey == 'F10':
             hotkey = Key.f10
        elif hotkey == 'q':
             hotkey = 'q'
        elif hotkey == 'stop':
             stop_keys = [Key.down, Key.up, Key.right, Key.left]
             hotkey = random.choice(stop_keys)

        #db_window.restore()
        try:
            db_window.show()
            print('show')
            db_window.activate()
            if withSpin:

                keyboard.press(Key.ctrl_l)
                delay = random.uniform(15, 45)  # Generate a random number between 0 and 10
                time.sleep(delay/1000)  # Sleep for the amount of seconds generated

                keyboard.press(Key.up)
                delay = random.uniform(15, 45)  # Generate a random number between 0 and 10
                time.sleep(delay/1000)  # Sleep for the amount of seconds generated
                keyboard.release(Key.up)

                delay = random.uniform(15, 25)  # Generate a random number between 0 and 10
                time.sleep(delay/1000)  # Sleep for the amount of seconds generated

                keyboard.press(Key.down)
                delay = random.uniform(15, 45)  # Generate a random number between 0 and 10
                time.sleep(delay/1000)  # Sleep for the amount of seconds generated
                keyboard.release(Key.down)

                keyboard.release(Key.ctrl_l)

            else:
                keyboard.press(hotkey)
                delay = random.uniform(15, 45)  # Generate a random number between 0 and 10
                time.sleep(delay/1000)  # Sleep for the amount of seconds generated
                keyboard.release(hotkey)
        except Exception as err:
            print(err)
            pass

  
def is_within_range(location, maxDistance):
    center_x = 960
    center_y = 416

    x, y = location  # Unpack the tuple into x and y coordinates

    distance = max(abs(center_x - x), abs(center_y - y))
    print('distance is ->: ' + str(distance))

    return distance <= maxDistance
import psutil

lastMobTimestamp = None
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"
lastClickTimestamp = None
howManyMobs = 0
def recognize(image_path, screenshot_image, screenshot_image_gray, thread_name, message_queue):
    # if 'mobs' in image_path:
    #     print(image_path)
    global mouse
    global keyboard
    global howManyMobs
    global current_index
    global lastClickTimestamp
    global lastMobTimestamp

    differenceBetweenLastMobFound = None
    wasSalka = False
    wasMouseClick = False
    current_mouse_position = mouse.position
    #print(image_path)
    # object = cv.imread(image_path, cv.IMREAD_UNCHANGED)
    object = imagesByImagePath[image_path]

    result = cv.matchTemplate(screenshot_image, object, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

    image_name = image_path.split('/')[-1]
    
    if 'waypoint' in image_path:
        #print(image_path)
        #print(max_val)
        pass

    if 'mob' in image_path:
        #print('Best match: %s' % str(max_val))
        pass
    

    threshold = 0.5
    if 'full' in image_path:
         threshold = 0.98

    if 'missing' in image_path:
         threshold = 0.99
         return

    if 'missing_mana' in image_path:
        threshold = 0.92
        return
    
    if 'mobs' in image_path:
        threshold = 0.69

    if 'map_center' in image_path:
        threshold = 0.95

    if '_waypoint' in image_path:
        threshold = 0.85
        #print(image_path)
        #print('before retry')
        #print(max_val)

    if 'msgcheck' in image_path:
        threshold = 0.72

    
    
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))
    random.shuffle(locations)

    #print(locations)
    # if '_waypoint' in image_path and not locations and (lastClickTimestamp == None or time.time() - lastClickTimestamp >= 15):
    #     for x in range(3):
    #         #print('retry')
    #         screenshot_image = screenshot(thread_name)
    #         result = cv.matchTemplate(screenshot_image, object, cv.TM_CCOEFF_NORMED)
    #         min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    #         #print('after retry -> ' + str(max_val))
    #         if max_val > threshold:
    #             print('success retry!!!')
    #             locations = np.where(result >= threshold)
    #             locations = list(zip(*locations[::-1]))
    #             random.shuffle(locations)q
    #             break

    # if '_waypoint' in image_path and not locations:
    #     if str(current_index) + '_' in image_path:
    #         current_index = current_index + 1

    #     if current_index >= len(waypoints_reference):
    #         current_index = 1

    if locations:
        if 'msgcheck':
            print(max_val)
            print('MSG CHECK!!!')
        
        needle_w = object.shape[1]
        needle_h = object.shape[0]
        line_color = (0, 255, 0)  # Green color for lines
        line_type = cv.LINE_4

        folder_name = os.path.dirname(image_path)  # Extract the folder name
        folder_name = os.path.basename(folder_name)
        if 'mob' in folder_name:
           #print('mob found!')
           pass

        existing_text_points = []

        for loc in locations:

            if 'msgcheck' in image_path:
                #playsound('alarm.wav')
                os.startfile('alarm.wav')
                sendHotkey('q')

            if 'waypoint' in image_path and (lastClickTimestamp == None or time.time() - lastClickTimestamp >= 10):

                awaiting_no_mobs = message_queue.get()
                
                if 'map_center' in image_name:
                    sendHotkey('stop')
                    
                    top_left = loc
                    middle_x = top_left[0] + needle_w // 2
                    middle_y = top_left[1] + needle_h // 2

                    middle_y = middle_y + 23

                    middle_point = (middle_x, middle_y)

                    delay = random.uniform(200, 225)  # Generate a random number between 0 and 10

                    mouse.position = middle_point
                    time.sleep(delay/1000) 
                    mouse.press(Button.left )
                    
                    time.sleep(delay/1000)
                    mouse.release(Button.left)
                    
                    time.sleep(delay/1000)

                    middle_point = (middle_x + 23, middle_y + 24)
                    mouse.position = middle_point

                    time.sleep(delay/1000)
                    mouse.press(Button.left)
                    time.sleep(delay/1000)
                    mouse.release(Button.left)
                    time.sleep(delay/1000)

                    mouse.press(Button.left)
                    time.sleep(delay/1000)
                    mouse.release(Button.left)
                    time.sleep(delay/1000)

                    #mouse.position = current_mouse_position
                    #wasMouseClick = True

                #if 'waypoint' in image_name and str(current_index) + '_' in image_path:
                if 'waypoint' in image_name and random.choice([False, True, False]):
                    print(image_name)
                    print(max_val)

                    # current_index = current_index + 1
                    # if current_index >= len(waypoints_reference):
                    #     current_index = 1

                    if not wasMouseClick:
                        lastClickTimestamp = time.time()
                        top_left = loc
                        middle_x = top_left[0] + needle_w // 2
                        middle_y = top_left[1] + needle_h // 2

                        middle_y = middle_y + 21

                        middle_point = (middle_x, middle_y)
                        
                        mouse.position = middle_point

                        delay = random.uniform(125, 255)  # Generate a random number between 0 and 10
                        time.sleep(delay/1000)  # Sleep for the amount of seconds generated
        
                        mouse.press(Button.left)
                        delay = random.uniform(125, 255)  # Generate a random number between 0 and 10
                        time.sleep(delay/1000)  # Sleep for the amount of seconds generated
                        mouse.release(Button.left)
                        wasMouseClick = True

                        #mouse.position = current_mouse_position
                        
                    else:
                        pass



                    #print('clicking waypoint!')

                    #print(image_name)
                    #if not wasMouseClick and random.choice([True, False]):
                    
            # Determine the box positions
            top_left = loc
            bottom_right = (top_left[0] + needle_w, top_left[1] + needle_h)
            
           
            
            # Draw the box with green color
            cv.rectangle(screenshot_image, top_left, bottom_right, line_color, line_type)

            middle_x = top_left[0] + needle_w // 2
            middle_y = top_left[1] + needle_h // 2

            middle_point = (middle_x, middle_y)
            #print(middle_point)


            if any(abs(middle_x - existing_x) <= 20 and abs(middle_y - existing_y) <= 20 for existing_x, existing_y in existing_text_points):
                continue  # Skip this middle point

            existing_text_points.append((middle_x, middle_y))  # Add the current middle point to existing text points

            font = cv.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_thickness = 2
            font_color = (0, 255, 0)  # White color
            hotkey = ''


            if 'mobs' in folder_name:
                
                 if is_within_range(middle_point, 600):
                     print('that ^ was hit')
                     wasSalka = True

                 hotkey = 'F1'
                 folder_name = folder_name.split('/')[-1] + ' (' + str(max_val) +')'
                 howManyMobs = len(existing_text_points)
                 #print('howManyMobs? ' + str(howManyMobs))

            elif 'furie' in folder_name:
                 hotkey = 'F11'
                 folder_name = folder_name.split('/')[-1] + ' (' + hotkey +')'

            text_size, _ = cv.getTextSize(folder_name, font, font_scale, font_thickness)

            x = middle_point[0]
            y = middle_point[1] - 10

            # Calculate the position to place the text
            text_x = x - int(text_size[0] / 2) + 75
            text_y = y + int(text_size[1] / 2) - 50
            # Draw the text with green color
            cv.putText(screenshot_image, folder_name, (text_x, text_y), font, font_scale, font_color, font_thickness)
            cv.putText(screenshot_image, folder_name, (text_x + 2, text_y - 2), font, font_scale, (0,0,0), font_thickness)
            update_tkinker('update_' + str(thread_name), screenshot_image)

            if wasSalka:
                 if wasSalka:
                    
                    lastMobTimestamp = time.time()


                    sendHotkey('F1')
                    delay = random.uniform(100, 215)  # Generate a random number between 0 and 10
                    time.sleep((555+delay) / 1000)  # Sleep for the amount of seconds generated

                    #time.sleep(0.8 + (delay/1000))

                    # time.sleep(0.4)
                    # sendHotkey('F1')
            else:
               pass

            if wasSalka or wasMouseClick:
                #print('returning....')
                return True
    else:
        if 'mobs' in image_path:
            if lastMobTimestamp == None:
                if message_queue.empty():
                    message_queue.put(time.time())
            else:
                differenceBetweenLastMobFound = time.time() - lastMobTimestamp
                print('difference is : ' + str(differenceBetweenLastMobFound))

            if message_queue.empty() and differenceBetweenLastMobFound != None and differenceBetweenLastMobFound > 3:
                print('sending to queue!')
                #sendHotkey('F10')
                message_queue.put(time.time())
        pass
        #print('Needle not found.')

   
        


window_width = 1200
window_height = 600
def on_close():
    print('on close function')
    global root
    global threads
    # global instance
    # if player is not None:
    #     player.stop()
    #     player.get_media().release()
    #     player.release()
    #     player.get_instance().release()
    print(threads)
    for speech_thread in threads:
        if speech_thread.is_alive():
            speech_thread.terminate()
    #root.destroy()
    sys.exit(1)

import os

folder_path = 'assets'
folder_files_dict = {}
imagesByImagePath = {}

for root, dirs, files in os.walk(folder_path):
    if root != folder_path:  # Exclude the 'assets' folder itself
        folder_name = os.path.relpath(root, folder_path)
        folder_files_dict[folder_name] = []
        for file in files:
            if 'xd_map_center' not in file:
                image_path = os.path.join(root, file).replace('\\', '/')
                folder_files_dict[folder_name].append(image_path)
                imagesByImagePath[image_path] = cv.imread(image_path, cv.IMREAD_UNCHANGED)
                
#print(folder_files_dict)

from PIL import ImageGrab
def capture_rectangle(left, upper, right, lower):
    # Capture the screen region within the specified rectangle
    image = None
    try:
        image = ImageGrab.grab(bbox=(left, upper, right, lower))
    except:
        pass
    
    return image

import re
def remove_non_numbers(text):
    pattern = r'\D'  # Regular expression pattern to match non-numeric characters
    result = re.sub(pattern, '', text)
    return result

def get_value_by_cooridantes(left, upper, right, lower):
    hp_screenshot = capture_rectangle(left, upper, right, lower)
    if hp_screenshot == None:
        return 100
    
    custom_config = r'--psm 7 --oem 1 -c tessedit_char_whitelist=0123456789'
    text = pytesseract.image_to_string(hp_screenshot, config=custom_config)

    try:
         
        if text.strip() == '':
            return 100
        else:
            first_three_letters = text[:2] if len(text) >= 2 else ''
            return int(first_three_letters)
    except:
        return 100
    
energyRoom = False
iteration = 0
def heal():
    global energyRoom, iteration
    #time.sleep(0.5)
    if energyRoom is False:
        hp = get_value_by_cooridantes(1803,88,1826,98)
    else:
        time.sleep(0.17)
    #print('hp: ' + str(hp))
    if energyRoom is False:
        if (energyRoom == False and hp != 10 and hp != 100) or (energyRoom and hp != 10 and hp < 70):
                print('hp!')
                sendHotkey('F3')
                if energyRoom == False:
                    sendHotkey('F5')


            #time.sleep(0.1)
            # if energyRoom is False:
            #     sendHotkey('F3')

    if energyRoom:
        iteration = iteration + 1
        
        print('iteration ->' + str(iteration))
        if iteration >= 75:
            sendHotkey('F3')
            iteration = 0
            sendHotkey('spin')
            time.sleep(1.5)
            sendHotkey('F2')

                
    if energyRoom is False:
        mana = get_value_by_cooridantes(1804,107,1826,116)
        print(mana)
        if (mana != 10 and mana != 100 and mana < 60):
                sendHotkey('F5')
                print('mana!')

def screenshot(thread_name):
    wincap = WindowCapture('Dragon Ball Legend')
    screenshot = wincap.get_screenshot()
    #screenshot = pyautogui.screenshot()
    screenshot_image = screenshot
    if 'waypoint' in thread_name:
        #cv.imwrite('wtf2.png', screenshot_image)
        pass
    screenshot_image_gray = screenshot
    update_tkinker('update_' + str(thread_name), screenshot_image)
    return screenshot_image

from msvcrt import getch
import os
import signal

def custom_sort(item):
    if any(char.isdigit() for char in item):
        return (1, item)
    else:
        return (0, item)
    


def combine_arrays_in_dict(dictionary):
    result = []
    for key in dictionary:
        result.extend(dictionary[key])
    return result

filtered_dict = None
waypoints_reference = []
current_index = 1
def listen(thread_name, message_queue):
    #time.sleep(2)
    global db_window
    if db_window == None:
        db_window = gw.getWindowsWithTitle('Dragon Ball Legend')[0]
    global folder_files_dict
    global img
    global canvas
    global loopFiles
    global filtered_dict
    global waypoints_reference

    if filtered_dict == None:
        #filtered_dict = {key: value for key, value in folder_files_dict.items() if thread_name in key}
        filtered_dict = {key: sorted(value, key=custom_sort) for key, value in folder_files_dict.items() if thread_name in key}
        print('filtered dict:')
        print(filtered_dict)
        if 'waypoint' in thread_name:
            #total_length = sum(len(value) for value in filtered_dict.values())
            waypoints_reference = combine_arrays_in_dict(filtered_dict)
        
        print('thread name -> ' + thread_name)

    while True:

        if thread_name == 'smooth':
            screenshot(thread_name)
            continue

        if 'heal' in thread_name:
            #print('heal check...')
            heal()
        else:    
            for folder, files in filtered_dict.items():
                #print('current folder ' + str(folder))
                for image_path in files:
                    #print('current image ' + str(image_path))

                    screenshot_image = screenshot(thread_name)
                    image_name = image_path.split('/')[-1]
                    if 'waypoint' in image_name:
                        screenshot_image = screenshot(thread_name)

                    #print(image_path)


                    response = recognize(image_path, screenshot_image, None, thread_name, message_queue)

                    if response == True:
                        break
                        #heal()

                    global howManyMobs
                    howManyMobs = 0


       
def update_tkinker(file_name, screenshot_image):
    global img
    global canvas
    global loopFiles
    file_name = file_name + '.jpg'
    if not 'mob' in file_name:
        return

    # cv.imwrite(file_name, screenshot_image)
    # tk_image  = Image.open(file_name)
    # tk_image = tk_image.resize((window_width, window_height), Image.ANTIALIAS)
    # render = ImageTk.PhotoImage(tk_image)

    pil_image = Image.fromarray(cv.cvtColor(screenshot_image, cv.COLOR_BGR2RGB))

    # Resize the PIL Image
    resized_image = pil_image.resize((window_width, window_height), Image.ANTIALIAS)

    # Convert PIL Image to Tkinter ImageTk format
    render = ImageTk.PhotoImage(resized_image)

    canvas.create_image(0, 0, anchor=tk.NW, image=render)
    canvas.update()

root = tk.Tk()
root.attributes("-topmost", False) 
root.title("PROJECT DICK LAURENT IS DEAD")
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen
x = (ws/2) - (window_width/2)
y = (hs/2) - (window_height/2)
x = -x - 1000
y = -y + 250

root.geometry('%dx%d+%d+%d' % (window_width, window_height, x, y))

root.protocol("WM_DELETE_WINDOW", on_close)
canvas = tk.Canvas(root, width=window_width, height=window_height, highlightthickness=0)
canvas.pack()
threads = []



from multiprocessing import Process, Event, Queue
if __name__ == '__main__':

    #WindowCapture.list_window_names()
    message_queue = Queue()

    event = Event()

    heal_thread = Process(target=listen, args=('heal', message_queue, ))
   
    mob_thread = Process(target=listen, args=('mob', message_queue, ))

    cavebot_thread = Process(target=listen, args=('waypoint', message_queue, ))

    alarm_thread = Process(target=listen, args=('msgcheck', message_queue, ))

    threads.append(heal_thread)
    threads.append(mob_thread)
    threads.append(cavebot_thread)
    threads.append(alarm_thread)

    for thread in threads:
        thread.start()

    from pynput.keyboard import Listener

    def on_press(key):
        #print("Key pressed: {0}".format(key))
        key = str(key).replace("'", '')
        if str(key) == 'q':
            print('terminating')
            on_close()

    def on_release(key):
        pass

    with Listener(on_press=on_press, on_release=on_release) as listener:
        print('click q to exit(1)')
        listener.join()

    #root.mainloop()
