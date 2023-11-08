import os
import cv2
import time
import qrcode
import re,sys
import tempfile
import pyperclip
import threading
import numpy as np
from ChatBot.models import *
from selenium import webdriver
from django.contrib import messages
from asgiref.sync import sync_to_async
from selenium.webdriver.common.by import By
from django.shortcuts import render,redirect
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from django.contrib.auth import authenticate, login, logout 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from ChatBot.constants import DEFAULT_WAIT,MAIN_SEARCH_BAR__SEARCH_ICON,EXTRACT_SESSION,INJECT_SESSION,QR_CODE


def HomePage(request):
    return render(request,"Home.html")




def SignUpPage(request):
    if request.method == "POST":
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        email = request.POST['email']
        password = request.POST['password']
        conform_password = request.POST['confirmpassword']
        if email:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                messages.error(request,"Invalid email address")
        if password != conform_password:
            messages.error(request,"Password and Conform Password is does not match")
        else:
            check_user = CustomUser.objects.filter(email=email).exists()
            if check_user:
                messages.error(request,"User email alredy exits")
            else:
                if first_name  and last_name and email and password:
                    CustomUser.objects.create_user(email=email,first_name=first_name,last_name=last_name,password=password)
                    messages.success(request,"Create User Successfully")
                    return redirect("/login/")
                else:
                    messages.error(request,"All data are required.")
    return render(request,"signup.html")

def LoginPage(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                messages.error(request,"Invalid email or password.")
            if not user.is_active:
                messages.error('User account is inactive.')
            login(request, user)    
            messages.success(request,"Login Successfully.")
            return redirect("/")
        else:
            messages.error(request,"Both email and password are required.")
    return render(request,"login.html")

def LogOutPage(request):
    logout(request)
    messages.success(request,"Successfully Logout")
    return redirect("/")

def validate_digit_phone_number(request,value):
    if not re.match(r'^\d+$', value):
        return f'Phone number "{value}" must contain only digits.'
    if  len(value) != 10:
        return f'Phone number "{value}" must have exactly 10 digits.'
      
def validate_phone_numbers(request, phone_numbers):
    errors = []
    valid_phone_numbers = []

    if phone_numbers:
        phone_number_list = phone_numbers.split(",")
        for number in phone_number_list:
            error = validate_digit_phone_number(request, number)
            if error:
                errors.append(error)
            else:
                valid_phone_numbers.append(number)
                
    return errors, valid_phone_numbers

def _wait_for_presence_of_an_element(browser, selector):
    element = None
    try:
        element = WebDriverWait(browser, DEFAULT_WAIT).until(
            EC.presence_of_element_located(selector)
        )
    except:
        pass
    finally:
        return element




async def  send_message(phone_numbers,message_text,file_paths):
    try:
        profile_folder = 'Wtsp'
        user_home_dir = os.path.expanduser("~")
        CHROME_PROFILE_PATH = ''
        if os.name == 'nt': 
            CHROME_PROFILE_PATH = "user-data-dir="+os.path.join(user_home_dir, "AppData", "Local", "Google", "Chrome", "User Data", profile_folder)
        elif sys.platform.startswith('linux') or sys.platform == 'darwin':
            CHROME_PROFILE_PATH = "user-data-dir="+ os.path.join(user_home_dir, '.config','google-chrome', profile_folder)
        else:
            CHROME_PROFILE_PATH = "user-data-dir="+ os.path.join(user_home_dir, 'Library','Application Support','Google','Chrome', profile_folder)

        options = webdriver.ChromeOptions()
        options.add_argument(CHROME_PROFILE_PATH)
        options.add_argument("--headless")
        browser = webdriver.Chrome(options=options)

        browser.get("https://web.whatsapp.com/")
    
        _wait_for_presence_of_an_element(browser, MAIN_SEARCH_BAR__SEARCH_ICON)
        browser.execute_script(EXTRACT_SESSION)
        for phone_number in phone_numbers:
            # Construct the WhatsApp URL with the phone number
            whatsapp_url = f'https://web.whatsapp.com/send?phone={phone_number}'
            browser.get(whatsapp_url)
            if message_text:
                message = WebDriverWait(browser, 100).until(EC.element_to_be_clickable((By.XPATH, '//div[@title="Type a message"]')))
                for text in message_text:
                    action_chains = ActionChains(browser)
                    action_chains.context_click(message).perform()
                    pyperclip.copy(text)
                    message.send_keys(Keys.CONTROL, "v")
                    message.send_keys(Keys.ENTER)
                    time.sleep(0.5)

            # Loop through file paths and send files
            if file_paths:
                for file_path in file_paths:
                    attachment_button = WebDriverWait(browser, 100).until(EC.element_to_be_clickable((By.XPATH, '//div[@title="Attach"]')))
                    browser.execute_script("arguments[0].click();", attachment_button)

                    document_option = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@accept="*"]')))
                    document_option.send_keys(file_path)

                    time.sleep(40)

                    send_button = browser.find_element(By.XPATH, '//span[@data-icon="send"]')
                    send_button.click()
                    time.sleep(10)
        browser.quit()
        return True
    except Exception as e:
        print(e,"error is >>>>>>>>>>>>>>>>>>>>>>>")






@sync_to_async
def create_message(user_id, phone_numbers, filtered_list, message_files):
    for phone_data in phone_numbers:
        if filtered_list:
            for text_data in filtered_list:
                if message_files:
                    for file_data in message_files:
                        add_message = MessageModel.objects.create(user_name=user_id, phone_number=phone_data, message_file=file_data)
                        add_message.meessage = text_data
                        add_message.save()
                else:
                    add_message = MessageModel.objects.create(user_name=user_id, phone_number=phone_data)
                    add_message.meessage = text_data
                    add_message.save()
        else:
            if message_files:
                for file_data in message_files:
                    add_message = MessageModel.objects.create(user_name=user_id, phone_number=phone_data, message_file=file_data)
                    add_message.save()
        
    

@sync_to_async
def get_user_id(request):
    return request.user.id

@sync_to_async
def get_message_limit(user_id):
    return MessageModel.objects.filter(user_name=user_id).count()
    
async def SendMessage(request):
    if request.method == "POST":
        file_paths = []
        phone_numbers = request.POST['phonenumber']
        message_text = request.POST.getlist('messagetext',[])
        message_file = request.FILES.getlist('messagefile',[])
        filtered_list = [value for value in message_text if value is not None and value != '']
        if not phone_numbers:
            messages.error(request,"Phone Number is complesery")
        user_id = await get_user_id(request)
        if phone_numbers:
            check_message_limit = await get_message_limit(user_id)
            if check_message_limit > 1000:
                messages.error(request,"Your free message sending limit has been exceeded.")
            else:
                errors,valid_phone_numbers  = validate_phone_numbers(request, phone_numbers)
                if errors or valid_phone_numbers:
                    for error in errors:
                        messages.error(request, error)
                    if valid_phone_numbers:
                        if filtered_list or message_file:  
                            for  i  in message_file:
                                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                                    for chunk in i.chunks():
                                        temp_file.write(chunk)
                                    file_paths.append(temp_file.name)
                            response_data = await  send_message(valid_phone_numbers,filtered_list,file_paths)
                            if response_data:
                                await create_message(request.user, valid_phone_numbers, filtered_list, message_file)
                                messages.success(request,'Send message successfully')
                            else:
                                messages.error(request, 'Failed to send message')
                        else:
                            messages.error(request,"Message or file are required")
    return redirect("/") 