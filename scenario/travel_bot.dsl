response start.default->routing: "您好，欢迎使用旅行客服。请问您需要查询哪一项？"
response start.greeting->routing: "您好，欢迎使用旅行客服。"
response routing.ask_order->order: "请问您要查询哪个订单？请输入订单号。"
response order.provide_order: "已为您查询到订单：{user_input}，谢谢。"
