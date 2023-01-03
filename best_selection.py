import requests
from bs4 import BeautifulSoup
import copy
import re
from soupsieve import select_one
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
import os
import time

url = "https://book.naver.com/bestsell/bestseller_list.naver?cp=kyobo&cate=total&indexCount=&type=list&page="
headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36", "Accept-Language" : "ko-KR,ko"}


#headlees
options = webdriver.ChromeOptions()
options.headless = True
options.add_argument("window-size=1920x1080")
browser = webdriver.Chrome(r"C:\Users\kimchiwha\Desktop\2022년\SW프로그래밍\22_1_SW\project\selenium\chromedriver_win32\chromedriver.exe", options=options)

browser.maximize_window()




def best_sellers(pageNum):
    
    
    #교보문고 베스트셀러 정보 가져오기
    res = requests.get(url + str(pageNum), headers=headers)
    res.raise_for_status()
    gyobo = BeautifulSoup(res.text, "lxml") #res문서를 lxml을 통해서 beautifulsoup으로
     
    #베스트셀러 제목
    hello_title = gyobo.find_all("a", attrs = {"class" : "N=a:bel.title"})
    
    #베스트셀러 저자 (class 명이 txt_block txt_block2인 것도 있어서 lambda 사용함)
    hello_info = gyobo.find_all(lambda tag: tag.name == 'dd' and tag.get('class') == ['txt_block'])

    
    #베스트셀러 도서관에 검색
    for i in range(0,25):
        title_ = hello_title[i].get_text().strip()
        writer_ = hello_info[i].a.get_text().strip()

        browser.get("https://lib.nyj.go.kr/jyy/menu/10071/program/30018/plusSearchDetail.do") #페이지 열기
        browser.find_element(By.ID, "searchKeyword1").send_keys(title_) #도서명 입력
        browser.find_element(By.ID, "searchKeyword2").send_keys(writer_) #작가 입력
        select = Select(browser.find_element(By.ID, "searchRecordCount")) #50개 노출
        select.select_by_value("50")
        browser.find_element(By.ID, "searchBtn").click() #책 검색 클릭
        
        
        # 도서관 책 상황 수집
        dasanlib = BeautifulSoup(browser.page_source, "lxml")
        booklist_ = dasanlib.find_all("p", attrs = {"class" : "txt"})     
        

                
        # 대출, 예약, 청구기호 수집
        for beableto in booklist_:
            takeout = beableto.find_all("b")
            takeout_str = ", ".join(map(str,takeout)) #takeout list를 str로
        
            
        # 예약 가능 여부 수집 
            reservation = dasanlib.select_one("#searchForm > ul > li > div.bookStateBar.clearfix > p > span")
            reservation_str = "".join(map(str, reservation)) #list에서 str로 변환

                     
        # 대출 가능 여부 수집
            #"대출가능"이라는 말이 있으면 -> can_borrow = 3, cannot_borrow = -1
            #"대출불가능"이라는 말이 있으면 -> can_borrow = -1, cannot_borrow = 3
            can_borrow = takeout_str.find("대출가능")
            cannot_borrow = takeout_str.find("대출불가")

        # 청구기호   
            bookNum = dasanlib.select_one("#searchForm > ul > li > dl > dd.data > span > strong").get_text()
        
        
        #분야: 도서관 청구기호 이용하여 분류함 (청구기호가 아동~ 이렇게 시작하는 것도 있어서ㅜ)
        
            ONLY_bookNum_list = re.findall("\d+", bookNum) # 청구기호에서 숫자만 뽑기 (list임)
            bookNum3_int = list(map(int, ONLY_bookNum_list)) # str리스트를 int리스트로 변환
            # print(ONLY_bookNum_list) -> ['814', '7', '82']
            # print(type(ONLY_bookNum_list)) -> list       
                
                
            if 000<=bookNum3_int[0]<100:
                genre = "총류"
            if 100<=bookNum3_int[0]<200:
                genre = "철학"
            if 200<=bookNum3_int[0]<300:
                genre = "종교"
            if 300<=bookNum3_int[0]<400:
                genre = "사회과학"
            if 400<=bookNum3_int[0]<500:
                genre = "자연과학"                
            if 500<=bookNum3_int[0]<600:
                genre = "기술과학"                
            if 600<=bookNum3_int[0]<700:
                genre = "예술"
            if 700<=bookNum3_int[0]<800:
                genre = "언어"
            if 800<=bookNum3_int[0]<900:
                genre = "문학"
            if 900<=bookNum3_int[0]<1000:
                genre = "역사"

                               
                


# 출력 조건:
    # 1. 도서관이 보유하고 있어야 함.
        # 2. 대출이 가능해야 함.
            # 3. 대출이 불가능하다면, 예약이 가능해야 함. 즉, 예약자가 5명 미만 (5명 이상이라면, 예약 불가)



                #대출 가능한지
                    
            if can_borrow == 3: #can_borrow가 3이면 가능함
                rank_ = (25*pageNum-24) + i
                print(f"\033[34m[대출가능]\033[0m\n{rank_}위: ({genre}) {title_} | {writer_} ------------ {bookNum}")
                print("")
                break #같은 책 여러 권 있을 때, 대출 가능한 것 찾아버리면 멈추기
            
            else: #can_borrow가 3이 아니면 불가능함
                rank_ = (25*pageNum-24) + i
                
                
                #예약 가능한지 (대출불가능한 것 중)
                
                    #예약자가 5명이라 불가능 할 때
                if reservation.find("5") == True:
                    break   #대출도 안 되고, 예약도 안 되면 출력 안 함
                
                    #예약자가 5명 미만이라 가능할 때
                else:
                    print(f"\033[33m[예약가능]\033[0m\n{rank_}위: ({genre}) {title_} | {writer_} ------------ {bookNum}")
                    print("")
                    # break
                    
                
            

        
        
for pageNum in range(1,7):        
    best_sellers(pageNum)
    

    
