from selenium import webdriver
from selenium.webdriver.common.by import By
import re
from bs4 import BeautifulSoup
import pymongo


browser = webdriver.Chrome()
def search():
    browser.get("https://www.taobao.com/")
    browser.find_element(By.CSS_SELECTOR,"#q").send_keys("美食")
    browser.find_element(By.CSS_SELECTOR,"#J_TSearchForm > div.search-button > button").click()
    total=browser.find_element(By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > div.total").text
    total=int(re.findall("(\d+)",total)[0])

    get_products()
    return total

def next_page(page_number):
    input=browser.find_element(By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > div.form > input")
    input.clear()
    input.send_keys(page_number)
    submit=browser.find_element(By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit")
    submit.click()
    get_products()

def get_products():
    page=browser.page_source
    soup=BeautifulSoup(page,"lxml")
    items=soup.select('div[data-category="auctions"]')
    print(len(items))

    for item in items:
        print(item["data-index"])

        image=item.select('div .img')[0].get("src")
        price=item.select("strong")[0].text
        shop=item.select('div[class="shop"]')[0].text.strip()
        location=item.select('div[class="location"]')[0].text
        deal=item.select('div[class="deal-cnt"]')[0].text[:-3]
        product={
            "image":image,
            "price":price,
            "shop":shop,
            "location":location,
            "deal":deal
        }
        print(product)
        save_to_mongodb(product)



def save_to_mongodb(product):
    conn = pymongo.MongoClient("192.168.11.129",27017)
    db = conn["test"]  #连接mydb数据库，没有则自动创建
    collec=db.taobao
    if collec.insert(product):
       print("inserted into MongoDB")
       return  True
    return False
if __name__=="__main__":
    total=search()
    # for i in range(2,total+1):
    #     try:
    #         next_page(i)
    #     except:
    #         browser.refresh()
    #         next_page(i)
    browser.close()