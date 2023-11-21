# import os
# user_home_dir = os.path.expanduser("~")
# print(user_home_dir)

# import os
# import shutil

# def find_chrome_path():
#     chrome_executables = ['chrome.exe', 'google-chrome', 'chromium', 'chromium-browser']
#     possible_paths = [
#         os.path.join(os.getenv('PROGRAMFILES(X86)'), 'Google', 'Chrome', 'Application'),
#         os.path.join(os.getenv('PROGRAMFILES'), 'Google', 'Chrome', 'Application'),
#         os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'Application'),
#     ]
#     for path in possible_paths:
#         for exe_name in chrome_executables:
#             chrome_path = os.path.join(path, exe_name)
#             if os.path.exists(chrome_path):
#                 return chrome_path
#     return None

# chrome_path = find_chrome_path()
# if chrome_path:
#     print(f"Google Chrome executable found at: {chrome_path}")
# else:
#     print("Google Chrome executable not found.")


import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # Specify the path to your Chrome executable

url_to_open = "https://www.google.com"
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path), 1)
webbrowser.get('chrome').open(url_to_open)




