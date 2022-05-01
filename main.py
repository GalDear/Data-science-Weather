# This is a sample Python script.
import time

import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def test():
    driver = webdriver.Chrome('C:/Users/yuval/PycharmProjects/Data-science-Weather/chromedriver/chromedriver')
    df = pd.DataFrame([], columns=["year", "month", "day", "temp", "humidity", "windspeed", "precipitation"])
    df_row_count=1

    # switch temp from fahrenheit to celsius
    driver.get(f"https://www.wunderground.com/history/monthly/us/ny/new-york-city/KLGA/date/2000-1")
    settings = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "wuSettings")))
    settings.click()
    time.sleep(2)
    celsius = driver.find_element(By.XPATH, '//*[@id="wuSettings-quick"]/div/a[2]').click()

    for year in range(2000,2022):
        for month in range(1,13):
            driver.get(f"https://www.wunderground.com/history/monthly/us/ny/new-york-city/KLGA/date/{year}-{month}")
            table_id= WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "days")))
            data = table_id.find_elements(By.TAG_NAME, "table") # get all of the rows in the table
            num_of_days = len(data[1].find_elements(By.TAG_NAME, "tr"))

            for i in range(1,num_of_days):
                day = data[0].find_elements(By.TAG_NAME, "tr")[i].text
                temp = data[1].find_elements(By.TAG_NAME, "tr")[i].text.split(' ')[1]
                humidity = data[3].find_elements(By.TAG_NAME, "tr")[i].text.split(' ')[1]
                windspeed = data[4].find_elements(By.TAG_NAME, "tr")[i].text.split(' ')[1]
                precipitation = data[6].find_elements(By.TAG_NAME, "tr")[i].text
                day_data = [year,month,day,temp,humidity,windspeed,precipitation]
                df.loc[df_row_count] = day_data
                df_row_count+=1
    driver.quit()
    print(df)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
