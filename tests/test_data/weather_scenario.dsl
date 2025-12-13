response start.当前天气->processing: "正在查询上海的当前天气..."
response processing.api_response->completed: "【上海当前天气】 天气状况：晴 温度：22.5°C 湿度：65%"

# forecast flow
response start.天气预报->processing: "正在查询北京未来3天的天气预报..."
response processing.api_response->analyzing: "【北京未来3天天气预报】 2024-01-16 白天：多云，20°C 降水概率：30%"
response analyzing.api_response->completed: "天气趋势分析：未来几天有小雨，气温逐渐下降 注意事项：记得带伞"