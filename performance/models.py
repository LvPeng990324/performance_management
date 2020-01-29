from django.db import models


# 月度营业数据
class MonthlySalesData(models.Model):
    date = models.DateTimeField(verbose_name='日期')
    turnover = models.FloatField(verbose_name='营业额')
    operating_expenses = models.FloatField(verbose_name='营业费用')
    amount_repaid = models.FloatField(verbose_name='回款额')
    inventory = models.FloatField(verbose_name='库存量')
    profit = models.FloatField(verbose_name='利润额')

    class Meta:
        verbose_name_plural = '月度营业数据'
        verbose_name = '月度营业数据'

    def __str__(self):
        return str(self.id)


# 季度营业数据
class QuarterlySalesData(models.Model):
    quarterly = models.IntegerField(verbose_name='季度')
    turnover = models.FloatField(verbose_name='营业额')
    operating_expenses = models.FloatField(verbose_name='营业费用')
    amount_repaid = models.FloatField(verbose_name='回款额')
    inventory = models.FloatField(verbose_name='库存量')
    profit = models.FloatField(verbose_name='利润额')

    class Meta:
        verbose_name_plural = '季度营业数据'
        verbose_name = '季度营业数据'

    def __str__(self):
        return str(self.id)


# 内控指标汇总
class InternalControlIndicators(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='序号')
    date = models.DateTimeField(verbose_name='时间')
    order_number = models.CharField(max_length=100, verbose_name='订单号')
    scheduled_delivery = models.DateTimeField(verbose_name='计划交期')
    actual_delivery = models.DateTimeField(verbose_name='实际交期')
    finished_number = models.IntegerField(verbose_name='完成数')
    unfinished_number = models.IntegerField(verbose_name='未完成数')
    target_well_done_rate = models.FloatField(verbose_name='目标成品率')
    actual_well_done_rate = models.FloatField(verbose_name='实际成品率')
    month_medical_expenses = models.FloatField(verbose_name='当月医药费')
    cost_per_wan = models.FloatField(verbose_name='万元成本')
    field_management_compliance = models.IntegerField(verbose_name='现场管理符合数')

    class Meta:
        verbose_name_plural = '内控指标汇总'
        verbose_name = '内控指标汇总'

    def __str__(self):
        return str(self.order_number)


# 月度绩效考核结果
class MonthlyPerformance(models.Model):
    date = models.DateTimeField(verbose_name='时间')
    delivery_rate = models.FloatField(verbose_name='交付率')
    well_done_rate = models.FloatField(verbose_name='成品率')
    medical_expenses = models.FloatField(verbose_name='医药费')
    overall_cost = models.FloatField(verbose_name='内控综合成本')
    field_management = models.FloatField(verbose_name='现场管理')

    class Meta:
        verbose_name_plural = '月度绩效考核结果'
        verbose_name = '月度绩效考核结果'

    def __str__(self):
        return str(self.id)


# 季度绩效考核结果
class QuarterlyPerformance(models.Model):
    date = models.DateTimeField(verbose_name='时间')
    turnover = models.FloatField(verbose_name='营业额')
    operating_rate = models.FloatField(verbose_name='营业费率')
    repaid_rate = models.FloatField(verbose_name='回款率')
    inventory_rate = models.FloatField(verbose_name='库存率')
    profit_rate = models.FloatField(verbose_name='利润率')

    class Meta:
        verbose_name_plural = '季度绩效考核结果'
        verbose_name = '季度绩效考核结果'

    def __str__(self):
        return str(self.id)


# 常量数据
class ConstantData(models.Model):
    month_plan_order_number = models.IntegerField(verbose_name='当月约定订单数')
    target_cost = models.FloatField(verbose_name='目标成本')
    field_management_compliance_target_number = models.IntegerField(verbose_name='现场管理标准目标数')
    annual_target_turnover = models.FloatField(verbose_name='年度目标营业额')
    annual_target_award = models.FloatField(verbose_name='年度目标奖金额')

    class Meta:
        verbose_name_plural = '常量数据'
        verbose_name = '常量数据'

    def __str__(self):
        return str(self.id)
