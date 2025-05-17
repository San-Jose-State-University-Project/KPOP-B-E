from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import pickle
import os
import shutil

# 쿠키 저장 경로
COOKIES_PATH = "spotify_cookies.pkl"
# 다운로드 경로
DOWNLOAD_DIR = "/Users/pdh/Desktop/Project/spofity/global_/downloaded_spotify_files"

def save_cookies_after_manual_login():
    """사용자 수동 로그인 후 쿠키 저장"""
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={os.path.expanduser('~')}/.spotify_profile")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://charts.spotify.com/")

    print("수동으로 로그인하세요. (Google 또는 이메일 인증 포함)")
    input("로그인 완료 후 Enter 키를 누르세요...")

    with open(COOKIES_PATH, "wb") as f:
        pickle.dump(driver.get_cookies(), f)

    print("쿠키 저장 완료")
    driver.quit()

def create_driver_with_cookies() -> webdriver.Chrome:
    """쿠키를 불러와 로그인 유지된 driver 반환"""
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": DOWNLOAD_DIR}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://charts.spotify.com/")

    if not os.path.exists(COOKIES_PATH):
        raise FileNotFoundError("쿠키 파일이 없습니다. 먼저 save_cookies_after_manual_login()을 실행하세요.")

    with open(COOKIES_PATH, "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception:
                pass

    driver.get("https://charts.spotify.com/")
    return driver

def close_cookie_banner(driver):
    """쿠키 배너가 있으면 닫기"""
    try:
        close_btn = driver.find_element(By.CLASS_NAME, "onetrust-close-btn-handler")
        close_btn.click()
        print("쿠키 배너 닫기 완료")
        time.sleep(1)
    except NoSuchElementException:
        print("ℹ쿠키 배너 없음 또는 이미 닫힘")

def wait_for_download_and_rename(download_dir, new_filename, timeout=15):
    """다운로드 폴더에서 .crdownload 종료까지 대기 후 파일명 변경"""
    start_time = time.time()
    downloaded_file = None

    while time.time() - start_time < timeout:
        files = os.listdir(download_dir)
        csv_files = [f for f in files if f.endswith(".csv") and not f.startswith(".")]
        if csv_files:
            downloaded_file = csv_files[0]
            break
        time.sleep(1)

    if not downloaded_file:
        raise TimeoutError("⚠다운로드된 CSV 파일을 찾지 못했습니다.")

    src = os.path.join(download_dir, downloaded_file)
    dst = os.path.join(download_dir, new_filename)
    shutil.move(src, dst)
    print(f"📁 저장 완료: {dst}")
    return dst

def fetch_korea_chart_by_date(driver, target_date: str, chart_type="daily"):
    """특정 날짜 차트 접속 후 다운로드 버튼 클릭"""
    chart_url = f"https://charts.spotify.com/charts/view/regional-kr-{chart_type}/{target_date}"
    driver.get(chart_url)
    time.sleep(3)

    close_cookie_banner(driver)

    try:
        download_button = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[3]/div/div/div[2]/span/span/button')
        download_button.click()
        print(f"[{target_date}] 다운로드 버튼 클릭 완료")
    except Exception as e:
        print(f"[{target_date}] 다운로드 실패: {e}")

def crawl_one_day(date_str: str, chart_type="daily"):
    """지정된 날짜 하루만 다운로드"""
    driver = create_driver_with_cookies()
    fetch_korea_chart_by_date(driver, date_str, chart_type=chart_type)
    print("다운로드 대기 중...")
    try:
        filename = f"spotify_kr_{chart_type}_{date_str}.csv"
        wait_for_download_and_rename(DOWNLOAD_DIR, filename)
    except Exception as e:
        print(f"파일 저장 실패: {e}")
    driver.quit()

if __name__ == "__main__":
    print("🚀 Spotify KR Chart Downloader 시작")

    # 최초 1회만 실행
    save_cookies_after_manual_login()

    # 원하는 날짜 하루만 다운로드
    crawl_one_day(date_str="2025-05-13", chart_type="daily")
