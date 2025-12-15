response start.查询余额->processing_balance: "正在为您查询账户余额..."
response processing_balance.api_response->completed_balance: "您的账户余额为：10000 CNY"

# 转账流程
response start.转账->confirming: "请确认转账信息："
response confirming.确认转账->processing_transfer: "安全验证通过，正在处理转账..."
response processing_transfer.api_response->completed_transfer: "转账成功！交易号：TXN20240115001，手续费：5.0元"

# 高风险转账（直接警告并结束）
response start.转账高风险->warning: "转账风险较高，建议您前往柜台办理或联系客服确认。"

# 账单查询
response start.查询账单->processing_bill: "正在查询本月的交易记录..."
response processing_bill.api_response->completed_bill: "共找到8笔交易，总收入：15000元，总支出：637.3元"