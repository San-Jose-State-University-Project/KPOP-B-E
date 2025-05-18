import os
import time
import pickle
import shutil
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class DownloadChart:

    def __init__(self, user):
        self.COOKIES_PATH = "spotify_cookies.pkl"
        self.DOWNLOAD_DIR = f"/Users/{user}/Desktop/Project/spofity/global_/downloaded_spotify_files"
        self.options = webdriver.ChromeOptions()

    def save_cookies_after_manual_login(self):
        self.options.add_argument(f"--user-data-dir={os.path.expanduser('~')}/.spotify_profile")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        driver.get("https://charts.spotify.com/")
        print("수동으로 로그인하세요.")
        input("로그인 완료 후 Enter 키를 누르세요...")
        with open(self.COOKIES_PATH, "wb") as f:
            pickle.dump(driver.get_cookies(), f)
        print("쿠키 저장 완료")
        driver.quit()

    def create_driver_with_cookies(self) -> webdriver.Chrome:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        prefs = {"download.default_directory": self.DOWNLOAD_DIR}
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://charts.spotify.com/")
        if not os.path.exists(self.COOKIES_PATH):
            raise FileNotFoundError("쿠키 파일이 없습니다.")
        with open(self.COOKIES_PATH, "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except Exception:
                    pass
        driver.get("https://charts.spotify.com/")
        return driver

    def close_cookie_banner(self, driver):
        try:
            btn = driver.find_element(By.CLASS_NAME, "onetrust-close-btn-handler")
            btn.click()
            print("쿠키 배너 닫기 완료")
            time.sleep(1)
        except NoSuchElementException:
            print("쿠키 배너 없음")

    def wait_for_download_and_rename(self, download_dir, expected_partial_name, new_filename, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            for fname in os.listdir(download_dir):
                if fname.startswith(expected_partial_name) and fname.endswith(".csv"):
                    full_path = os.path.join(download_dir, fname)
                    dst_path = os.path.join(download_dir, new_filename)
                    shutil.move(full_path, dst_path)
                    print(f"📁 저장 완료: {dst_path}")
                    return dst_path
            time.sleep(1)
        raise TimeoutError("❌ 다운로드된 CSV 파일을 찾지 못했습니다.")

    def fetch_korea_chart_by_date(self, driver, target_date: str, chart_type="daily"):
        url = f"https://charts.spotify.com/charts/view/regional-kr-{chart_type}/{target_date}"
        driver.get(url)
        time.sleep(3)
        self.close_cookie_banner(driver)
        try:
            btn = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[3]/div/div/div[2]/span/span/button')
            btn.click()
            print(f"[{target_date}] 다운로드 버튼 클릭 완료")
        except Exception as e:
            print(f"[{target_date}] 다운로드 실패: {e}")

    def crawl_one_day(self, date_str: str, chart_type="daily"):
        """지정된 날짜 하루만 다운로드 (이미 있으면 생략)"""
        new_filename = f"spotify_kr_{chart_type}_{date_str}.csv"
        file_path = os.path.join(self.DOWNLOAD_DIR, new_filename)

        if os.path.exists(file_path):
            print(f"📁 이미 존재함, 다운로드 생략: {file_path}")
            return

        driver = self.create_driver_with_cookies()
        self.fetch_korea_chart_by_date(driver, date_str, chart_type=chart_type)
        print("다운로드 대기 중...")

        try:
            expected_name = f"regional-kr-{chart_type}-{date_str}"
            self.wait_for_download_and_rename(self.DOWNLOAD_DIR, expected_name, new_filename)
        except Exception as e:
            print(f"파일 저장 실패: {e}")
        time.sleep(3)
        driver.quit()

if __name__ == "__main__":
    print("🚀 Spotify KR Chart Downloader 시작")
    download_chart = DownloadChart("pdh")

    # download_chart.save_cookies_after_manual_login()  # 최초 1회만 실행
    download_chart.crawl_one_day(date_str="2025-05-16", chart_type="daily")
