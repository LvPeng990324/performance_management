from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


# 权限表
class Permission(models.Model):
    class Meta:
        permissions = (
            ('view_monthly_sales_data', '查看月度营业数据'),
            ('manage_monthly_sales_data', '管理月度营业数据'),
            ('view_quarterly_sales_data', '查看季度营业数据'),
            ('view_internal_control_indicators', '查看内控指标汇总'),
            ('manage_internal_control_indicators', '管理内控指标汇总'),
            ('view_monthly_performance', '查看月度绩效考核结果'),
            ('view_quarterly_performance', '查看季度绩效考核结果'),
            ('manage_constant_data', '管理常量数据'),
            ('manage_formula', '管理报表公式'),
            ('manage_user', '管理用户'),
            ('manage_permission', '管理授权'),
        )


# 用户扩展表
class UserExtension(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='extension')
    job_number = models.CharField(max_length=100, verbose_name='工号')
    telephone = models.CharField(max_length=100, verbose_name='电话号码')
    department = models.CharField(max_length=100, verbose_name='部门')


# 接收到save信号，将扩展表与原表绑定
@receiver(post_save, sender=User)
def handler_user_extension(sender, instance, created, **kwargs):
    if created:
        UserExtension.objects.create(user=instance)
    else:
        instance.extension.save()


# 月度营业数据
class MonthlySalesData(models.Model):
    year = models.IntegerField(verbose_name='年份')
    month = models.IntegerField(verbose_name='月份')
    turnover = models.FloatField(verbose_name='营业额')
    operating_expenses = models.FloatField(verbose_name='营业费用')
    amount_repaid = models.FloatField(verbose_name='回款额')
    inventory = models.IntegerField(verbose_name='库存量')
    profit = models.FloatField(verbose_name='利润额')

    class Meta:
        verbose_name_plural = '月度营业数据'
        verbose_name = '月度营业数据'

    def __str__(self):
        return str(self.id)


# 季度营业数据
class QuarterlySalesData(models.Model):
    year = models.IntegerField(verbose_name='年份')
    quarter = models.IntegerField(verbose_name='季度')
    turnover = models.FloatField(verbose_name='营业额')
    operating_expenses = models.FloatField(verbose_name='营业费用')
    amount_repaid = models.FloatField(verbose_name='回款额')
    inventory = models.IntegerField(verbose_name='库存量')
    profit = models.FloatField(verbose_name='利润额')

    class Meta:
        verbose_name_plural = '季度营业数据'
        verbose_name = '季度营业数据'

    def __str__(self):
        return str(self.id)


# 内控指标汇总
class InternalControlIndicators(models.Model):
    order_date = models.DateField(verbose_name='订单时间')
    order_number = models.CharField(max_length=100, verbose_name='订单号')
    order_money = models.FloatField(verbose_name='订单额')
    scheduled_delivery = models.DateField(verbose_name='计划交期')
    target_well_done_rate = models.FloatField(verbose_name='目标成品率')
    target_medical_expenses = models.FloatField(verbose_name='目标医药费')
    target_comprehensive_cost = models.FloatField(verbose_name='目标综合成本')
    target_management_compliance = models.IntegerField(verbose_name='目标管理符合数')
    # 以下为二次录入数据项
    actual_delivery = models.DateField(verbose_name='实际交期', null=True)
    finished_number = models.IntegerField(verbose_name='完成数', null=True)
    unfinished_number = models.IntegerField(verbose_name='未完成数', null=True)
    actual_well_done_rate = models.FloatField(verbose_name='实际成品率', null=True)
    actual_medical_expenses = models.FloatField(verbose_name='实际医药费', null=True)
    actual_cost = models.FloatField(verbose_name='实际成本', null=True)
    actual_management_compliance = models.IntegerField(verbose_name='实际管理符合数', null=True)

    class Meta:
        verbose_name_plural = '内控指标汇总'
        verbose_name = '内控指标汇总'

    def __str__(self):
        return str(self.order_number)


# 月度绩效考核结果
class MonthlyPerformance(models.Model):
    year = models.IntegerField(verbose_name='年份')
    month = models.IntegerField(verbose_name='月份')
    delivery_rate = models.FloatField(verbose_name='交付率')
    well_done_rate = models.FloatField(verbose_name='成品率')
    medical_expenses = models.FloatField(verbose_name='医药费')
    month_dig_cost = models.FloatField(verbose_name='当月挖掘成本')
    field_management_well_rate = models.FloatField(verbose_name='现场管理符合率')

    class Meta:
        verbose_name_plural = '月度绩效考核结果'
        verbose_name = '月度绩效考核结果'

    def __str__(self):
        return str(self.id)


# 季度绩效考核结果
class QuarterlyPerformance(models.Model):
    year = models.IntegerField(verbose_name='年份')
    quarter = models.IntegerField(verbose_name='季度')
    turnover = models.FloatField(verbose_name='营业额')
    operating_rate = models.FloatField(verbose_name='营业费率', null=True)
    repaid_rate = models.FloatField(verbose_name='回款率')
    inventory_rate = models.FloatField(verbose_name='库存率', null=True)
    profit_rate = models.FloatField(verbose_name='利润率', null=True)

    class Meta:
        verbose_name_plural = '季度绩效考核结果'
        verbose_name = '季度绩效考核结果'

    def __str__(self):
        return str(self.id)


# 季度绩效奖金额
class QuarterlyAward(models.Model):
    year = models.IntegerField(verbose_name='年份')
    quarter = models.IntegerField(verbose_name='季度')
    turnover_award = models.FloatField(verbose_name='营业额所得奖金额')
    operating_rate_award = models.FloatField(verbose_name='营业费率所得奖金额')
    repaid_rate_award = models.FloatField(verbose_name='回款率所得奖金额')
    inventory_rate_award = models.FloatField(verbose_name='库存率所得奖金额')
    profit_rate_award = models.FloatField(verbose_name='利润率所得奖金额')
    total = models.FloatField(verbose_name='合计')

    class Meta:
        verbose_name_plural = '季度绩效奖金额'
        verbose_name = '季度绩效奖金额'

    def __str__(self):
        return str(self.id)


# 常量数据
class ConstantData(models.Model):
    date = models.DateField(verbose_name='日期', auto_now_add=True)
    target_medical_expenses_rate = models.FloatField(verbose_name='目标医药费百分比')
    target_comprehensive_cost_rate = models.FloatField(verbose_name='目标综合成本百分比')
    target_management_compliance_value = models.IntegerField(verbose_name='目标管理符合数值')
    annual_target_turnover = models.FloatField(verbose_name='年度目标营业额')
    annual_target_award = models.FloatField(verbose_name='年度目标奖金额')

    class Meta:
        verbose_name_plural = '常量数据'
        verbose_name = '常量数据'

    def __str__(self):
        return str(self.id)


# 月度绩效考核公式表
class MonthlyFormula(models.Model):
    target_item = models.CharField(max_length=100, verbose_name='指标')
    formula = models.CharField(max_length=100, verbose_name='公式')

    class Meta:
        verbose_name_plural = '月度绩效考核公式表'
        verbose_name = '月度绩效考核公式表'

    def __str__(self):
        return str(self.id)


# 季度绩效考核公式表
class QuarterlyFormula(models.Model):
    target_item = models.CharField(max_length=100, verbose_name='指标')
    formula = models.CharField(max_length=100, verbose_name='公式')

    class Meta:
        verbose_name_plural = '季度绩效考核公式表'
        verbose_name = '季度绩效考核公式表'

    def __str__(self):
        return str(self.id)


# 季度奖金公式表
class QuarterlyAwardFormula(models.Model):
    target_item = models.CharField(max_length=100, verbose_name='指标')
    formula = models.CharField(max_length=100, verbose_name='公式')

    class Meta:
        verbose_name_plural = '季度奖金公式表'
        verbose_name = '季度奖金公式表'

    def __str__(self):
        return str(self.id)


# 日志表
class Logs(models.Model):
    log_time = models.DateTimeField(auto_now_add=True, verbose_name='日志时间')
    user_name = models.CharField(max_length=100, verbose_name='用户姓名')
    job_number = models.CharField(max_length=100, verbose_name='工号')
    action = models.CharField(max_length=254, verbose_name='动作描述')
    result = models.CharField(max_length=20, verbose_name='操作结果')

    class Meta:
        verbose_name_plural = '日志表'
        verbose_name = '日志表'

    def __str__(self):
        return '{} {}'.format(str(self.user_name), str(self.action))


# 公告表
class Announcement(models.Model):
    time = models.DateTimeField(verbose_name='时间')
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    who = models.CharField(max_length=100, verbose_name='发布者')

    class Meta:
        verbose_name_plural = '公告表'
        verbose_name = '公告表'

    def __str__(self):
        return self.title


# 系统配置表
class SystemConfig(models.Model):
    login_ways = models.CharField(max_length=200, verbose_name='系统登录方式')

    class Meta:
        verbose_name_plural = '系统配置表'
        verbose_name = '系统配置表'
