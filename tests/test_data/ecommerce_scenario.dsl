response start.查询订单->processing_order: "正在查询订单信息..."
response processing_order.api_response->completed_order: "找到2个订单。订单号：ORD20240115001，商品：智能手机，2999.0元"

response start.物流查询->processing_logistics: "正在查询物流信息..."
response processing_logistics.api_response->completed_logistics: "物流公司：顺丰速运，当前状态：已签收，2024-01-12 北京分拨中心"

response start.退货->processing_return: "正在为您处理退货申请..."
response processing_return.api_response->confirming_return: "您的订单符合退货条件，退货期限：收到商品7天内，运费由卖家承担"
response confirming_return.api_response->completed_return: "退货申请已提交！退货单号：RTN20240115001，退货地址：上海市浦东新区"

response start.商品咨询->processing_product: "正在查询商品信息..."
response processing_product.api_response->completed_product: "商品信息：名称：iPhone 15 Pro，价格：8999.0元，屏幕尺寸：6.7英寸，新年优惠：立减500元"