response greeting: "欢迎来到电商客服。您可以查询订单、物流、退货退款或商品信息。"
response order_help: "查询订单请提供订单号或注册手机号，我们将帮您查找订单信息。"
response logistics_help: "物流查询请提供运单号或订单号以便跟踪配送状态。"
response refund_help: "退货退款请先确认订单是否符合退货条件，我们会为您指引下一步操作。"
response product_help: "商品咨询请提供商品名称或ID，支持查询价格与库存信息。"
response promo_help: "当前优惠请关注活动页面或联系客服了解更多。"

############################################
# 会员服务
############################################

WHEN "会员等级" OR "积分查询" OR "VIP"
THEN
    CALL get_member_info()
    
    IF api_response.success THEN
        SAY "会员信息："
        SAY "等级：{api_response.level}"
        SAY "积分：{api_response.points}"
        SAY "成长值：{api_response.growth_value}"
        SAY "有效期：{api_response.expiry_date}"
        
        # 显示会员权益
        CALL get_member_benefits(api_response.level)
        
        IF api_response.benefits THEN
            SAY "会员权益："
            WHILE benefit IN api_response.benefits DO
                SAY "✓ {benefit}"
            ENDWHILE
        ENDIF
        
        # 显示积分可兑换商品
        IF api_response.points > 1000 THEN
            SAY "您的积分可以兑换："
            CALL get_points_products(api_response.points)
            WHILE product IN api_response.products DO
                SAY "- {product.name}: {product.points_required}积分"
            ENDWHILE
        ENDIF
    ENDIF
END