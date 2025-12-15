response start.当前天气->processing_current: "正在查询上海的当前天气..."
response processing_current.api_response->completed_current: "【上海当前天气】 天气状况：晴 温度：22.5°C 湿度：65%"

response start.天气预报->processing_forecast: "正在查询北京未来3天的天气预报..."
response processing_forecast.api_response->analyzing_forecast: "【北京未来3天天气预报】 2024-01-16 白天：多云，20°C 降水概率：30%"
response analyzing_forecast.api_response->completed_forecast: "天气趋势分析：未来几天有小雨，气温逐渐下降 注意事项：记得带伞"

response start.空气质量->processing_aqi: "正在查询广州的空气质量..."
response processing_aqi.api_response->evaluating_aqi: "【广州空气质量】 AQI指数：85 主要污染物：PM2.5 PM2.5：65 μg/m³"
response evaluating_aqi.api_response->completed_aqi: "健康建议：空气质量可接受，空气质量正在好转。"

# 多城市对比流程
response start.天气对比->processing_compare: "正在对比北京、上海、广州的天气情况..."
response processing_compare.api_response->analyzing_compare: "【多城市天气对比】 生成中，正在汇总城市天气数据。"
response analyzing_compare.api_response->completed_compare: "分析结果： 最适合出行的城市：上海，原因：温度适宜，空气质量良好。不推荐城市：北京：空气质量较差; 广州：湿度过高，有雨"