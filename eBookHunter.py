import requests
import json
import sys
import os
from datetime import datetime
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pymysql
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
import threading
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class eBookHunter:

    def __init__(self, onupload_username, onupload_password, start_page, end_page, home_url):
        self.home_url = home_url
        self.onupload_username = onupload_username
        self.onupload_password = onupload_password
        self.start_page = int(start_page)
        self.end_page = int(end_page)

    def homepage(self):
        try:
            chrome_options = Options()

            chrome_options.add_argument("--start-maximized")
            self.ebook_hunter_file_dir = os.getcwd() + "\\hunter books files"
            self.ebook_hunter_img_dir = os.getcwd() + "\\hunter books imgs"

            if os.path.exists(self.ebook_hunter_file_dir) == False:
                os.makedirs(self.ebook_hunter_file_dir)

            if os.path.exists(self.ebook_hunter_img_dir) == False:
                os.makedirs(self.ebook_hunter_img_dir)

            chrome_options.add_experimental_option(
                'excludeSwitches', ['enable-logging'])
            prefs = {
                "download.default_directory": self.ebook_hunter_file_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing_for_trusted_sources_enabled": False,
                "safebrowsing.enabled": False,
                "plugins.always_open_pdf_externally": True
            }

            chrome_options.add_experimental_option("prefs", prefs)
            self.driver = webdriver.Chrome(
                options=chrome_options, service=Service(ChromeDriverManager().install()))
            self.driver.minimize_window()
            # self.driver.implicitly_wait(50)
            while True:
                try:
                    self.driver.get(self.home_url)
                    break
                except:
                    print("problem in getting home page")
                    time.sleep(1)
            time.sleep(30)
            # self.driver.implicitly_wait(10)
            # self.driver.set_page_load_timeout(5)
        except Exception as e:
            print("problem in homepage:", e)

    def insert_into_database(self, file_name, url_list, category, website):
        file_name = file_name.replace(".epub", "")
        wait_time = 3
        for sec in range(wait_time):
            try:
                con_Server = "localhost"
                con_username = "root"
                con_password = ""
                con_database = "bookdownloader"
                pdf_url = ""
                epub_url = ""
                for url in url_list:
                    if ".pdf" in url:
                        pdf_url = url
                    else:
                        epub_url = url

                insert_query = """INSERT INTO books
                    (name,category,epuburl,pdfurl,website)
                    VALUES(%s, %s, %s, %s,%s)"""

                conn = pymysql.connect(host=con_Server,
                                       user=con_username,
                                       password=con_password,
                                       database=con_database,
                                       cursorclass=pymysql.cursors.DictCursor)

                cursor = conn.cursor()

                cursor.execute(
                    insert_query, (file_name, category, epub_url, pdf_url, website))
                conn.commit()
                conn.close()
                break

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                line_num = exc_tb.tb_lineno
                print(
                    f"waiting for database to respond, seconds remaining {wait_time - sec}...")
                if sec == (wait_time - 1):
                    print(f"Inserting in database failed for file_name:{file_name} due to:" + str(
                        e) + " line_num:" + str(line_num))
                time.sleep(1)

    def uploade_files_and_getlink(self, username, password):
        try:
            try:

                self.driver.get("https://onuploads.com/login.html")
                self.driver.find_element(
                    By.XPATH, "//input[@name='login']").send_keys(username)
                self.driver.find_element(
                    By.XPATH, "//input[@name='password']").send_keys(password)
                self.driver.find_element(
                    By.XPATH, '//input[@type="submit"]').click()
            except:
                print("login is already done")
            while True:
                try:
                    self.driver.get("https://onuploads.com/?op=upload_form")
                    files = os.listdir(self.ebook_hunter_file_dir)
                    self.driver.find_element(By.ID, "file_0").send_keys(
                        self.ebook_hunter_file_dir+"\\"+files[0]+"\n" + self.ebook_hunter_file_dir+"\\"+files[1])
                    self.driver.execute_script(
                        "window.scrollTo(0,document.body.scrollHeight)")
                    self.driver.find_element(
                        By.XPATH, '//input[@name="upload"]').click()
                    break
                except:
                    time.sleep(1)

            while True:
                result = self.driver.find_element(By.TAG_NAME, 'h2').text
                if "Files Uploaded" in result:
                    break
                else:
                    time.sleep(2)

            urls = self.driver.find_element(
                By.XPATH, '//div[@class="box visible"]/textarea').text
            urls_list = urls.split("\n")
            print(urls_list)

            return urls_list

        except Exception as e:
            _, _, line_tb = sys.exc_info()
            line_num = line_tb.tb_lineno
            print("uploade_files_and_getlink:", e, "line_num:", line_num)

    def epub_to_pdf(self, epub_file):
        try:

            chrome_options = Options()
            prefs = {
                "download.default_directory": self.ebook_hunter_file_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing_for_trusted_sources_enabled": False,
                "safebrowsing.enabled": False,
                "plugins.always_open_pdf_externally": True
            }

            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_experimental_option(
                'excludeSwitches', ['enable-logging'])
            self.browser = webdriver.Chrome(
                options=chrome_options, service=Service(ChromeDriverManager().install()))
            self.browser.minimize_window()
            while True:
                try:
                    self.browser.get("https://www.pdf2go.com/epub-to-pdf")
                    time.sleep(5)
                    self.browser.find_element(By.ID, "fileUploadInput").send_keys(
                        self.ebook_hunter_file_dir+"\\"+epub_file)
                    time.sleep(5)
                    upload_status = self.browser.find_element(
                        By.XPATH, f"""//span[@title="{epub_file}"]""").text
                    if "canceled" not in upload_status and "failed" not in upload_status:
                        break

                except Exception as e:
                    _, _, line_tb = sys.exc_info()
                    line_num = line_tb.tb_lineno
                    print(line_num, e)
                    time.sleep(1)

            for tryy in range(2):
                try:
                    time.sleep(2)
                    self.browser.find_element(By.ID, "submitBtn").click()
                    break
                except:
                    time.sleep(1)

            epub_file = epub_file.split(".")
            epub_file.pop()
            file_name = ".".join(epub_file)+".pdf"

            while True:
                if os.path.exists(f"{self.ebook_hunter_file_dir}\\{file_name}"):
                    print(f"file:{file_name} found in dir")
                    self.browser.quit()
                    break
                else:
                    print(f"no file:{file_name} in dir")
                    time.sleep(2)

        except Exception as e:
            _, _, line_tb = sys.exc_info()
            line_num = line_tb.tb_lineno
            print("epub_to_pdf:", e, "line_num:", line_num)

    def main_func(self):
        try:
            self.homepage()
            total_pages = self.driver.find_elements(
                By.XPATH, "//div[@class='nav-links']/a")

            page_num = int(total_pages[-2].text.replace(",", ""))

            if self.end_page >= page_num:
                self.end_page = page_num
            if self.start_page <= 1:
                self.start_page = 1

            for page in range(self.start_page, self.end_page+1):
                book = 1
                for category in ["contemporary-romance", "paranormal-romance", "historical-romance", "suspense"]:
                    while True:
                        try:
                            self.driver.get(
                                f"https://www.ebookhunter.net/category/{category}/page/{page}/")
                            break
                        except:
                            time.sleep(1)

                    time.sleep(2)

                    books = self.driver.find_elements(
                        By.XPATH, "//h2[@class='title post-title']/a")
                    books_imgs = self.driver.find_elements(
                        By.XPATH, "//div[@class='post-img']/a/img")

                    books_urls = [url.get_attribute("href") for url in books]
                    books_imgs_url = [books_imgs[img_num].get_attribute(
                        "src") for img_num in range(0, 10)]

                    for book_url, img_url in zip(books_urls, books_imgs_url):

                        while True:
                            try:
                                self.driver.get(book_url)
                                writer = " BY " + self.driver.find_element(By.XPATH, "//h2[@style]").text.split(
                                    "BY")[-1].split("–")[0].strip().replace(".", "").replace(",", "")
                                self.driver.find_element(
                                    By.XPATH, "//p[@style='text-align: center;']/strong/a").click()
                                break
                            except:
                                time.sleep(1)
                        time.sleep(3)

                        file_to_convert = ""

                        while True:
                            downloaded_files = os.listdir(
                                self.ebook_hunter_file_dir)
                            for files in downloaded_files:
                                if "epub" in files and "crdownload" not in files:
                                    new_file_name = files.split(
                                        "epub")[0]+writer
                                    new_file_name=new_file_name.replace("_"," ")
                                    new_file_name = ''.join(
                                        s for s in new_file_name if s.isalnum() or s == " ")
                                    new_file_name = new_file_name.split()
                                    new_file_name = ' '.join(
                                        str_item for str_item in new_file_name)
                                    new_file_name = new_file_name + ".epub"
                                    os.rename(self.ebook_hunter_file_dir+"\\"+files,
                                              self.ebook_hunter_file_dir+"\\"+new_file_name)
                                    file_to_convert = new_file_name
                                    break
                            if file_to_convert != "":
                                break

                        img_name = file_to_convert.replace(" ", "").split(
                            ".epub")[0] + "PdfDownload" + ".jpg"

                        while True:
                            try:
                                res = requests.get(img_url)
                                break
                            except:
                                time.sleep(1)

                        with open(f"{self.ebook_hunter_img_dir}\\{img_name}", "wb") as file:
                            file.write(res.content)

                        self.epub_to_pdf(file_to_convert)

                        urls_list = self.uploade_files_and_getlink(
                            self.onupload_username, self.onupload_password)

                        self.insert_into_database(
                            file_name=file_to_convert, url_list=urls_list, category=category, website="www.ebookhunter.net/")
                        files_d = os.listdir(self.ebook_hunter_file_dir)
                        with open("check.txt", "w", encoding="utf-8") as f:
                            f.write(f"page:{page} book={book}")
                        book += 1
                        for fl in files_d:
                            os.remove(self.ebook_hunter_file_dir+"\\"+fl)

            self.driver.quit()
        except Exception as e:
            _, _, line_tb = sys.exc_info()
            line_num = line_tb.tb_lineno
            print("problem:", e, "line_num:", line_num)


class MainScreen(QDialog):
    def __init__(self):
        super(MainScreen, self).__init__()
        loadUi("main.ui", self)
        self.start_program.clicked.connect(self.process)

    def process(self):
        onupload_username = self.username.text()
        onupload_password = self.pasword.text()
        start_page = self.start_page.text()
        end_page = self.end_page.text()
        start = eBookHunter(onupload_username, onupload_password,
                            start_page, end_page, home_url="https://www.ebookhunter.net/")
        t = threading.Thread(target=lambda: start.main_func())
        t.daemon = True
        t.start()


app = QApplication(sys.argv)
welcome = MainScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setFixedWidth(400)
widget.setFixedHeight(300)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print('exiting')
