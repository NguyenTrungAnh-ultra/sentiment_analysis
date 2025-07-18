from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.actions.action_builder import ActionBuilder
import pandas as pd
import time
import os

# Tạo DF
folder_path = "./"
file_name = "vietstock_nhandinhthitruong.csv" 
# Kết hợp đường dẫn thư mục và tên file
file_path = os.path.join(folder_path, file_name)
# Kiểm tra xem file có tồn tại không
if os.path.isfile(file_path):
    print(f"File {file_name} tồn tại trong thư mục.")
    DF = pd.read_csv(file_path)
    DF.reset_index(drop=True, inplace=True)
else:
    print(f"File {file_name} không tồn tại trong thư mục.")
    columns = ['Datetime', 'Title', 'Brief']
    DF = pd.DataFrame(columns=columns)


data = [] # Lưu bài viết dưới dạng list để chuyển thành DataFrame
page = 1
start_time = time.time()


driver = webdriver.Chrome()
driver.get("https://vietstock.vn/nhan-dinh-phan-tich/nhan-dinh-thi-truong.htm")
while True:
        # Lấy dữ liệu trang page.
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "single_post.post_type12.type20.mb20.channelContent")) # Chờ elements xuất hiện
        )
        posts = driver.find_elements(By.CLASS_NAME, "single_post.post_type12.type20.mb20.channelContent") # Tìm elements
        print(f'Load page {page} success!')
            

        try:
            # Thêm post vào data
            for post in posts:
                information = post.text.split('\n')
                information = [val.strip() for val in information] # Loại bỏ khoảng trắng thừa
                data.append(information)
            print(f"Scrap page {page} FINISHED!")
            print(f"Total post:  {len(data)}")
            # Chuyển trang kế
            page += 1
            WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.LINK_TEXT, f'{page}'))
                        ) # Chờ nút xuất hiện
            next_page_button = driver.find_element(By.LINK_TEXT, f'{page}')
            driver.execute_script("arguments[0].click();", next_page_button) # Thực hiện Action qua trang
            time.sleep(5)
        except:
            print(f"Something went wrong at page {page} \n"
                    "or this is THE LAST page")
            page = 1
            driver.quit()
            columns = ['Datetime', 'Title', 'Brief']
            df = pd.DataFrame(data, columns=columns)

            if DF.empty:
                DF.reset_index(drop=True, inplace=True)
                df.reset_index(drop=True, inplace=True)
                DF = pd.concat([DF, df], ignore_index=False) 
                DF.to_csv("vietstock_nhandinhthitruong.csv", index=False)
            else:
                # Lọc các hàng không trùng lặp dựa trên cột 'Title'
                unique_rows = df[~df['Title'].isin(DF['Title'])]
                DF.reset_index(drop=True, inplace=True)
                df.reset_index(drop=True, inplace=True)
                DF = pd.concat([unique_rows, DF], ignore_index=False)
                DF.to_csv("vietstock_nhandinhthitruong.csv", index=False)

            end_time = time.time()
            break

columns = ['Datetime', 'Title', 'Brief']
df = pd.DataFrame(data, columns=columns)

if DF.empty:
    DF.reset_index(drop=True, inplace=True)
    df.reset_index(drop=True, inplace=True)
    DF = pd.concat([DF, df], ignore_index=False) 
    DF.to_csv("vietstock_nhandinhthitruong.csv", index=False)
else:
    # Lọc các hàng không trùng lặp dựa trên cột 'Title'
    unique_rows = df[~df['Title'].isin(DF['Title'])]
    DF.reset_index(drop=True, inplace=True)
    df.reset_index(drop=True, inplace=True)
    DF = pd.concat([unique_rows, DF], ignore_index=False)
    DF.to_csv("vietstock_nhandinhthitruong.csv", index=False)

end_time = time.time()
print(f"DF SHAPE: {DF.shape}")
print(f"Running time {end_time-start_time}")
print('Something went wrong!')