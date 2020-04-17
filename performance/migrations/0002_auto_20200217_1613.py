# Generated by Django 2.2 on 2020-02-17 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': (('view_monthly_sales_data', '查看月度营业数据'), ('manage_monthly_sales_data', '管理月度营业数据'), ('view_quarterly_sales_data', '查看季度营业数据'), ('manage_quarterly_sales_data', '管理季度营业数据'), ('view_internal_control_indicators', '查看内控指标汇总'), ('manage_internal_control_indicators', '管理内控指标汇总'), ('view_monthly_performance', '查看月度绩效考核结果'), ('view_quarterly_performance', '查看季度绩效考核结果'), ('manage_constant_data', '管理常量数据'), ('manage_formula', '管理报表公式'), ('manage_user', '管理用户'), ('manage_permission', '管理授权')),
            },
        ),
        migrations.AlterModelOptions(
            name='constantdata',
            options={'verbose_name': '常量数据', 'verbose_name_plural': '常量数据'},
        ),
        migrations.AlterModelOptions(
            name='internalcontrolindicators',
            options={'verbose_name': '内控指标汇总', 'verbose_name_plural': '内控指标汇总'},
        ),
        migrations.AlterModelOptions(
            name='monthlyformula',
            options={'verbose_name': '月度绩效考核公式表', 'verbose_name_plural': '月度绩效考核公式表'},
        ),
        migrations.AlterModelOptions(
            name='monthlyperformance',
            options={'verbose_name': '月度绩效考核结果', 'verbose_name_plural': '月度绩效考核结果'},
        ),
        migrations.AlterModelOptions(
            name='monthlysalesdata',
            options={'verbose_name': '月度营业数据', 'verbose_name_plural': '月度营业数据'},
        ),
        migrations.AlterModelOptions(
            name='quarterlyperformance',
            options={'verbose_name': '季度绩效考核结果', 'verbose_name_plural': '季度绩效考核结果'},
        ),
        migrations.AlterModelOptions(
            name='quarterlysalesdata',
            options={'verbose_name': '季度营业数据', 'verbose_name_plural': '季度营业数据'},
        ),
    ]