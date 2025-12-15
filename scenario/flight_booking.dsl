response start.default->booking: "欢迎，输入出发地/目的地/日期，我们将为您订票。"
response booking.provide_info->confirm: "已收到信息：{user_input}，正在生成确认信息..."
response confirm.default: llm_generate("Create a short booking confirmation using: " + user_input)
