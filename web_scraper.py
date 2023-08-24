import os 
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
import sys
import random
from bs4 import BeautifulSoup


start_tick = time.perf_counter()
stop_tick = 0
newsletters = [
    "https://tldr.tech/tech/archives",
    "https://tldr.tech/webdev/archives",
    "https://tldr.tech/ai/archives",
    "https://tldr.tech/crypto/archives",
    # "https://reactnewsletter.com/issues",
]


options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(0.5)

def get_articles_from_tldr(link):
    global driver
    type_of_article = link.split("/")[-2]
    # driver.get("https://tldr.tech/tech/2023-08-07")
    driver.get(link)
    wait_for_page_to_load()

    # time.sleep(3)
    # data = driver.page_source
    # # print(data)
    # with open("output.html", "w", encoding='utf-8') as f:
    #     f.write(data)
    article_script = driver.find_element(by=By.ID, value="__NEXT_DATA__")
    # print(f"article_script: {article_script}")
    # print(f"article_script.text: {article_script.text}")
    articles = article_script.get_attribute("innerHTML")
    with open(f"{type_of_article}_articles.json", "w", encoding='utf-8') as f:
        f.write(articles)

    articles = json.loads(articles)
    return articles["props"]["pageProps"]["stories"]



def wait_for_page_to_load():
    pass

def get_latest_articles(link):
    # get the latest by looking at dates
    # print(link)
    type_of_article = link.split("/")[-1]
    category = link.split("/")[-2]
    if "." in type_of_article:
        type_of_article = type_of_article.split(".")[0]
    driver.get(link)
    news_script = driver.find_element(by=By.ID, value="__NEXT_DATA__")
    news = news_script.get_attribute("innerHTML")
    news = json.loads(news)
    # print(news["props"]["pageProps"]["campaigns"])
    stories = news["props"]["pageProps"]["campaigns"]
    # for story in stories:
    #     print(story["date"])
    latest = stories[0]["date"]
    return f"{category}/{latest}"

    # with open(f"archives_{type_of_article}.json", "w", encoding="utf-8") as f:
    #     f.write(str(news["props"]["pageProps"]))


# latest_link = get_latest_articles("https://tldr.tech/tech/archives")
# latest_link = "https://tldr.tech/" + latest_link
# print(latest_link)
# get_articles_from_tldr("https://tldr.tech/tech/archives")

stories = []

for link in newsletters:
    if "tldr.tech" in link:
        print(link)
        latest_link = "https://tldr.tech/" + get_latest_articles(link)
        print(latest_link)
        time.sleep(random.uniform(1.0,2.0))
        stories = stories + get_articles_from_tldr(latest_link)
        time.sleep(random.uniform(1.0,3.0))

driver.quit()
stop_tick = time.perf_counter()
print(f"Scraping: {stop_tick-start_tick}s")

def remove_duplicates(stories):
    result = []
    ids = []
    for story in stories:
        if story["id"] not in ids:
            ids.append(story["id"])
            result.append(story)
        
    return result

def order_by_newsletter(stories):
    reordered = {}
    for story in stories:
        if story["newsletter"] not in reordered:
            reordered[story["newsletter"]] = []
        reordered[story["newsletter"]].append(story)
    
    return reordered

stories = remove_duplicates(stories)
stories_by_type = order_by_newsletter(stories)
print(stories_by_type)
with open('./index.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

for news_type in stories_by_type:
    header2 = soup.new_tag("h2")
    header2.string = news_type.upper()
    header2["style"] = "color: lightsalmon;"
    soup.html.body.append(header2)

    for sample in stories_by_type[news_type]:
        print(sample)
        new_div = soup.new_tag("div")

        header3 = soup.new_tag("h3")
        link = soup.new_tag("a")
        link.string = sample['title']
        link['href'] = sample['url']
        link['style'] = "color: lightgreen;"
        header3.append(link)

        description = soup.new_tag("p")
        description.string = sample['tldr']
        new_div.append(header3)
        new_div.append(description)

        soup.html.body.append(new_div)
    top_padding = soup.new_tag("div")
    top_padding["style"] = "height: 5vh;"
    soup.html.body.append(top_padding)
    divider = soup.new_tag("hr")
    divider["style"] = "border-top: 3px solid #bbb;"
    soup.html.body.append(divider)
    bottom_padding = soup.new_tag("div")
    bottom_padding["style"] = "height: 5vh;"
    soup.html.body.append(bottom_padding)

# print(soup.prettify())
with open("scraper_result.html", "w", encoding="utf-8") as f:
    f.write(soup.prettify())