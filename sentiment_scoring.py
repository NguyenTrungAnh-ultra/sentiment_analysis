# --- Code cập nhật ---
import pandas as pd
import time
import torch
from transformers import RobertaForSequenceClassification, AutoTokenizer
import re
from datetime import datetime

# (Giữ nguyên phần tải model và hàm pre_process)
print("Đang tải model và tokenizer...")
model_sentiment = RobertaForSequenceClassification.from_pretrained("wonrax/phobert-base-vietnamese-sentiment")
tokenizer = AutoTokenizer.from_pretrained("wonrax/phobert-base-vietnamese-sentiment", use_fast=False)
print("Tải model hoàn tất.")

# Hàm analyze_sentiment đã sửa đổi ở trên
def analyze_sentiment(sentence: str):
    # ... (code từ trên) ...
    if not isinstance(sentence, str) or not sentence.strip():
        return (None, None)
    labels = ["Negative", "Positive", "Neutral"]
    input_ids = torch.tensor([tokenizer.encode(sentence)])
    with torch.no_grad():
        out = model_sentiment(input_ids)
        probabilities = out.logits.softmax(dim=-1).tolist()
        predicted_index = torch.argmax(out.logits, dim=1).item()
        return (labels[predicted_index], probabilities)

def pre_process(df: pd.DataFrame):
    # ... (giữ nguyên hàm pre_process của bạn) ...
    regex_pattern = r'^(.*?):\s*(.*)$'
    extracted_cols = df['Title'].str.extract(regex_pattern)
    extracted_cols.columns = ['news_type', 'new_Title']
    extracted_cols['news_type'] = extracted_cols['news_type'].str.strip()
    extracted_cols['new_Title'] = extracted_cols['new_Title'].str.strip()
    df1 = pd.concat([df, extracted_cols], axis=1)
    df1 = df1.drop(columns=['Title'])
    df1 = df1.rename(columns={'new_Title': 'Title'})
    if 'Datetime' in df1.columns and 'Brief' in df1.columns:
        df1 = df1[['Datetime', 'news_type', 'Title', 'Brief']]
    df1.dropna(subset=['news_type', 'Title'], inplace=True)
    return df1

def extract_date_or_today(text_string: str) -> str:
    """
    Trích xuất ngày tháng (DD/MM) từ một chuỗi.
    - Nếu tìm thấy, nó sẽ trả về ngày đó với năm hiện tại.
    - Nếu không tìm thấy hoặc ngày không hợp lệ (ví dụ: 30/02), nó sẽ trả về ngày hôm nay.
    
    Returns:
        Một đối tượng datetime.date.
    """
    match = re.search(r'(\d{2}/\d{2})', text_string)

    # 2. Kiểm tra xem có tìm thấy mẫu không
    if match:
        # Lấy chuỗi đã khớp (ví dụ: "30/06")
        date_str_dd_mm = match.group(1)
        # %d: ngày, %m: tháng, %Y: năm
        extracted_date = date_str_dd_mm
        return extracted_date
    else:
        # 4. Nếu không tìm thấy mẫu, trả về ngày hôm nay
        return datetime.now().date().strftime('%d/%m')

# --- Chương trình chính ---
start_time = time.time()
path = '/Users/nguyentrunganhonichan/Documents/Reinforcement_learning/sentiment_ana/nhan_dinh_market/vietstock_nhandinhthitruong.csv'
output_path = 'vietstock_nhandinhthitruong_sentiment.csv'
df_raw = pd.read_csv(path)
df_processed = pre_process(df_raw.copy())

if not df_processed.empty:
    print("\nBắt đầu thực hiện phân tích sentiment...")


    sentiment_results = pd.DataFrame(
        df_processed['Title'].apply(analyze_sentiment).tolist(),
        columns=['Sentiment', 'Scores'],
        index=df_processed.index # Quan trọng: giữ lại index gốc
    )

    # Ghép DataFrame kết quả sentiment vào DataFrame đã xử lý
    df_final = pd.concat([df_processed, sentiment_results], axis=1)

    print("Phân tích sentiment hoàn tất.")

    # In và lưu kết quả
    print("\nDataFrame kết quả (5 dòng đầu):")
    print(df_final.head())
    print(f"\nShape của DataFrame kết quả: {df_final.shape}")
else:
    print("\nDataFrame rỗng sau khi tiền xử lý.")


print("\nBắt đầu tách cột 'Scores'...")


score_lists = df_final['Scores'].str[0].tolist()

score_columns = ['Negative_Score', 'Positive_Score', 'Neutral_Score']
scores_df = pd.DataFrame(score_lists, columns=score_columns, index=df_final.index)


df_final = pd.concat([df_final, scores_df], axis=1)


df_final = df_final.drop(columns=['Scores'])

print("Tách cột hoàn tất.")

# Trích ngày tháng trong cột Datetime
df_final['Date'] = df_final['Datetime'].apply(extract_date_or_today)
df_final.drop(columns=['Datetime'], inplace=True)
df_final = df_final[['Date', 'news_type', 'Title', 'Brief', 'Sentiment',\
                    'Negative_Score', 'Positive_Score', 'Neutral_Score']]

# In kết quả cuối cùng
print("\nDataFrame cuối cùng sau khi đã tách Scores (5 dòng đầu):")
print(df_final.head())

# Lưu file kết quả cuối cùng
df_final.to_csv(output_path, index=False)
print(f"\nĐã lưu kết quả cuối cùng vào file: {output_path}")

end_time = time.time()
print(f"\nTổng thời gian thực thi: {end_time - start_time:.2f} giây")