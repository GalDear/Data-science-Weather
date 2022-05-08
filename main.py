# This is a sample Python script.
import time

import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
Shahar = "/Users/yuval/PycharmProjects/Data-science-Weather/chromedriver/chromedriver"
Gal = '/Users/gal.bachar/git_wa/HIT/Data-science-Weather/chromedriver/chromedriver'


def data_collect():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome("C:/Users/yuval/PycharmProjects/Data-science-Weather/chromedriver/chromedriver")#, options=chrome_options)
    df = pd.DataFrame([], columns=["year", "month", "day", "temp", "humidity", "windspeed", "precipitation"])
    df_row_count=1

    # switch temp from fahrenheit to celsius
    driver.get(f"https://www.wunderground.com/history/monthly/us/ny/new-york-city/KLGA/date/2000-1")
    settings = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "wuSettings")))
    settings.click()
    time.sleep(2)
    celsius = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                              '//*[@id="wuSettings-quick"]/div/a[2]')))
    celsius.click()

    for year in range(2000,2023):
        for month in range(1,13):
            driver.get(f"https://www.wunderground.com/history/monthly/us/ny/new-york-city/KLGA/date/{year}-{month}")
            try:
                table_id= WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "days")))
                data = table_id.find_elements(By.TAG_NAME, "table") # get all of the rows in the table
                num_of_days = len(data[1].find_elements(By.TAG_NAME, "tr"))

                for i in range(1,num_of_days):
                    day = int(data[0].find_elements(By.TAG_NAME, "tr")[i].text)
                    temp = float(data[1].find_elements(By.TAG_NAME, "tr")[i].text.split(' ')[1])
                    humidity = float(data[3].find_elements(By.TAG_NAME, "tr")[i].text.split(' ')[1])
                    windspeed = float(data[4].find_elements(By.TAG_NAME, "tr")[i].text.split(' ')[1])
                    precipitation = float(data[6].find_elements(By.TAG_NAME, "tr")[i].text)
                    day_data = [year,month,day,temp,humidity,windspeed,precipitation]
                    df.loc[df_row_count] = day_data
                    df_row_count += 1
            except Exception as e:
                print(f"cloud not get {year}-{month} data: {e}")

    driver.quit()
    df.to_csv('~/Documents/nyc_weather.csv',index=False) #for debugging
    return df


def normalize_data(data_df, good_weather_values):
    norm_df = data_df.copy()
    for i in norm_df.columns:
        if i not in ['year', 'month', 'day']:
            good_min = good_weather_values[i][0]
            good_max = good_weather_values[i][1]
            diff_min = good_weather_values[i][0] - norm_df[i].min()
            diff_max = norm_df[i].max() - good_weather_values[i][1]
            norm_df.loc[(norm_df[i] < good_min), i] = 1 - ((good_min - norm_df[i]) / diff_min)
            norm_df.loc[(norm_df[i] > good_max), i] = 1 - ((norm_df[i] - good_max) / diff_max)
            norm_df.loc[(norm_df[i] <= good_max) & (norm_df[i] >= good_min), i] = 1
    # norm_df.to_csv('~/Documents/nyc_weather_norm.csv', index=False)  # for debugging
    return norm_df



def calculate_values(row, good_weather_values):
    if (row[3] >= good_weather_values["temp"][0]) and (row[3] <= good_weather_values["temp"][1]):  # checking temp
        temp_value = 1
    elif row[3] < good_weather_values["temp"][0]:
        temp_value = row[3] / good_weather_values["temp"][0]
    elif row[3] > good_weather_values["temp"][1]:
        temp_value = good_weather_values["temp"][1] / row[3]

    if (row[4] >= good_weather_values["humidity"][0]) and (row[4] <= good_weather_values["humidity"][1]):  # checking humidity
        humidity_value = 1.0
    elif row[4] < good_weather_values["humidity"][0]:
        humidity_value = row[4] / good_weather_values["humidity"][0]
    elif row[4] > good_weather_values["humidity"][1]:
        humidity_value = good_weather_values["humidity"][1]/ row[4]

    if (row[5] >= good_weather_values["windspeed"][0]) and (row[5] <= good_weather_values["windspeed"][1]):  # checking windspeed
        windspeed_value = 1
    elif row[5] < good_weather_values["windspeed"][0]:
        windspeed_value = row[5] / good_weather_values["windspeed"][0]
    elif row[5] > good_weather_values["windspeed"][1]:
        windspeed_value = good_weather_values["windspeed"][1] / row[5]

    if (row[6] >= good_weather_values["precipitation"][0]) and (row[6] <= good_weather_values["precipitation"][1]):  # checking precipitation
        precipitation_value = 1
    elif row[6] < good_weather_values["precipitation"][0]:
        precipitation_value = row[6] / good_weather_values["precipitation"][0]
    elif row[6] > good_weather_values["precipitation"][1]:
        precipitation_value = good_weather_values["precipitation"][1] / row[6]

    return (precipitation_value + windspeed_value + humidity_value + temp_value) / 4


def pleasant(data_df, good_weather_values):
    plea_df = data_df.copy()
    plea_df.insert(7,"Pleasant Day", 0)
    for index, row in plea_df.iterrows():
        pleasant_value = calculate_values(row, good_weather_values)
        plea_df.loc[index, ["Pleasant Day"]] = pleasant_value
        #if pleasant_value >= 0.8:
        #    plea_df.loc[index, ["Pleasant Day"]] = pleasant_value
    return plea_df

if __name__ == '__main__':
    # nice weather:
    # temp 18-25
    # humidity 30-50%
    # windspeed 0-7
    # precipitation 0 - 0.5
    good_weather_values = {'temp': [18,25], 'humidity':[30,50],'windspeed':[4,20], 'precipitation':[0,0.5]}
    # df = data_collect()
    df = pd.read_csv('~/Documents/nyc_weather.csv') # for debugging
    norm_df = normalize_data(df, good_weather_values)
    df_with_plea = pleasant(df, good_weather_values)


    count = 0       # counting pleasant days
    for row in df_with_plea.iterrows():
        if(row[1][7] >= 0.85):
            count+=1
    print(count)
