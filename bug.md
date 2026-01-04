# bug 1

當輸入不同的股票代號的時候，股票名稱不會更新，程式碼應該參考`https://ai.finlab.tw/database`這邊的文件來拿個股的名稱，收盤價成交量等檔案。`公司簡稱	data.get('company_basic_info')	str`

# bug 2 
收盤價不會自動更新，也就是說個股的收盤價還有開盤價成交量等資料，應該根據finlab資料更新，並且將資料存儲在 `data` 資料夾中。

# bug 3
redis尚未完成，可以參考 `real_time_page.py` 的程式碼邏輯優化程式碼。

完成之後把任務給到四個 agent再讓他們繼續完成。 修改 `docs\agent_1_core.md` `docs\agent_2_data.md` `docs\agent_3_ui.md` `docs\agent_4_charts.md`。