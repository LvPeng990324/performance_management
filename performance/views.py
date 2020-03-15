from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.db.models import F
from django.db.models import Q
from django.db.models import Sum
from django.http import JsonResponse, FileResponse
from django.contrib import messages
from datetime import datetime
from datetime import date
from django.utils.encoding import escape_uri_path
from .models import MonthlySalesData
from .models import QuarterlySalesData
from .models import InternalControlIndicators
from .models import ConstantData
from .models import MonthlyPerformance
from .models import QuarterlyPerformance
from .models import MonthlyFormula
from .models import QuarterlyFormula
from .models import QuarterlyAwardFormula
from .models import QuarterlyAward
from .models import User
from .models import Logs
from .models import Announcement
from .models import SystemConfig
from .models import OpenApi
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from .forms import cleaned_formula, check_data_format
from .utils import UploadTable
from .utils import ExportTable
from .utils import CalcuteMonthlyPerformance
from .utils import CalculateQuarterlyPerformance
from .utils import CalculateQuarterlySalesData
from .utils import CalculateQuarterlyAward
from .utils import DatabaseBackup
from .utils import GetVerificationCode
from .utils.Paginator import PageInfo
from .utils.UserLog import add_log
from django.conf import settings


# 测试页面方法
def test_page(request):
    return render(request, '开放接口.html')

# 展示首页
@login_required
def index(request):
    # 统计首页展示数据
    # 统计本月订单数
    today = date.today()
    month_order_count = InternalControlIndicators.objects.filter(order_date__year=today.year,
                                                                 order_date__month=today.month).count()
    # 获取当前用户角色
    user_group = []
    if request.user.is_superuser:
        user_group.append('超级管理员')
    else:
        for group in request.user.groups.all():
            user_group.append(group.name)
    # 获取本月待完成订单信息
    month_to_finish_order = InternalControlIndicators.objects.filter(scheduled_delivery__year=today.year,
                                                                     scheduled_delivery__month=today.month,
                                                                     finished_number=None)
    # 获取前N条公告信息，根据时间逆序排序
    announcements = Announcement.objects.all().order_by('-time')[:2]

    # 打包数据
    context = {
        'month_order_count': month_order_count,
        'user_group': user_group,
        'month_to_finish_order': month_to_finish_order,
        'announcements': announcements,
    }

    return render(request, '首页.html', context=context)


# 公告页面方法
def notice(request):
    # 分页获取公告信息，根据时间逆序排序
    counts = Announcement.objects.all().order_by('-time').count()
    page_info = PageInfo(request.GET.get('page'), counts, 20, '/notice?')
    announcements = Announcement.objects.all().order_by('-time')[page_info.start():page_info.end()]
    # 打包数据
    context = {
        'announcements': announcements,
        'page_info': page_info,
    }
    return render(request, '首页-公告页面.html', context=context)


# 登陆方法
def user_login(request):
    if request.method == 'GET':
        # 打包已开启的登录方式
        ways = SystemConfig.objects.first()
        # 如果没取到，创建三个
        if not ways:
            SystemConfig.objects.create(
                login_ways='工号登录 短信验证 微信扫码'
            )
            # 重载登录界面
            return redirect('user_login')
        else:
            ways = ways.login_ways
        login_ways = []
        for way in ways.split(' '):
            login_ways.append(way)
        # 打包信息
        context = {
            'login_ways': login_ways,
        }
        return render(request, '登录.html', context=context)
    else:
        # 从前端获取用户名密码
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()

        # 验证登录信息
        user = authenticate(username=username, password=password)
        if user:
            # 登录成功，记录登录信息，重定向首页
            login(request, user)
            return redirect('index')
        else:
            # 登录失败，写入用户名密码错误信息并重载页面
            messages.error(request, '用户名或密码错误')
            return redirect('user_login')


# 手机验证码登录方法
# 注意！！此方法尚未完善，需要接入第三方短信提供商
# 现在此方法仅仅处于测试阶段，勿用于生产环境！
def phone_login(request):
    # 从前端获取手机号
    phone = request.POST.get('phone')
    # 取出此手机号的用户
    user = User.objects.get(extension__telephone=phone)
    if user:
        # 登录成功，记录登录信息，重定向首页
        login(request, user)
        return redirect('index')
    else:
        # 登录失败，写入用户名密码错误信息并重载页面
        messages.error(request, '手机号无记录')
        return redirect('user_login')


# 邮箱验证码登录方法
def email_login(request):
    # GET为请求验证码，POST为验证码登录
    if request.method == 'GET':
        # 获取当前填的email
        email = request.GET.get('email')
        # 随机生成六位验证码
        verification_code = GetVerificationCode.get_verification_code()
        # 记录邮箱和验证码到session
        
    else:
        pass


# 登出方法
@login_required
def user_logout(request):
    # 登出用户
    logout(request)
    # 重定向登录页面
    return redirect('user_login')


# 展示账号管理页面方法
@login_required
@permission_required('performance.manage_user', raise_exception=True)
def user_management(request):
    # GET：无筛选访问
    # POST：带部门筛选的访问
    if request.method == 'GET':
        # 获取所有用户信息
        users = User.objects.all()
        department = ''
    else:
        # 获取要筛选的部门名
        department = request.POST.get('department')
        # 筛选名称包含该字段的部门下所有员工
        users = User.objects.filter(extension__department__contains=department)
    # 打包已选登录方法
    ways = SystemConfig.objects.first()
    # 如果没取到就设为空字符串
    if not ways:
        ways = ''
    else:
        ways = ways.login_ways
    # 将登录方法打包进列表
    login_ways = []
    for way in ways.split(' '):
        login_ways.append(way)
    # 打包信息
    context = {
        'users': users,
        'department': department,
        'login_ways': login_ways,
    }
    # 引导前端页面
    return render(request, '账号权限管理-账号管理.html', context=context)


# 新增账号方法
@login_required
@permission_required('performance.manage_user', raise_exception=True)
def add_user(request):
    # 从前端获取填写用户信息
    job_number = str(request.POST.get('job_number')).strip()
    name = str(request.POST.get('name')).strip()
    department = str(request.POST.get('department')).strip()
    telephone = str(request.POST.get('telephone')).strip()
    email = str(request.POST.get('email')).strip()
    password = str(request.POST.get('password')).strip()

    # 保存用户
    try:
        user = User.objects.create_user(
            username=job_number,
            password=password,
            last_name=name,
            email=email,
        )
        user.extension.job_number = job_number
        user.extension.department = department
        user.extension.telephone = telephone
        user.save()
        # 写入成功提示
        messages.success(request, '用户增加成功')
        # 记录日志
        action = '增加了工号为{}，姓名为{}的账号'.format(job_number, name)
        add_log(request, action, '成功')
    except:
        # 写入失败提示
        messages.error(request, '用户增加失败')
        # 记录日志
        action = '试图增加工号为{}，姓名为{}的账号'.format(job_number, name)
        add_log(request, action, '失败')
    # 重载账号展示页面
    return redirect('user_management')


# 删除账号方法
@login_required
@permission_required('performance.manage_user', raise_exception=True)
def delete_user(request):
    # 防止把自己删除
    # 先获取当前登录用户id
    current_user_id = str(User.objects.get(id=request.user.id).id)
    # GET为多条删除，POST为单条删除
    if request.method == 'GET':
        delete_id = request.GET.getlist('delete_id', [])
        # 判断当前用户是否在列表中
        # 在的话就直接提示不能删自己
        if current_user_id in delete_id:
            messages.error(request, '不可以删除当前登录的账号')
            return HttpResponse('success')
        # 遍历删除
        for id in delete_id:
            User.objects.get(id=id).delete()
        # 写入删除成功提示
        messages.success(request, '选中用户删除成功')
        # 记录日志
        action = '多选删除了{}个账号'.format(len(delete_id))
        add_log(request, action, '成功')
        # 返回成功
        return HttpResponse('success')
    else:
        # 取得要删除的id
        delete_id = request.POST.get('delete_id')
        # 判断要删除的是不是当前用户
        # 是的话直接提示不能删自己
        if current_user_id == delete_id:
            messages.error(request, '不能删除当前登录账号')
            return redirect('user_management')
        # 从数据库中取出
        user = User.objects.get(id=delete_id)
        # 记录日志用信息
        job_number = user.extension.job_number
        name = user.last_name
        # 删除
        user.delete()
        # 写入删除成功提示
        messages.success(request, '用户删除成功')
        # 记录日志
        action = '删除了工号为{}，姓名为{}的账号'.format(job_number, name)
        add_log(request, action, '成功')
    # 重载账号展示页面
    return redirect('user_management')


# 修改账户方法
@login_required
@permission_required('performance.manage_user', raise_exception=True)
def change_user(request):
    # 从前端获取要修改的id
    change_id = request.POST.get('change_id')
    # 获取修改后的信息
    job_number = request.POST.get('job_number')
    name = request.POST.get('name')
    department = request.POST.get('department')
    telephone = request.POST.get('telephone')
    email = request.POST.get('email')
    # 取出此账户并更新信息
    user = User.objects.get(id=change_id)
    user.extension.job_number = job_number
    user.username = job_number
    user.last_name = name
    user.extension.department = department
    user.extension.telephone = telephone
    user.email = email
    user.save()
    # 写入成功提示
    messages.success(request, '用户信息修改成功')
    # 记录日志
    action = '修改了工号为{}，姓名为{}的账号信息'.format(job_number, name)
    add_log(request, action, '成功')
    # 重载账号展示页面
    return redirect('user_management')


# 管理员修改账户密码方法
@login_required
@permission_required('performance.manage_user', raise_exception=True)
def admin_change_password(request):
    # 获取要更改密码的id
    change_id = request.POST.get('passwd_id')
    user = User.objects.get(id=change_id)
    # 获取新密码
    password = request.POST.get('password').strip()
    # 设置新密码
    user.set_password(password)
    user.save()
    # 写入成功提示
    messages.success(request, '密码修改成功')
    # 记录日志
    action = '修改了工号为{}，姓名为{}的账号密码'.format(user.extension.job_number, user.last_name)
    add_log(request, action, '成功')
    # 重载页面
    return redirect('user_management')


# 用户修改自己密码方法
@login_required
def user_change_password(request):
    if request.method == 'GET':
        return render(request, '账号-修改密码.html')
    else:
        # 获取用户输入的密码
        old_password = request.POST.get('old_password').strip()
        new_password = request.POST.get('new_password').strip()
        new_password_again = request.POST.get('new_password_again').strip()
        # 取出当前用户
        user = request.user
        # 验证当前用户密码是否匹配用户输入的旧密码
        if not user.check_password(old_password):
            # 验证失败，写入验证失败提示
            messages.error(request, '旧密码有误，如遗忘请联系管理员修改')
            # 重载更改密码页面
            return redirect('user_change_password')
    # 验证二次密码是否相同
    if new_password != new_password_again:
        # 写入两次确认密码不同错误
        messages.error(request, '两次确认密码不同，请重新输入')
        # 重载更改密码页面
        return redirect('user_change_password')
    try:
        # 更新用户密码
        user.set_password(new_password)
        user.save()
    except:
        messages.error(request, '未知错误，请重试或重新登录尝试')
        return redirect('user_change_password')
    # 写入成功提示
    messages.success(request, '密码修改成功，请重新登录')
    # 记录日志
    action = '修改了自己账户的密码'
    add_log(request, action, '成功')
    # 注销该用户
    logout(request)
    # 重载登录界面
    return redirect('user_login')


# 用户修改自己个人信息
@login_required
def user_change_information(request):
    if request.method == 'GET':
        # 取出当前用户
        user = request.user
        # 打包信息
        context = {
            'user': user,
        }
        # 引导前端
        return render(request, '账号-用户修改个人信息.html', context=context)
    else:
        # 目前只能改手机号和邮箱
        # 从前端获取输入的手机号和邮箱
        telephone = request.POST.get('telephone').strip()
        email = request.POST.get('email').strip()
        try:
            # 获取当前用户
            user = request.user
            # 更新信息
            user.extension.telephone = telephone
            user.email = email
            user.save()
        except:
            # 打包错误信息
            messages.error(request, '未知错误，请重试或重新登录尝试')
            # 重载信息修改页面
            return redirect('user_change_information')
        # 打包成功信息
        messages.success(request, '信息修改成功')
        # 记录日志
        action = '修改了个人账号信息'
        add_log(request, action, '成功')
        # 重载信息修改页面
        return redirect('user_change_information')


# 展示角色权限管理界面
@login_required
@permission_required('performance.manage_permission', raise_exception=True)
def group_management(request):
    # 从数据库中取出所有角色(组)
    groups = Group.objects.all()
    # 从数据库中取出所有账号
    users = User.objects.all()
    # 打包数据
    context = {
        'groups': groups,
        'users': users,
    }
    return render(request, '账号权限管理-权限管理.html', context=context)


# 增加角色方法
@login_required
@permission_required('performance.manage_permission', raise_exception=True)
def add_group(request):
    # 取得角色名称
    name = request.POST.get('name')
    # 取得权限列表
    permissions = request.POST.getlist('permissions', [])
    # 判断前三张表有没有只有管理没查看的权限
    # 如果存在这种情况，将相应的查看权限补充上
    # 月度营业数据
    if 'manage_monthly_sales_data' in permissions and 'view_monthly_sales_data' not in permissions:
        permissions.append('view_monthly_sales_data')
    # # 季度营业数据
    # if 'manage_quarterly_sales_data' in permissions and 'view_quarterly_sales_data' not in permissions:
    #     permissions.append('view_quarterly_sales_data')
    # 内控指标汇总
    if 'manage_internal_control_indicators' in permissions and 'view_internal_control_indicators' not in permissions:
        permissions.append('view_internal_control_indicators')
    # 从权限表中取出相应的权限
    permissions_list = Permission.objects.filter(codename__in=permissions)

    # 创建角色(组)
    group = Group.objects.get_or_create(name=name)[0]
    # 给新角色加权限
    group.permissions.add(*permissions_list)
    # 写入成功信息
    messages.success(request, '角色增加成功')
    # 记录日志
    action = '增加了{}角色'.format(name)
    add_log(request, action, '成功')
    # 重载角色权限管理界面
    return redirect('group_management')


# 删除角色方法
@login_required
@permission_required('performance.manage_permission', raise_exception=True)
def delete_group(request):
    # get为多选删除，post为单条删除
    if request.method == 'GET':
        delete_id = request.GET.getlist('delete_id', [])
        # 遍历删除
        for id in delete_id:
            Group.objects.get(id=id).delete()
        # 写入删除成功提示
        messages.success(request, '选中角色删除成功')
        # 记录日志
        action = '多选删除了{}个角色'.format(len(delete_id))
        add_log(request, action, '成功')
        # 返回成功
        return HttpResponse('success')
    else:
        delete_id = request.POST.get('delete_id')
        # 从数据库中删除
        group = Group.objects.get(id=delete_id)
        # 取出记录日志信息
        name = group.name
        # 删除
        group.delete()
        # 写入删除成功提示
        messages.success(request, '角色删除成功')
        # 记录日志
        action = '删除了{}角色'.format(name)
        add_log(request, action, '成功')
        # 重载页面
        return redirect('group_management')


# 修改角色方法
@login_required
@permission_required('performance.manage_permission', raise_exception=True)
def change_group(request):
    # 获取要修改的id
    change_id = request.POST.get('change_id')
    # 获取更改后的权限列表
    permissions = request.POST.getlist('permissions')
    # 取出相应的权限
    permissions_list = Permission.objects.filter(codename__in=permissions)
    # 获取要修改的角色(组)
    group = Group.objects.get(id=change_id)
    # 清空当前权限
    group.permissions.clear()
    # 给当前角色(组)重新赋予权限
    group.permissions.add(*permissions_list)
    # 写入成功信息
    messages.success(request, '角色权限修改成功')
    # 记录日志
    action = '修改了{}角色权限'.format(group.name)
    add_log(request, action, '成功')
    # 重载角色权限管理界面
    return redirect('group_management')


# 从角色(组)批量赋予给账号方法
@login_required
@permission_required('performance.manage_permission', raise_exception=True)
def group_to_user(request):
    # 如果是POST，则为筛选
    if request.method == 'POST':
        # 获取筛选条件
        search = request.POST.get('search')
        # 获取角色(组)的id
        group_id = request.POST.get('group_id')
        group = Group.objects.get(id=group_id)
        # 获取这个角色下的账号
        in_group_users = group.user_set.all()
        # 获取所有用户
        users = User.objects.all()
        # 筛选出未在此角色(组)的用户列表
        out_group_user = users
        for user in in_group_users:
            out_group_user = out_group_user.exclude(id=user.id)
        # 筛选未在此角色(组)的用户中符合筛选要求的用户列表
        out_group_user = out_group_user.filter(
            Q(extension__department__contains=search) |
            Q(extension__job_number__contains=search) |
            Q(last_name__contains=search)
        )
        # 打包数据
        context = {
            'group_id': group_id,
            'in_group_users': in_group_users,
            'out_group_users': out_group_user,
            'search': search,
        }
        # 引导前端页面
        return render(request, '账号权限管理-权限管理-赋予用户角色.html', context=context)
    # 判断有无ajax变量值，有的话就是提交数据，没有就是访问页面
    if not request.GET.get('ajax'):
        # 获取角色(组)的id
        group_id = request.GET.get('group_id')
        group = Group.objects.get(id=group_id)
        # 获取这个角色下的账号
        in_group_users = group.user_set.all()
        # 获取所有用户
        users = User.objects.all()
        # 筛选出未在此角色(组)的用户列表
        out_group_user = users
        for user in in_group_users:
            out_group_user = out_group_user.exclude(id=user.id)
        # 打包数据
        context = {
            'group_id': group_id,
            'in_group_users': in_group_users,
            'out_group_users': out_group_user,
        }
        # 引导前端页面
        return render(request, '账号权限管理-权限管理-赋予用户角色.html', context=context)
    else:
        # 获取组id并取出这个组
        group_id = request.GET.get('group_id')
        group = Group.objects.get(id=group_id)
        # 获取选择的账号id列表
        user_id_list = request.GET.getlist('selected', [])

        # 将这个组的用户清空
        in_group_users = group.user_set.all()
        for user in in_group_users:
            user.groups.remove(group)

        # 将这些用户加入到这个组中去
        # 选出这些用户
        users = User.objects.filter(id__in=user_id_list)
        # 将这些用户加入到这个组里
        for user in users:
            user.groups.add(group)
        # 写入成功提示
        messages.success(request, '赋予角色成功')
        # 记录日志
        action = '将{}角色赋予给{}个账号'.format(group.name, len(user_id_list))
        add_log(request, action, '成功')

        return HttpResponse('success')


# 展示月度营业数据方法
@login_required
@permission_required('performance.manage_monthly_sales_data', raise_exception=True)
def show_monthly_sales_data(request):
    # 打包年份数据，去重并逆序排序
    year_list = MonthlySalesData.objects.values('year').distinct().order_by('-year')
    # 如果没有年份数据，直接返回空数据
    if not year_list:
        # 打包空数据
        context = {
            'current_year': '无数据',
        }
        # 引导前端页面
        return render(request, '业务数据管理-月度营业数据.html', context=context)
    # 尝试取用户选择的年份
    current_year = request.GET.get('current_year')
    # 如果没取到或者取到了'所有年份'，说明是访问此页面或者选择展示所有数据，展示所有数据
    if current_year == '所有年份' or not current_year:
        # 从数据库中取出所有数据，并按照年份和月份顺序排序
        monthly_sales_data = MonthlySalesData.objects.all().order_by(F('year') * 100 + F('month'))
        # 记录current_year
        current_year = '所有年份'
    # 如果取到了具体年份数据，取出对应的数据并展示
    else:
        # 从数据库中取出对用年份的数据并按照月份顺序排序
        monthly_sales_data = MonthlySalesData.objects.filter(year=current_year).order_by('month')
        # 记录current_year
        current_year = int(current_year)
    # 打包数据
    context = {
        'monthly_sales_data': monthly_sales_data,
        'year_list': year_list,
        'current_year': current_year,
    }
    # 引导前端页面
    return render(request, '业务数据管理-月度营业数据.html', context=context)


# 增加月度营业数据方法
@login_required
@permission_required('performance.manage_monthly_sales_data', raise_exception=True)
def add_monthly_sales_data(request):
    # 从前端获取数据
    year_month = str(request.POST.get('date')).split('-')
    year = year_month[0]
    month = year_month[1]
    turnover = check_data_format(request.POST.get('turnover'), 'float')
    operating_expenses = check_data_format(request.POST.get('operating_expenses'), 'float')
    amount_repaid = check_data_format(request.POST.get('amount_repaid'), 'float')
    inventory = check_data_format(request.POST.get('inventory'), 'int')
    # 验证数据合法性
    for data in [turnover, operating_expenses, amount_repaid, inventory]:
        if data is False:
            messages.error(request, '输入存在格式问题，请检查输入')
            return redirect('show_monthly_sales_data')
    # 利润额根据 营业额 - 营业费用 得出
    profit = float(turnover) - float(operating_expenses)

    # 写入数据库
    MonthlySalesData.objects.create(
        year=year,
        month=month,
        turnover=turnover,
        operating_expenses=operating_expenses,
        amount_repaid=amount_repaid,
        inventory=inventory,
        profit=profit,
    )

    # 写入成功提示
    messages.success(request, '数据添加成功')
    # 记录日志
    action = '增加了{}年{}月的月度营业数据'.format(year, month)
    add_log(request, action, '成功')
    # 刷新当年季度营业数据
    CalculateQuarterlySalesData.calculate_quarterly_sales_data(year=[year])
    # 刷新当年季度考核结果
    CalculateQuarterlyPerformance.quarterly_get_and_refresh(year_list=[year])
    # 刷新所有季度奖金额
    CalculateQuarterlyAward.quarterly_get_and_refresh()

    # 重定向展示页面
    return redirect('show_monthly_sales_data')


# 删除月度营业数据方法
@login_required
@permission_required('performance.manage_monthly_sales_data', raise_exception=True)
def delete_monthly_sales_data(request):
    # 用来记录删除数据的年份
    year_set = set()
    # get为多选删除，post为单条删除
    if request.method == 'GET':
        delete_id = request.GET.getlist('delete_id', [])
        # 遍历删除，取出年份
        for id in delete_id:
            data = MonthlySalesData.objects.get(id=id)
            # 记录年份，方便更新季度数据
            year_set.add(data.year)
            # 删除数据
            data.delete()
        # 写入删除成功提示
        messages.success(request, '选中数据删除成功')

        # 记录日志
        action = '多选删除了{}条月度营业数据'.format(len(delete_id))
        add_log(request, action, '成功')

        # 刷新当年季度营业数据
        CalculateQuarterlySalesData.calculate_quarterly_sales_data(year=year_set)
        # 刷新当年季度考核结果
        CalculateQuarterlyPerformance.quarterly_get_and_refresh(year_list=year_set)
        # 刷新所有季度奖金额
        CalculateQuarterlyAward.quarterly_get_and_refresh()

        # 返回成功
        return HttpResponse('success')
    else:
        delete_id = request.POST.get('delete_id')
        # 从数据库中删除
        data = MonthlySalesData.objects.get(id=delete_id)
        # 取出数据年月
        year = data.year
        month = data.month
        year_set.add(year)
        data.delete()
        # 写入删除成功提示
        messages.success(request, '数据删除成功')

        # 记录日志
        action = '删除了{}年{}月的月度营业数据'.format(year, month)
        add_log(request, action, '成功')

        # 刷新当年季度营业数据
        CalculateQuarterlySalesData.calculate_quarterly_sales_data(year=year_set)
        # 刷新当年季度考核结果
        CalculateQuarterlyPerformance.quarterly_get_and_refresh(year_list=year_set)
        # 刷新所有季度奖金额
        CalculateQuarterlyAward.quarterly_get_and_refresh()

        # 重载页面
        return redirect('show_monthly_sales_data')


# 修改月度营业数据
@login_required
@permission_required('performance.manage_monthly_sales_data', raise_exception=True)
def change_monthly_sales_data(request):
    # 从前端获取要修改的id
    change_id = request.POST.get('change_id')
    # 从前端获取修改后的数据
    change_year_month = str(request.POST.get('change_date')).split('-')
    change_turnover = check_data_format(request.POST.get('change_turnover'), 'float')
    change_operating_expenses = check_data_format(request.POST.get('change_operating_expenses'), 'float')
    change_amount_repaid = check_data_format(request.POST.get('change_amount_repaid'), 'float')
    change_inventory = check_data_format(request.POST.get('change_inventory'), 'int')
    # 验证数据合法性
    for data in [change_turnover, change_operating_expenses, change_amount_repaid, change_inventory]:
        if data is False:
            messages.error(request, '输入存在格式问题，请检查输入')
            return redirect('show_monthly_sales_data')
    # 利润额根据 营业额 - 营业费用 得出
    change_profit = float(change_turnover) - float(change_operating_expenses)

    # 从数据库中取出该数据
    data = MonthlySalesData.objects.get(id=change_id)
    # 修改数据
    data.year = change_year_month[0]
    data.month = change_year_month[1]
    data.turnover = change_turnover
    data.operating_expenses = change_operating_expenses
    data.amount_repaid = change_amount_repaid
    data.inventory = change_inventory
    data.profit = change_profit
    # 保存更改
    data.save()

    # 写入数据修改成功
    messages.success(request, '数据修改成功')

    # 记录日志
    action = '修改了{}年{}月的月度营业数据'.format(change_year_month[0], change_year_month[1])
    add_log(request, action, '成功')

    # 刷新季度营业数据
    CalculateQuarterlySalesData.calculate_quarterly_sales_data(year=[change_year_month[0]])
    # 刷新季度考核结果
    CalculateQuarterlyPerformance.quarterly_get_and_refresh(year_list=[change_year_month[0]])
    # 刷新所有季度奖金额
    CalculateQuarterlyAward.quarterly_get_and_refresh()

    # 重定向展示页面
    return redirect('show_monthly_sales_data')


# 展示内控指标汇总表方法
@login_required
@permission_required('performance.manage_internal_control_indicators', raise_exception=True)
def show_internal_control_indicators(request):
    # GET为请求页面，展示所有数据
    # POST为带时间段筛选请求，取出时间段内数据展示
    if request.method == 'GET':
        # 尝试获取选择的状态
        # 如果没有或者是'所有状态'，就取出所有数据
        # 如果有状态，就筛选出相应状态的订单
        current_status = request.GET.get('current_status')
        if current_status == '按时完成':
            # 完成数为1
            data = InternalControlIndicators.objects.filter(finished_number=1)
            all_count = data.count()
            page_info = PageInfo(request.GET.get('page'), all_count, 15,
                                 '/show_internal_control_indicators/?current_status=按时完成&')
            internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
        elif current_status == '尚未完成':
            # 没有完成数
            # 当前时间没超过计划交期
            # 时间进度小于等于70%
            data = InternalControlIndicators.objects.filter(finished_number=None)
            # 获取当前时间
            current_time = date.today()
            # 遍历循环，不符合条件的排除掉
            for temp in data:
                # 计算时间进度百分比
                # 如果订单时间跟计划交期相同，则排除掉
                if temp.order_date == temp.scheduled_delivery:
                    data = data.exclude(id=temp.id)
                    continue
                percentage = (current_time - temp.order_date).days / (temp.scheduled_delivery - temp.order_date).days
                # 当前时间大于计划时间的排除
                # 时间进度百分比超过0.7的排除
                # 当前时间小于订单时间的排除
                if current_time > temp.scheduled_delivery or percentage > 0.7 or current_time < temp.order_date:
                    data = data.exclude(id=temp.id)
            # 写入数据
            all_count = data.count()
            page_info = PageInfo(request.GET.get('page'), all_count, 15,
                                 '/show_internal_control_indicators/?current_status=尚未完成&')
            internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
        elif current_status == '逾期完成':
            # 完成数为0
            data = InternalControlIndicators.objects.filter(finished_number=0)
            all_count = data.count()
            page_info = PageInfo(request.GET.get('page'), all_count, 15,
                                 '/show_internal_control_indicators/?current_status=逾期完成&')
            internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
        elif current_status == '快到交期':
            # 没有完成数
            # 当前时间没超过计划交期
            # 时间进度大于70%
            data = InternalControlIndicators.objects.filter(finished_number=None)
            # 获取当前时间
            current_time = date.today()
            # 遍历循环，不符合条件的排除掉
            for temp in data:
                # 计算时间进度百分比
                # 当订单时间与计划交期一样时，只有当前时间也一样才是快到交期
                if temp.scheduled_delivery == temp.order_date:
                    if current_time == temp.order_date:
                        percentage = 1
                    else:
                        data = data.exclude(id=temp.id)
                        continue
                else:
                    percentage = (current_time - temp.order_date).days / (
                            temp.scheduled_delivery - temp.order_date).days
                # 当前时间大于计划时间的排除
                # 时间进度百分比未超过0.7的排除
                if current_time > temp.scheduled_delivery or percentage <= 0.7:
                    data = data.exclude(id=temp.id)
            # 写入数据
            all_count = data.count()
            page_info = PageInfo(request.GET.get('page'), all_count, 15,
                                 '/show_internal_control_indicators/?current_status=快到交期&')
            internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
        elif current_status == '已经逾期':
            # 没有完成数
            # 当前时间在计划交期之后
            data = InternalControlIndicators.objects.filter(finished_number=None)
            # 获取当前时间
            current_time = date.today()
            # 遍历判断，不符合条件的排除掉
            for temp in data:
                # 判断当前时间是否在计划交期之后
                # 是的话就pass
                # 不是就排除掉
                if current_time > temp.scheduled_delivery:
                    pass
                else:
                    data = data.exclude(id=temp.id)
            # 写入数据
            all_count = data.count()
            page_info = PageInfo(request.GET.get('page'), all_count, 15,
                                 '/show_internal_control_indicators/?current_status=已经逾期&')
            internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
        elif current_status == '还未开始':
            current_time = date.today()
            data = InternalControlIndicators.objects.filter(order_date__gte=current_time, finished_number=None)
            # 写入数据
            all_count = data.count()
            page_info = PageInfo(request.GET.get('page'), all_count, 15,
                                 '/show_internal_control_indicators/?current_status=还未开始&')
            internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
        else:
            # 取出所有订单信息
            data = InternalControlIndicators.objects.all()
            all_count = data.count()
            page_info = PageInfo(request.GET.get('page'), all_count, 15, '/show_internal_control_indicators/?')
            internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
            # 标记当前状态
            current_status = '所有状态'

        # 打包数据
        context = {
            'internal_control_indicators': internal_control_indicators,
            'page_info': page_info,
            'current_status': current_status,
        }
        # 引导前端页面
        return render(request, '业务数据管理-内控指标汇总.html', context=context)
    else:
        # 获取当前动作
        current_action = request.POST.get('action')
        # 判断动作
        if current_action == '订单时间筛选':
            # 根据订单时间筛选
            # 从前端获取起止时间
            start_date = str(request.POST.get('start_date')).split('-')
            end_date = str(request.POST.get('end_date')).split('-')
            # 转换日期对象
            start_date = date(year=int(start_date[0]), month=int(start_date[1]), day=int(start_date[2]))
            end_date = date(year=int(end_date[0]), month=int(end_date[1]), day=int(end_date[2]))
            # 筛选此时间段内的订单数据
            data = InternalControlIndicators.objects.filter(order_date__gte=start_date,
                                                            scheduled_delivery__lte=end_date)
        elif current_action == '订单号搜索':
            # 根据订单号搜索
            # 获取搜索用订单号
            order_number = request.POST.get('order_number')
            # 筛选订单信息
            data = InternalControlIndicators.objects.filter(order_number__contains=order_number)
        # 如果出现未知动作，重载页面
        else:
            return redirect('show_internal_control_indicators')

        # 写入数据
        all_count = data.count()
        page_info = PageInfo(request.GET.get('page'), all_count, 9999,
                             '/show_internal_control_indicators/?')
        internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
        # 记录当前状态
        current_status = '所有状态'
        # 打包数据
        context = {
            'internal_control_indicators': internal_control_indicators,
            'page_info': page_info,
            'current_status': current_status,
        }
        # 引导前端页面
        return render(request, '业务数据管理-内控指标汇总.html', context=context)


# 增加内控指标汇总表方法
@login_required
@permission_required('performance.manage_internal_control_indicators', raise_exception=True)
def add_internal_control_indicators(request):
    # 从前端获取数据
    order_date = request.POST.get('order_date')  # 订单时间
    order_number = check_data_format(request.POST.get('order_number'), 'str')  # 订单号
    order_money = check_data_format(request.POST.get('order_money'), 'float')  # 订单额
    scheduled_delivery = request.POST.get('scheduled_delivery')  # 计划交期
    target_well_done_rate = check_data_format(request.POST.get('target_well_done_rate'), 'float')  # 目标成品率
    # 验证数据合法性
    for data in [order_number, order_money, target_well_done_rate]:
        if data is False:
            messages.error(request, '输入存在格式问题，请检查输入')
            return redirect('show_internal_control_indicators')

    # 转换日期对象
    order_date_list = order_date.split('-')
    scheduled_delivery_list = scheduled_delivery.split('-')
    order_date = date(year=int(order_date_list[0]), month=int(order_date_list[1]), day=int(order_date_list[2]))
    scheduled_delivery = date(year=int(scheduled_delivery_list[0]), month=int(scheduled_delivery_list[1]),
                              day=int(scheduled_delivery_list[2]))
    # 如果计划交期在订单时间之前，返回计划交期不能在订单时间之前错误
    if scheduled_delivery < order_date:
        messages.error(request, '计划交期不能在订单时间之前')
        return redirect('show_internal_control_indicators')

    # 从常量数据表中取出相应的常量数据
    # 规则为，日期在这条数据之前的最新一条常量数据
    # 获取符合条件的一批常量
    constant_data = ConstantData.objects.filter(date__lte=order_date).last()
    # 如果没获取到符合条件的常量，写入错误信息
    if not constant_data:
        messages.error(request, '未找到符合条件的常量数据，请检查订单时间或者联系管理员录入常量数据')
        return redirect('show_internal_control_indicators')
    # 获取常量数据
    target_medical_expenses_rate = constant_data.target_medical_expenses_rate  # 目标医药费百分比
    target_comprehensive_cost_rate = constant_data.target_comprehensive_cost_rate  # 目标综合成本百分比
    target_management_compliance_value = constant_data.target_management_compliance_value  # 目标管理符合数值
    # 计算数据项
    target_medical_expenses = order_money * target_medical_expenses_rate  # 目标医药费
    target_comprehensive_cost = order_money * target_comprehensive_cost_rate  # 目标综合成本
    target_management_compliance = order_money * target_management_compliance_value  # 目标管理符合数

    # 存入数据库
    InternalControlIndicators.objects.create(
        order_date=order_date,
        order_number=order_number,
        order_money=order_money,
        scheduled_delivery=scheduled_delivery,
        target_well_done_rate=target_well_done_rate,
        target_medical_expenses=target_medical_expenses,
        target_comprehensive_cost=target_comprehensive_cost,
        target_management_compliance=target_management_compliance,
    )

    # 写入数据增加成功提示
    messages.success(request, '数据增加成功')

    # 记录日志
    action = '增加了{}订单号为{}的订单数据'.format(order_date.strftime('%Y年%m月%d日'), order_number)
    add_log(request, action, '成功')

    # 重定向展示页面
    return redirect('show_internal_control_indicators')


# 删除内控指标汇总表方法
@login_required
@permission_required('performance.manage_internal_control_indicators', raise_exception=True)
def delete_internal_control_indicators(request):
    # 用来记录删除数据的年份
    year_set = set()
    # get为多选删除，post为单条删除
    if request.method == 'GET':
        delete_id = request.GET.getlist('delete_id', [])
        # 遍历删除
        for id in delete_id:
            data = InternalControlIndicators.objects.get(id=id)
            if data.actual_delivery:
                # 记录年份，方便更新月度数据
                year_set.add(data.actual_delivery.year)
            # 删除数据
            data.delete()
        # 写入数据删除成功提示
        messages.success(request, '选中数据删除成功')
        # 记录日志
        action = '删除了{}条订单数据'.format(len(delete_id))
        add_log(request, action, '成功')
        # 刷新月度考核结果
        CalcuteMonthlyPerformance.monthly_get_and_refresh(year_list=year_set)
        # 返回成功
        return HttpResponse('success')
    else:
        delete_id = request.POST.get('delete_id')
        # 从数据库中删除
        data = InternalControlIndicators.objects.get(id=delete_id)
        # 记录日志用时间、订单号
        order_date = data.order_date
        order_number = data.order_number
        if data.actual_delivery:
            # 记录年份，方便更新月度数据
            year_set.add(data.actual_delivery.year)
        # 删除数据
        data.delete()
        # 写入数据删除成功提示
        messages.success(request, '数据删除成功')
        # 记录日志
        action = '删除了{}订单号为{}的订单数据'.format(order_date.strftime('%Y年%m月%d日'), order_number)
        add_log(request, action, '成功')
        # 刷新月度考核结果
        CalcuteMonthlyPerformance.monthly_get_and_refresh(year_list=year_set)
        # 重载页面
        return redirect('show_internal_control_indicators')


# 修改内控指标汇总表方法
@login_required
@permission_required('performance.manage_internal_control_indicators', raise_exception=True)
def change_internal_control_indicators(request):
    # 从前端获取要修改的id
    change_id = request.POST.get('change_id')
    # 从前端获取修改后的数据
    change_order_date = request.POST.get('order_date')  # 订单时间
    change_order_number = check_data_format(request.POST.get('order_number'), 'str')  # 订单号
    change_order_money = check_data_format(request.POST.get('order_money'), 'float')  # 订单额
    change_scheduled_delivery = request.POST.get('scheduled_delivery')  # 计划交期
    change_target_well_done_rate = request.POST.get('target_well_done_rate')  # 目标成品率
    change_actual_delivery = request.POST.get('actual_delivery')  # 实际交期
    change_actual_well_done_rate = check_data_format(request.POST.get('actual_well_done_rate'), 'float')  # 实际成品率
    change_actual_medical_expenses = check_data_format(request.POST.get('actual_medical_expenses'), 'float')  # 实际医药费
    change_actual_cost = check_data_format(request.POST.get('actual_cost'), 'float')  # 实际成本
    change_actual_management_compliance = check_data_format(request.POST.get('actual_management_compliance'),
                                                            'int')  # 实际管理符合数
    # 验证数据合法性
    for data in [change_order_number, change_order_money, change_actual_well_done_rate, change_actual_medical_expenses,
                 change_actual_cost, change_actual_management_compliance]:
        if data is False:
            messages.error(request, '输入存在格式问题，请检查输入')
            return redirect('show_internal_control_indicators')
    # 从常量数据表中取出相应的常量数据
    # 规则为，日期在这条数据之前的最新一条常量数据
    # 获取符合条件的一批常量
    constant_data = ConstantData.objects.filter(date__lte=change_order_date).last()
    # 如果没获取到符合条件的常量，写入错误信息
    if not constant_data:
        messages.error(request, '未找到符合条件的常量数据，请检查订单时间或者联系管理员录入常量数据')
        return redirect('show_internal_control_indicators')
    # 获取常量数据
    target_medical_expenses_rate = constant_data.target_medical_expenses_rate  # 目标医药费百分比
    target_comprehensive_cost_rate = constant_data.target_comprehensive_cost_rate  # 目标综合成本百分比
    target_management_compliance_value = constant_data.target_management_compliance_value  # 目标管理符合数值
    # 计算数据项
    change_target_medical_expenses = change_order_money * target_medical_expenses_rate  # 目标医药费
    change_target_comprehensive_cost = change_order_money * target_comprehensive_cost_rate  # 目标综合成本
    change_target_management_compliance = change_order_money * target_management_compliance_value  # 目标管理符合数
    # 比对实际交期于计划交期，生成完成数于未完成数
    # 实际交期在计划交期之前，完成数 = 1，未完成数 = 0
    # 实际交期在计划交期之后，完成数 = 0，未完成数 = 1
    if change_actual_delivery <= change_scheduled_delivery:
        # 按时完成
        change_finished_number = 1
        change_unfinished_number = 0
    else:
        # 未按时完成
        change_finished_number = 0
        change_unfinished_number = 1

    # 转换日期对象
    order_date_list = change_order_date.split('-')
    scheduled_delivery_list = change_scheduled_delivery.split('-')
    actual_delivery_list = change_actual_delivery.split('-')
    change_date = date(year=int(order_date_list[0]), month=int(order_date_list[1]), day=int(order_date_list[2]))
    change_scheduled_delivery = date(year=int(scheduled_delivery_list[0]), month=int(scheduled_delivery_list[1]),
                                     day=int(scheduled_delivery_list[2]))
    change_actual_delivery = date(year=int(actual_delivery_list[0]), month=int(actual_delivery_list[1]),
                                  day=int(actual_delivery_list[2]))
    # 如果计划交期在订单时间之前，返回计划交期不能在订单时间之前错误
    if change_scheduled_delivery < change_order_date:
        messages.error(request, '计划交期不能在订单时间之前')
        return redirect('show_internal_control_indicators')

    # 从数据库中取出该数据
    data = InternalControlIndicators.objects.get(id=change_id)
    # 修改数据
    data.date = change_date  # 订单时间
    data.order_number = change_order_number  # 订单号
    data.order_money = change_order_money  # 订单额
    data.scheduled_delivery = change_scheduled_delivery  # 计划交期
    data.target_well_done_rate = change_target_well_done_rate  # 目标成品率
    data.target_medical_expenses = change_target_medical_expenses  # 目标医药费
    data.target_comprehensive_cost = change_target_comprehensive_cost  # 目标综合成本
    data.target_management_compliance = change_target_management_compliance  # 目标管理符合数
    data.actual_delivery = change_actual_delivery  # 实际交期
    data.finished_number = change_finished_number  # 完成数
    data.unfinished_number = change_unfinished_number  # 未完成数
    data.actual_well_done_rate = change_actual_well_done_rate  # 实际成品率
    data.actual_medical_expenses = change_actual_medical_expenses  # 实际医药费
    data.actual_cost = change_actual_cost  # 实际成本
    data.actual_management_compliance = change_actual_management_compliance  # 实际管理符合数

    # 保存更改
    data.save()

    # 返回数据修改成功提示
    messages.success(request, '数据修改成功')

    # 记录日志
    action = '修改了{}订单号为{}的订单数据'.format(change_order_date.strftime('%Y年%m月%d日'), change_order_number)
    add_log(request, action, '成功')

    # 刷新月度考核结果
    if change_actual_delivery:
        CalcuteMonthlyPerformance.monthly_get_and_refresh(year_list=[change_actual_delivery.year])

    # 重定向展示页面
    return redirect('show_internal_control_indicators')


# 上传月度营业数据表格方法
@login_required
@permission_required('performance.manage_monthly_sales_data', raise_exception=True)
def upload_monthly_performance(request):
    file_data = request.FILES.get('upload_file')
    result = UploadTable.upload_monthly_performance(file_data)
    if result.isdigit():
        # 写入导入成功提示
        messages.success(request, '导入成功')

        # 记录日志
        action = '上传导入了{}条月度营业数据'.format(result)
        add_log(request, action, '成功')

        # 刷新季度数据
        CalculateQuarterlySalesData.calculate_quarterly_sales_data()
        # 刷新当年季度考核结果
        CalculateQuarterlyPerformance.quarterly_get_and_refresh()
        # 刷新当年季度奖金额
        CalculateQuarterlyAward.quarterly_get_and_refresh()

        # 重定向数据展示页面
        return redirect('show_monthly_sales_data')
    else:
        # 写入相应的错误提示
        messages.error(request, result)
        # 记录日志
        action = '试图上传导入月度营业数据，错误：{}'.format(result)
        add_log(request, action, '失败')
        # 重定向数据展示页面
        return redirect('show_monthly_sales_data')


# 上传内控制表汇总表格方法
@login_required
@permission_required('performance.manage_internal_control_indicators', raise_exception=True)
def upload_internal_control_indicators_performance(request):
    file_data = request.FILES.get('upload_file')
    result = UploadTable.upload_internal_control_indicators_performance(file_data)
    if result.isdigit():
        # 写入导入成功提示
        messages.success(request, '导入成功')

        # 记录日志
        action = '上传导入了{}条订单数据'.format(result)
        add_log(request, action, '成功')

        CalcuteMonthlyPerformance.monthly_get_and_refresh()

        # 重定向数据展示页面
        return redirect('show_internal_control_indicators')
    else:
        # 写入相应的错误提示
        messages.error(request, result)
        # 记录日志
        action = '试图上传导入月度营业数据，错误：{}'.format(result)
        add_log(request, action, '失败')
        # 重定向数据展示页面
        return redirect('show_internal_control_indicators')


# 上传用户信息表格方法
@login_required
@permission_required('performance.manage_user', raise_exception=True)
def upload_user(request):
    file_data = request.FILES.get('upload_file')
    result = UploadTable.upload_user_excel(file_data)
    if result == 0:
        # 写入导入成功提示
        messages.success(request, '导入成功')
        # 记录日志
        action = '上传导入了{}条账号数据'.format(result)
        add_log(request, action, '成功')
        # 重定向账号展示页面
        return redirect('user_management')
    else:
        # 写入相应的错误提示
        messages.error(request, result)
        # 记录日志
        action = '试图上传导入账号数据，错误：{}'.format(result)
        add_log(request, action, '失败')
        # 重定向账号展示页面
        return redirect('user_management')


# 展示常量数据方法
@login_required
@permission_required('performance.manage_constant_data', raise_exception=True)
def show_constant_data(request):
    # 从数据库中取出所有数据
    constant_data = ConstantData.objects.order_by('-date').all()
    # 打包数据
    context = {
        'constant_data': constant_data,
    }
    # 引导前端页面
    return render(request, '常量数据.html', context=context)


# 增加常量数据方法
@login_required
@permission_required('performance.manage_constant_data', raise_exception=True)
def add_constant_data(request):
    # 从前端获取数据
    target_medical_expenses_rate = check_data_format(request.POST.get('target_medical_expenses_rate'), 'percentage')
    target_comprehensive_cost_rate = check_data_format(request.POST.get('target_comprehensive_cost_rate'), 'percentage')
    target_management_compliance_value = check_data_format(request.POST.get('target_management_compliance_value'),
                                                           'int')
    annual_target_turnover = check_data_format(request.POST.get('annual_target_turnover'), 'float')
    annual_target_award = check_data_format(request.POST.get('annual_target_award'), 'float')
    # 验证数据合法性
    for data in [target_medical_expenses_rate, target_comprehensive_cost_rate, target_management_compliance_value,
                 annual_target_turnover, annual_target_award]:
        if data is False:
            messages.error(request, '输入存在格式问题，请检查输入')
            return redirect('show_constant_data')

    # 写入数据库
    ConstantData.objects.create(
        target_medical_expenses_rate=target_medical_expenses_rate,
        target_comprehensive_cost_rate=target_comprehensive_cost_rate,
        target_management_compliance_value=target_management_compliance_value,
        annual_target_turnover=annual_target_turnover,
        annual_target_award=annual_target_award,
    )

    # 写入成功提示
    messages.success(request, '数据添加成功')

    # 记录日志
    action = '增加了一条常量数据'
    add_log(request, action, '成功')

    # 重定向展示页面
    return redirect('show_constant_data')


# 删除常量数据方法
@login_required
@permission_required('performance.manage_constant_data', raise_exception=True)
def delete_constant_data(request):
    # get为多选删除，post为单条删除
    if request.method == 'GET':
        delete_id = request.GET.getlist('delete_id', [])
        # 遍历删除
        for id in delete_id:
            ConstantData.objects.get(id=id).delete()
        # 写入删除成功提示
        messages.success(request, '选中数据删除成功')
        # 记录日志
        action = '多选删除了{}条常量数据'.format(len(delete_id))
        add_log(request, action, '成功')
        # 返回成功
        return HttpResponse('success')
    else:
        delete_id = request.POST.get('delete_id')
        # 从数据库中删除
        ConstantData.objects.get(id=delete_id).delete()
        # 写入删除成功提示
        messages.success(request, '数据删除成功')
        # 记录日志
        action = '删除了1条常量数据'
        add_log(request, action, '成功')
        # 重载页面
        return redirect('show_constant_data')


# 修改常量数据方法
@login_required
@permission_required('performance.manage_constant_data', raise_exception=True)
def change_constant_data(request):
    # 从前端获取数据
    change_id = request.POST.get('change_id')
    change_date = request.POST.get('date_m')
    change_target_medical_expenses_rate = check_data_format(request.POST.get('target_medical_expenses_rate_m'),
                                                            'percentage')
    change_target_comprehensive_cost_rate = check_data_format(request.POST.get('target_comprehensive_cost_rate_m'),
                                                              'percentage')
    change_target_management_compliance_value = check_data_format(
        request.POST.get('target_management_compliance_value_m'), 'int')
    change_annual_target_turnover = check_data_format(request.POST.get('annual_target_turnover_m'), 'float')
    change_annual_target_award = check_data_format(request.POST.get('annual_target_award_m'), 'float')
    # 验证数据合法性
    for data in [change_target_medical_expenses_rate, change_target_comprehensive_cost_rate,
                 change_target_management_compliance_value, change_annual_target_turnover, change_annual_target_award]:
        if data is False:
            messages.error(request, '输入存在格式问题，请检查输入')
            return redirect('show_constant_data')
    # 转换日期对象
    date_list = change_date.split('-')
    change_date = date(year=int(date_list[0]), month=int(date_list[1]), day=int(date_list[2]))

    # 从数据库中取出该数据
    data = ConstantData.objects.get(id=change_id)
    # 修改数据
    data.date = change_date
    data.target_medical_expenses_rate = change_target_medical_expenses_rate
    data.target_comprehensive_cost_rate = change_target_comprehensive_cost_rate
    data.target_management_compliance_value = change_target_management_compliance_value
    data.annual_target_turnover = change_annual_target_turnover
    data.annual_target_award = change_annual_target_award
    # 保存更改
    data.save()

    # 写入成功提示
    messages.success(request, '数据修改成功')

    # 记录日志
    action = '修改了{}常量数据'.format(change_date.strftime('%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日'))
    add_log(request, action, '成功')

    # 重定向展示页面
    return redirect('show_constant_data')


# 上传常量数据表格方法
@login_required
@permission_required('performance.manage_constant_data', raise_exception=True)
def upload_constant_data(request):
    file_data = request.FILES.get('upload_file')
    result = UploadTable.upload_constant_data(file_data)
    if result == 0:
        # 写入导入成功提示
        messages.success(request, '导入成功')
        # 重定向数据展示页面
        return redirect('show_constant_data')
    else:
        # 写入相应的错误提示
        messages.error(request, result)
        # 重定向数据展示页面
        return redirect('show_constant_data')


# 展示管理层月度绩效考核结果方法
@login_required
@permission_required('performance.view_monthly_performance', raise_exception=True)
def show_monthly_result(request):
    # 打包年份数据，去重并逆序排序
    dates = list(InternalControlIndicators.objects.values_list('actual_delivery', flat=True))
    date_list = []
    for date in dates:
        if date is not None:
            date_list.append(date)
    # 如果没有年份数据，直接返回空数据
    if date_list.__len__() == 0:
        context = {
            'current_year': '无数据',
        }
        # 引导前端页面
        return render(request, '数据统计-管理层月度绩效考核结果.html', context=context)
    year_list = set()
    for date in date_list:
        year_list.add(date.year)
    year_list = list(year_list)
    year_list.sort(reverse=True)
    # 如果是第一次访问，选取最新一年数据进行展示
    # 如果能获取年份，为用户选取年份筛选，取得这一年数据进行展示
    # 尝试获取年份
    select_year = request.GET.get('select_year')
    # 判断有无选取年份
    if select_year:
        # 有筛选年份
        # 记录当前年份
        current_year = select_year
    else:
        # 没有筛选年份
        # 记录当前年份
        current_year = year_list[0]
    # 选出当前年份的所有数据，按照月份正序排序
    monthly_result = MonthlyPerformance.objects.filter(year=current_year).order_by('month')
    # 打包数据
    context = {
        'monthly_result': monthly_result,
        'year_list': year_list,
        'current_year': int(current_year),  # 为了前端等值判断
    }
    # 引导前端页面
    return render(request, '数据统计-管理层月度绩效考核结果.html', context=context)


# 更新月度绩效考核结果的数据
@login_required
@permission_required('performance.view_monthly_performance', raise_exception=True)
def refresh_monthly_result(request):
    # 获取选中年份
    current_year = request.GET.get('select_year')
    # 无年份
    if current_year == '无数据':
        messages.error(request, '无相关数据')
        return redirect('/show_monthly_result')
    # 更新月度绩效考核结果中数据项的值，并更新数据库
    result = CalcuteMonthlyPerformance.monthly_get_and_refresh(current_year)
    if result == 'success':
        messages.success(request, '各月份考核结果已生成')
    elif result == '所有月份数据不足！请检查数据来源' or result == '刷新失败！请检查公式！':
        messages.error(request, result)
    else:
        messages.info(request, result)
    return redirect('/show_monthly_result?select_year=%s' % current_year)


# 展示管理层季度绩效考核结果方法
@login_required
@permission_required('performance.view_quarterly_performance', raise_exception=True)
def show_quarterly_result(request):
    # 打包年份数据，去重并逆序排序
    year_list = QuarterlySalesData.objects.values('year').distinct().order_by('-year')
    # 如果没有年份数据，直接返回空数据
    if not year_list:
        # 打包空数据
        context = {
            'current_year': '无数据',
        }
        # 引导前端页面
        return render(request, '数据统计-季度绩效考核结果.html', context=context)
    # 如果是第一次访问，选取最新一年数据进行展示
    # 如果能获取年份，为用户选取年份筛选，取得这一年数据进行展示
    # 尝试获取年份
    select_year = request.GET.get('select_year')
    # 判断有无选取年份
    if select_year:
        # 有筛选年份
        # 记录当前年份
        current_year = select_year
    else:
        # 没有筛选年份
        # 记录当前年份
        current_year = year_list.first()['year']
    # 选出当前年份的所有数据，按照月份正序排序
    quarterly_result = QuarterlyPerformance.objects.filter(year=current_year).order_by('quarter')
    # 打包数据
    context = {
        'quarterly_result': quarterly_result,
        'year_list': year_list,
        'current_year': int(current_year),  # 为了前端等值判断
    }
    # 引导前端页面
    return render(request, '数据统计-季度绩效考核结果.html', context=context)


# 更新季度绩效考核结果的数据
@login_required
@permission_required('performance.view_quarterly_performance', raise_exception=True)
def refresh_quarterly_result(request):
    # 获取选中年份
    current_year = request.GET.get('select_year')
    # 无年份
    if current_year == '无数据':
        messages.error(request, '无相关数据')
        return redirect('/show_quarterly_result')
    # 更新季度绩效考核结果中数据项的值，并更新数据库
    result = CalculateQuarterlyPerformance.quarterly_get_and_refresh(current_year)
    if result == 'success':
        messages.success(request, '各季度考核结果已生成')
    elif result == '所有季度数据不足！请检查数据来源':
        messages.error(request, result)
    else:
        messages.info(request, result)
    return redirect('/show_quarterly_result?select_year=%s' % current_year)


# 展示季度绩效奖金
@login_required
@permission_required('performance.view_quarterly_award', raise_exception=True)
def show_quarterly_award(request):
    # 打包年份数据，去重并逆序排序
    year_list = QuarterlySalesData.objects.values('year').distinct().order_by('-year')
    # 删除无数据的前三年
    try:
        year_list = list(year_list)
        for _ in range(3):
            year_list.pop()
    except:
        year_list = []
    # 如果没有年份数据，直接返回空数据
    if not year_list:
        # 打包空数据
        context = {
            'current_year': '无数据',
        }
        messages.info(request, '暂无数据！')
        # 引导前端页面
        return render(request, '数据统计-奖金表.html', context=context)
    # 如果是第一次访问，选取最新一年数据进行展示
    # 如果能获取年份，为用户选取年份筛选，取得这一年数据进行展示
    # 尝试获取年份
    select_year = request.GET.get('select_year')
    # 判断有无选取年份
    if select_year:
        # 有筛选年份
        # 记录当前年份
        current_year = select_year
    else:
        # 没有筛选年份
        # 记录当前年份
        current_year = year_list[0]['year']
    # 选出当前年份的所有数据，按照月份正序排序
    quarterly_award_result = QuarterlyAward.objects.filter(year=current_year).order_by('quarter')
    # 计算每项指标合计
    try:
        total_turnover_award = round(quarterly_award_result.aggregate(
            total_turnover_award=Sum('turnover_award'))['total_turnover_award'], 2)
        total_operating_rate_award = round(quarterly_award_result.aggregate(
            total_operating_rate_award=Sum('operating_rate_award'))['total_operating_rate_award'], 2)
        total_repaid_rate_award = round(quarterly_award_result.aggregate(
            total_repaid_rate_award=Sum('repaid_rate_award'))['total_repaid_rate_award'], 2)
        total_inventory_rate_award = round(quarterly_award_result.aggregate(
            total_inventory_rate_award=Sum('inventory_rate_award'))['total_inventory_rate_award'], 2)
        total_profit_rate_award = round(quarterly_award_result.aggregate(
            total_profit_rate_award=Sum('profit_rate_award'))['total_profit_rate_award'], 2)
        total_total = round(quarterly_award_result.aggregate(
            total_total=Sum('total'))['total_total'], 2)
    except:
        total_turnover_award = 0
        total_operating_rate_award = 0
        total_repaid_rate_award = 0
        total_inventory_rate_award = 0
        total_profit_rate_award = 0
        total_total = 0
    # 打包数据
    context = {
        'quarterly_award_result': quarterly_award_result,
        'year_list': year_list,
        'current_year': int(current_year),  # 为了前端等值判断
        'total_turnover_award': total_turnover_award,
        'total_operating_rate_award': total_operating_rate_award,
        'total_repaid_rate_award': total_repaid_rate_award,
        'total_inventory_rate_award': total_inventory_rate_award,
        'total_profit_rate_award': total_profit_rate_award,
        'total_total': total_total,
    }
    # 引导前端页面
    return render(request, '数据统计-奖金表.html', context=context)


# 仅展示月度营业数据方法
@login_required
@permission_required('performance.view_monthly_sales_data', raise_exception=True)
def display_monthly_sales_data(request):
    # 打包年份数据，去重并逆序排序
    year_list = MonthlySalesData.objects.values('year').distinct().order_by('-year')
    # 如果没有年份数据，直接返回空数据
    if not year_list:
        # 打包空数据
        context = {
            'current_year': '无数据',
        }
        # 引导前端页面
        return render(request, '数据统计-月度营业数据.html', context=context)
    # 如果是第一次访问，选取最新一年数据进行展示
    # 如果能获取年份，为用户选取年份筛选，取得这一年数据进行展示
    # 尝试获取年份
    select_year = request.GET.get('select_year')
    # 判断有无选取年份
    if select_year:
        # 有筛选年份
        # 记录当前年份
        current_year = select_year
    else:
        # 没有筛选年份
        # 记录当前年份
        current_year = year_list.first()['year']
    # 选出当前年份的所有数据，按照月份正序排序
    monthly_sales_data = MonthlySalesData.objects.filter(year=current_year).order_by('month')
    # 打包数据
    context = {
        'monthly_sales_data': monthly_sales_data,
        'year_list': year_list,
        'current_year': int(current_year),  # 为了前端等值判断
    }
    # 引导前端页面
    return render(request, '数据统计-月度营业数据.html', context=context)


# 仅展示季度营业数据方法
@login_required
@permission_required('performance.view_quarterly_sales_data', raise_exception=True)
def display_quarterly_sales_data(request):
    # 打包年份数据，去重并逆序排序
    year_list = QuarterlySalesData.objects.values('year').distinct().order_by('-year')
    # 如果没有年份数据，直接返回空数据
    if not year_list:
        # 打包空数据
        context = {
            'current_year': '无数据',
        }
        # 引导前端页面
        return render(request, '数据统计-季度营业数据.html', context=context)
    # 如果是第一次访问，选取最新一年数据进行展示
    # 如果能获取年份，为用户选取年份筛选，取得这一年数据进行展示
    # 尝试获取年份
    select_year = request.GET.get('select_year')
    # 判断有无选取年份
    if select_year:
        # 有筛选年份
        # 记录当前年份
        current_year = select_year
    else:
        # 没有筛选年份
        # 记录当前年份
        current_year = year_list.first()['year']
    # 选出当前年份的所有数据，按照季度正序排序
    quarterly_sales_data = QuarterlySalesData.objects.filter(year=current_year).order_by('quarter')
    # 打包数据
    context = {
        'quarterly_sales_data': quarterly_sales_data,
        'year_list': year_list,
        'current_year': int(current_year),  # 为了前端等值判断
    }
    # 引导前端页面
    return render(request, '数据统计-季度营业数据.html', context=context)


# 仅展示内控指标汇总方法
@login_required
@permission_required('performance.view_internal_control_indicators', raise_exception=True)
def display_internal_control_indicators(request):
    # GET为请求页面，展示所有数据
    # POST为带时间段筛选请求，取出时间段内数据展示
    if request.method == 'GET':
        # 尝试获取选择的状态
        # 如果没有或者是'所有状态'，就取出所有数据
        # 如果有状态，就筛选出相应状态的订单
        current_status = request.GET.get('current_status')
        if current_status == '按时完成':
            # 完成数为1
            data = InternalControlIndicators.objects.filter(finished_number=1)
            all_count = data.count()
            page_info = PageInfo(request.GET.get('page'), all_count, 15,
                                 '/display_internal_control_indicators/?current_status=按时完成&')
            internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
        elif current_status == '尚未完成':
            # 没有完成数
            # 当前时间没超过计划交期
            # 时间进度小于等于70%
            data = InternalControlIndicators.objects.filter(finished_number=None)
            # 获取当前时间
            current_time = date.today()
            # 遍历循环，不符合条件的排除掉
            for temp in data:
                # 计算时间进度百分比
                # 如果订单时间跟计划交期相同，则排除掉
                if temp.order_date == temp.scheduled_delivery:
                    data = data.exclude(id=temp.id)
                    continue
                percentage = (current_time - temp.order_date).days / (temp.scheduled_delivery - temp.order_date).days
                # 当前时间大于计划时间的排除
                # 时间进度百分比超过0.7的排除
                # 当前时间小于订单时间的排除
                if current_time > temp.scheduled_delivery or percentage > 0.7 or current_time < temp.order_date:
                    data = data.exclude(id=temp.id)
            # 写入数据
            all_count = data.count()
            page_info = PageInfo(request.GET.get('page'), all_count, 15,
                                 '/display_internal_control_indicators/?current_status=尚未完成&')
            internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
        elif current_status == '逾期完成':
            # 完成数为0
            data = InternalControlIndicators.objects.filter(finished_number=0)
            all_count = data.count()
            page_info = PageInfo(request.GET.get('page'), all_count, 15,
                                 '/display_internal_control_indicators/?current_status=逾期完成&')
            internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
        elif current_status == '快到交期':
            # 没有完成数
            # 当前时间没超过计划交期
            # 时间进度大于70%
            data = InternalControlIndicators.objects.filter(finished_number=None)
            # 获取当前时间
            current_time = date.today()
            # 遍历循环，不符合条件的排除掉
            for temp in data:
                # 计算时间进度百分比
                # 当订单时间与计划交期一样时，只有当前时间也一样才是快到交期
                if temp.scheduled_delivery == temp.order_date:
                    if current_time == temp.order_date:
                        percentage = 1
                    else:
                        data = data.exclude(id=temp.id)
                        continue
                else:
                    percentage = (current_time - temp.order_date).days / (
                            temp.scheduled_delivery - temp.order_date).days
                # 当前时间大于计划时间的排除
                # 时间进度百分比未超过0.7的排除
                if current_time > temp.scheduled_delivery or percentage <= 0.7:
                    data = data.exclude(id=temp.id)
            # 写入数据
            all_count = data.count()
            page_info = PageInfo(request.GET.get('page'), all_count, 15,
                                 '/display_internal_control_indicators/?current_status=快到交期&')
            internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
        elif current_status == '已经逾期':
            # 没有完成数
            # 当前时间在计划交期之后
            data = InternalControlIndicators.objects.filter(finished_number=None)
            # 获取当前时间
            current_time = date.today()
            # 遍历判断，不符合条件的排除掉
            for temp in data:
                # 判断当前时间是否在计划交期之后
                # 是的话就pass
                # 不是就排除掉
                if current_time > temp.scheduled_delivery:
                    pass
                else:
                    data = data.exclude(id=temp.id)
            # 写入数据
            all_count = data.count()
            page_info = PageInfo(request.GET.get('page'), all_count, 15,
                                 '/display_internal_control_indicators/?current_status=已经逾期&')
            internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
        elif current_status == '还未开始':
            current_time = date.today()
            data = InternalControlIndicators.objects.filter(order_date__gte=current_time, finished_number=None)
            # 写入数据
            all_count = data.count()
            page_info = PageInfo(request.GET.get('page'), all_count, 15,
                                 '/show_internal_control_indicators/?current_status=还未开始&')
            internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
        else:
            # 取出所有订单信息
            data = InternalControlIndicators.objects.all()
            all_count = data.count()
            page_info = PageInfo(request.GET.get('page'), all_count, 15, '/display_internal_control_indicators/?')
            internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
            # 标记当前状态
            current_status = '所有状态'

        # 打包数据
        context = {
            'internal_control_indicators': internal_control_indicators,
            'page_info': page_info,
            'current_status': current_status,
        }
        # 引导前端页面
        return render(request, '数据统计-内控指标汇总.html', context=context)
    else:
        # 获取当前动作
        current_action = request.POST.get('action')
        # 判断动作
        if current_action == '订单时间筛选':
            # 根据订单时间筛选
            # 从前端获取起止时间
            start_date = str(request.POST.get('start_date')).split('-')
            end_date = str(request.POST.get('end_date')).split('-')
            # 转换日期对象
            start_date = date(year=int(start_date[0]), month=int(start_date[1]), day=int(start_date[2]))
            end_date = date(year=int(end_date[0]), month=int(end_date[1]), day=int(end_date[2]))
            # 筛选此时间段内的订单数据
            data = InternalControlIndicators.objects.filter(order_date__gte=start_date,
                                                            scheduled_delivery__lte=end_date)
        elif current_action == '订单号搜索':
            # 根据订单号搜索
            # 获取搜索用订单号
            order_number = request.POST.get('order_number')
            # 筛选订单信息
            data = InternalControlIndicators.objects.filter(order_number__contains=order_number)
        # 如果出现未知动作，重载页面
        else:
            return redirect('display_internal_control_indicators')

        # 写入数据
        all_count = data.count()
        page_info = PageInfo(request.GET.get('page'), all_count, 9999,
                             '/show_internal_control_indicators/?')
        internal_control_indicators = data.order_by('-order_date')[page_info.start():page_info.end()]
        # 记录当前状态
        current_status = '所有状态'
        # 打包数据
        context = {
            'internal_control_indicators': internal_control_indicators,
            'page_info': page_info,
            'current_status': current_status,
        }
        # 引导前端页面
        return render(request, '数据统计-内控指标汇总.html', context=context)


# 导出月度营业数据excel
@login_required
@permission_required('performance.view_monthly_sales_data', raise_exception=True)
def export_monthly_sales_data(request):
    return ExportTable.export_monthly_sales_data()


# 导出季度营业数据excel
@login_required
@permission_required('performance.view_quarterly_sales_data', raise_exception=True)
def export_quarterly_sales_data(request):
    return ExportTable.export_quarterly_sales_data()


# 导出内控指标汇总excel
@login_required
@permission_required('performance.view_internal_control_indicators', raise_exception=True)
def export_internal_control_indicators(request):
    return ExportTable.export_internal_control_indicators()


# 导出月度绩效考核结果
@login_required
@permission_required('performance.view_monthly_performance', raise_exception=True)
def export_monthly_performance(request):
    return ExportTable.export_monthly_performance()


# 导出季度绩效考核结果
@login_required
@permission_required('performance.view_quarterly_performance', raise_exception=True)
def export_quarterly_performance(request):
    return ExportTable.export_quarterly_performance()


# 导出季度绩效奖金
@login_required
@permission_required('performance.view_quarterly_award', raise_exception=True)
def export_quarterly_award(request):
    return ExportTable.export_quarterly_award()


# 导出用户操作日志
@login_required
@permission_required('performance.user_logs', raise_exception=True)
def export_user_logs(request):
    return ExportTable.export_user_logs()


# 展示公式修改页-月度绩效考核
@login_required
@permission_required('performance.manage_formula', raise_exception=True)
def month_result_formula(request):
    # 第一次进入系统时，获取不到公式，则默认为原始公式
    try:
        delivery_rate = MonthlyFormula.objects.filter(target_item='交付率').first().formula
        well_done_rate = MonthlyFormula.objects.filter(target_item='成品率').first().formula
        medical_expenses = MonthlyFormula.objects.filter(target_item='医药费').first().formula
        month_dig_cost = MonthlyFormula.objects.filter(target_item='当月挖掘成本').first().formula
        field_management_well_rate = MonthlyFormula.objects.filter(target_item='现场管理符合率').first().formula
    except:
        MonthlyFormula.objects.create(target_item='交付率', formula='A/B')
        MonthlyFormula.objects.create(target_item='成品率', formula='C/B')
        MonthlyFormula.objects.create(target_item='医药费', formula='D-E')
        MonthlyFormula.objects.create(target_item='当月挖掘成本', formula='F-G')
        MonthlyFormula.objects.create(target_item='现场管理符合率', formula='H/I')
        delivery_rate = MonthlyFormula.objects.filter(target_item='交付率').first().formula
        well_done_rate = MonthlyFormula.objects.filter(target_item='成品率').first().formula
        medical_expenses = MonthlyFormula.objects.filter(target_item='医药费').first().formula
        month_dig_cost = MonthlyFormula.objects.filter(target_item='当月挖掘成本').first().formula
        field_management_well_rate = MonthlyFormula.objects.filter(target_item='现场管理符合率').first().formula
    month_result_item_A = SystemConfig.objects.first().month_result_item_A
    month_result_item_B = SystemConfig.objects.first().month_result_item_B
    month_result_item_C = SystemConfig.objects.first().month_result_item_C
    month_result_item_D = SystemConfig.objects.first().month_result_item_D
    month_result_item_E = SystemConfig.objects.first().month_result_item_E
    month_result_item_F = SystemConfig.objects.first().month_result_item_F
    month_result_item_G = SystemConfig.objects.first().month_result_item_G
    month_result_item_H = SystemConfig.objects.first().month_result_item_H
    month_result_item_I = SystemConfig.objects.first().month_result_item_I
    context = {
        'delivery_rate': delivery_rate,
        'well_done_rate': well_done_rate,
        'medical_expenses': medical_expenses,
        'month_dig_cost': month_dig_cost,
        'field_management_well_rate': field_management_well_rate,
        'month_result_item_A': month_result_item_A,
        'month_result_item_B': month_result_item_B,
        'month_result_item_C': month_result_item_C,
        'month_result_item_D': month_result_item_D,
        'month_result_item_E': month_result_item_E,
        'month_result_item_F': month_result_item_F,
        'month_result_item_G': month_result_item_G,
        'month_result_item_H': month_result_item_H,
        'month_result_item_I': month_result_item_I,
    }
    return render(request, '报表公式修改-管理层月度绩效考核结果.html', context=context)


# 展示公式修改页-季度绩效考核
@login_required
@permission_required('performance.manage_formula', raise_exception=True)
def quarter_result_formula(request):
    # 第一次进入系统时，获取不到公式，则默认为原始公式
    try:
        turnover = QuarterlyFormula.objects.filter(target_item='营业额').first().formula
        operating_rate = QuarterlyFormula.objects.filter(target_item='营业费率').first().formula
        repaid_rate = QuarterlyFormula.objects.filter(target_item='回款率').first().formula
        inventory_rate = QuarterlyFormula.objects.filter(target_item='库存率').first().formula
        profit_rate = QuarterlyFormula.objects.filter(target_item='利润率').first().formula
    except:
        QuarterlyFormula.objects.create(target_item='营业额', formula='A')
        QuarterlyFormula.objects.create(target_item='营业费率', formula='B/A')
        QuarterlyFormula.objects.create(target_item='回款率', formula='C/A')
        QuarterlyFormula.objects.create(target_item='库存率', formula='D/A')
        QuarterlyFormula.objects.create(target_item='利润率', formula='E/A')
        turnover = QuarterlyFormula.objects.filter(target_item='营业额').first().formula
        operating_rate = QuarterlyFormula.objects.filter(target_item='营业费率').first().formula
        repaid_rate = QuarterlyFormula.objects.filter(target_item='回款率').first().formula
        inventory_rate = QuarterlyFormula.objects.filter(target_item='库存率').first().formula
        profit_rate = QuarterlyFormula.objects.filter(target_item='利润率').first().formula
    quarter_result_item_A = SystemConfig.objects.first().quarter_result_item_A
    quarter_result_item_B = SystemConfig.objects.first().quarter_result_item_B
    quarter_result_item_C = SystemConfig.objects.first().quarter_result_item_C
    quarter_result_item_D = SystemConfig.objects.first().quarter_result_item_D
    quarter_result_item_E = SystemConfig.objects.first().quarter_result_item_E
    context = {
        'turnover': turnover,
        'operating_rate': operating_rate,
        'repaid_rate': repaid_rate,
        'inventory_rate': inventory_rate,
        'profit_rate': profit_rate,
        'quarter_result_item_A': quarter_result_item_A,
        'quarter_result_item_B': quarter_result_item_B,
        'quarter_result_item_C': quarter_result_item_C,
        'quarter_result_item_D': quarter_result_item_D,
        'quarter_result_item_E': quarter_result_item_E,
    }
    return render(request, '报表公式修改-季度绩效考核结果.html', context=context)


# 展示公式修改页-季度奖金额
@login_required
@permission_required('performance.manage_formula', raise_exception=True)
def quarter_award_formula(request):
    # 第一次进入系统时，获取不到公式，则默认为原始公式
    try:
        turnover = QuarterlyAwardFormula.objects.filter(target_item='营业额').first().formula
        operating_rate = QuarterlyAwardFormula.objects.filter(target_item='营业费率').first().formula
        repaid_rate = QuarterlyAwardFormula.objects.filter(target_item='回款率').first().formula
        inventory_rate = QuarterlyAwardFormula.objects.filter(target_item='库存率').first().formula
        profit_rate = QuarterlyAwardFormula.objects.filter(target_item='利润率').first().formula
    except:
        QuarterlyAwardFormula.objects.create(target_item='营业额', formula='C*(B/A)*0.2/A*0.25*C')
        QuarterlyAwardFormula.objects.create(target_item='营业费率', formula='C*(B/A)*0.3/(1-E)*(1-D)')
        QuarterlyAwardFormula.objects.create(target_item='回款率', formula='C*(B/A)*0.2*F')
        QuarterlyAwardFormula.objects.create(target_item='库存率', formula='C*(B/A)*0.1/(1-H)*(1-G)')
        QuarterlyAwardFormula.objects.create(target_item='利润率', formula='C*(B/A)*0.2/K*I')
        turnover = QuarterlyAwardFormula.objects.filter(target_item='营业额').first().formula
        operating_rate = QuarterlyAwardFormula.objects.filter(target_item='营业费率').first().formula
        repaid_rate = QuarterlyAwardFormula.objects.filter(target_item='回款率').first().formula
        inventory_rate = QuarterlyAwardFormula.objects.filter(target_item='库存率').first().formula
        profit_rate = QuarterlyAwardFormula.objects.filter(target_item='利润率').first().formula
    quarter_award_item_A = SystemConfig.objects.first().quarter_award_item_A
    quarter_award_item_B = SystemConfig.objects.first().quarter_award_item_B
    quarter_award_item_C = SystemConfig.objects.first().quarter_award_item_C
    quarter_award_item_D = SystemConfig.objects.first().quarter_award_item_D
    quarter_award_item_E = SystemConfig.objects.first().quarter_award_item_E
    quarter_award_item_F = SystemConfig.objects.first().quarter_award_item_F
    quarter_award_item_G = SystemConfig.objects.first().quarter_award_item_G
    quarter_award_item_H = SystemConfig.objects.first().quarter_award_item_H
    quarter_award_item_I = SystemConfig.objects.first().quarter_award_item_I
    quarter_award_item_K = SystemConfig.objects.first().quarter_award_item_K
    context = {
        'turnover': turnover,
        'operating_rate': operating_rate,
        'repaid_rate': repaid_rate,
        'inventory_rate': inventory_rate,
        'profit_rate': profit_rate,
        'quarter_award_item_A': quarter_award_item_A,
        'quarter_award_item_B': quarter_award_item_B,
        'quarter_award_item_C': quarter_award_item_C,
        'quarter_award_item_D': quarter_award_item_D,
        'quarter_award_item_E': quarter_award_item_E,
        'quarter_award_item_F': quarter_award_item_F,
        'quarter_award_item_G': quarter_award_item_G,
        'quarter_award_item_H': quarter_award_item_H,
        'quarter_award_item_I': quarter_award_item_I,
        'quarter_award_item_K': quarter_award_item_K,
    }
    return render(request, '报表公式修改-奖金表.html', context=context)


# 修改月度绩效考核结果公式方法
@login_required
@permission_required('performance.manage_formula', raise_exception=True)
def change_month_formula(request):
    # 获取输入的每个公式
    delivery_rate = request.POST.get('delivery_rate')
    well_done_rate = request.POST.get('well_done_rate')
    medical_expenses = request.POST.get('medical_expenses')
    overall_cost = request.POST.get('overall_cost')
    field_management = request.POST.get('field_management')
    # 验证公式合法性
    for data in [delivery_rate, well_done_rate, medical_expenses, overall_cost, field_management]:
        if cleaned_formula(data) is False:
            messages.error(request, '公式中存在非法字符，请重试')
            return redirect('month_result_formula')
    # 合法数据
    MonthlyFormula.objects.filter(target_item='交付率').update(formula=delivery_rate)
    MonthlyFormula.objects.filter(target_item='成品率').update(formula=well_done_rate)
    MonthlyFormula.objects.filter(target_item='医药费').update(formula=medical_expenses)
    MonthlyFormula.objects.filter(target_item='内控综合成本').update(formula=overall_cost)
    MonthlyFormula.objects.filter(target_item='现场管理符合率').update(formula=field_management)
    messages.success(request, '公式更改成功')
    # 记录日志
    action = '修改了月度绩效考核结果公式'
    add_log(request, action, '成功')
    # 修改月度考核结果
    CalcuteMonthlyPerformance.monthly_get_and_refresh()
    return redirect('month_result_formula')


# 修改季度绩效考核结果方法
@login_required
@permission_required('performance.manage_formula', raise_exception=True)
def change_quarter_formula(request):
    # 获取输入的每个公式
    turnover = request.POST.get('turnover')
    operating_rate = request.POST.get('operating_rate')
    repaid_rate = request.POST.get('repaid_rate')
    inventory_rate = request.POST.get('inventory_rate')
    profit_rate = request.POST.get('profit_rate')
    # 验证公式合法性
    for data in [turnover, operating_rate, repaid_rate, inventory_rate, profit_rate]:
        if cleaned_formula(data) is False:
            messages.error(request, '公式中存在非法字符，请重试')
            return redirect('quarter_result_formula')
    # 合法数据
    QuarterlyFormula.objects.filter(target_item='营业额').update(formula=turnover)
    QuarterlyFormula.objects.filter(target_item='营业费率').update(formula=operating_rate)
    QuarterlyFormula.objects.filter(target_item='回款率').update(formula=repaid_rate)
    QuarterlyFormula.objects.filter(target_item='库存率').update(formula=inventory_rate)
    QuarterlyFormula.objects.filter(target_item='利润率').update(formula=profit_rate)
    messages.success(request, '公式更改成功')
    # 记录日志
    action = '修改了季度绩效考核结果公式'
    add_log(request, action, '成功')
    # 刷新当年季度考核结果
    CalculateQuarterlyPerformance.quarterly_get_and_refresh()
    return redirect('quarter_result_formula')


# 修改季度奖金额方法
@login_required
@permission_required('performance.manage_formula', raise_exception=True)
def change_quarter_award_formula(request):
    # 获取输入的每个公式
    turnover = request.POST.get('turnover')
    operating_rate = request.POST.get('operating_rate')
    repaid_rate = request.POST.get('repaid_rate')
    inventory_rate = request.POST.get('inventory_rate')
    profit_rate = request.POST.get('profit_rate')
    # 验证公式合法性
    for data in [turnover, operating_rate, repaid_rate, inventory_rate, profit_rate]:
        if cleaned_formula(data) is False:
            messages.error(request, '公式中存在非法字符，请重试')
            return redirect('quarter_award_formula')
    # 合法数据
    QuarterlyAwardFormula.objects.filter(target_item='营业额').update(formula=turnover)
    QuarterlyAwardFormula.objects.filter(target_item='营业费率').update(formula=operating_rate)
    QuarterlyAwardFormula.objects.filter(target_item='回款率').update(formula=repaid_rate)
    QuarterlyAwardFormula.objects.filter(target_item='库存率').update(formula=inventory_rate)
    QuarterlyAwardFormula.objects.filter(target_item='利润率').update(formula=profit_rate)
    messages.success(request, '公式更改成功')
    # 记录日志
    action = '修改了季度奖金额结果公式'
    add_log(request, action, '成功')
    # 刷新当年季度考核结果
    CalculateQuarterlyAward.quarterly_get_and_refresh()
    return redirect('quarter_award_formula')


# 修改月度结果数据项
@login_required
@permission_required('performance.manage_formula', raise_exception=True)
def change_month_result_item(request):
    key = request.GET.get('key')
    value = request.GET.get('value')
    if key == 'A':
        SystemConfig.objects.update(month_result_item_A=value)
    elif key == 'B':
        SystemConfig.objects.update(month_result_item_B=value)
    elif key == 'C':
        SystemConfig.objects.update(month_result_item_C=value)
    elif key == 'D':
        SystemConfig.objects.update(month_result_item_D=value)
    elif key == 'E':
        SystemConfig.objects.update(month_result_item_E=value)
    elif key == 'F':
        SystemConfig.objects.update(month_result_item_F=value)
    elif key == 'G':
        SystemConfig.objects.update(month_result_item_G=value)
    elif key == 'H':
        SystemConfig.objects.update(month_result_item_H=value)
    elif key == 'I':
        SystemConfig.objects.update(month_result_item_I=value)
    return HttpResponse('success')


# 修改季度结果数据项
@login_required
@permission_required('performance.manage_formula', raise_exception=True)
def change_quarter_result_item(request):
    key = request.GET.get('key')
    value = request.GET.get('value')
    if key == 'A':
        SystemConfig.objects.update(quarter_result_item_A=value)
    elif key == 'B':
        SystemConfig.objects.update(quarter_result_item_B=value)
    elif key == 'C':
        SystemConfig.objects.update(quarter_result_item_C=value)
    elif key == 'D':
        SystemConfig.objects.update(quarter_result_item_D=value)
    elif key == 'E':
        SystemConfig.objects.update(quarter_result_item_E=value)
    return HttpResponse('success')


# 修改季度奖金数据项
@login_required
@permission_required('performance.manage_formula', raise_exception=True)
def change_quarter_award_item(request):
    key = request.GET.get('key')
    value = request.GET.get('value')
    if key == 'A':
        SystemConfig.objects.update(quarter_award_item_A=value)
    elif key == 'B':
        SystemConfig.objects.update(quarter_award_item_B=value)
    elif key == 'C':
        SystemConfig.objects.update(quarter_award_item_C=value)
    elif key == 'D':
        SystemConfig.objects.update(quarter_award_item_D=value)
    elif key == 'E':
        SystemConfig.objects.update(quarter_award_item_E=value)
    elif key == 'F':
        SystemConfig.objects.update(quarter_award_item_F=value)
    elif key == 'G':
        SystemConfig.objects.update(quarter_award_item_G=value)
    elif key == 'H':
        SystemConfig.objects.update(quarter_award_item_H=value)
    elif key == 'I':
        SystemConfig.objects.update(quarter_award_item_I=value)
    elif key == 'K':
        SystemConfig.objects.update(quarter_award_item_K=value)
    return HttpResponse('success')


def download_monthly_sales_modal(request):
    file = open('media/月度营业数据-模板.xls', 'rb')
    response = HttpResponse(file)
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response['Content-Disposition'] = "attachment;filename*=UTF-8''{}".format(escape_uri_path("月度营业数据-模板.xls"))
    return response


def download_internal_control_modal(request):
    file = open('media/内控指标汇总-模板.xls', 'rb')
    response = HttpResponse(file)
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response['Content-Disposition'] = "attachment;filename*=UTF-8''{}".format(escape_uri_path("内控指标汇总-模板.xls"))
    return response


# 展示用户操作日志方法
@login_required
@permission_required('performance.user_logs', raise_exception=True)
def show_user_logs(request):
    if request.method == 'GET':
        # 第一次访问此页面，取出所有数据
        logs = Logs.objects.all()
    else:
        # 获取当前动作
        current_action = request.POST.get('current_action')
        # 判断动作
        if current_action == '姓名或工号搜索':
            # 获取输入的搜索内容
            user_name_number = request.POST.get('user_name_number')
            # 从数据库中取出用户姓名或工号包含搜索内容的日志项
            logs = Logs.objects.filter(
                Q(user_name__contains=user_name_number) | Q(job_number__contains=user_name_number))
        elif current_action == '操作时间筛选':
            # 从前端获取起止时间
            start_time = str(request.POST.get('start_time')).split('-')
            end_time = str(request.POST.get('end_time')).split('-')

            # 转换日期对象
            start_time = datetime(year=int(start_time[0]), month=int(start_time[1]), day=int(start_time[2]),
                                  hour=int(start_time[3]), minute=int(start_time[4]))
            end_time = datetime(year=int(end_time[0]), month=int(end_time[1]), day=int(end_time[2]),
                                hour=int(end_time[3]), minute=int(end_time[4]))
            # 筛选此时间段内的订单数据
            logs = Logs.objects.filter(log_time__gte=start_time,
                                       log_time__lte=end_time)
        else:
            # 未知动作，重定向本页面
            return redirect('show_user_logs')
    # 分页展示，根据时间逆序排序
    counts = logs.count()
    page_info = PageInfo(request.GET.get('page'), counts, 20, '/show_user_logs?')
    page_logs = logs.order_by('-log_time')[page_info.start():page_info.end()]
    # 打包数据可视化用数据
    # 当前展示日志的成功与失败数
    success_log_num = logs.filter(result='成功').count()
    fail_log_num = logs.filter(result='失败').count()
    # 当前日志中用户及对应日志数量
    # 获取所有记录日志的用户姓名
    user_names = set(Logs.objects.values_list('user_name', flat=True))
    # 取出每个人对应的日志数量
    name_num = {}
    for name in user_names:
        name_num[name] = Logs.objects.filter(user_name=name).count()
    # 打包数据，日志按照时间倒序排序
    context = {
        'logs': page_logs,
        'success_log_num': success_log_num,
        'fail_log_num': fail_log_num,
        'user_names': list(name_num.keys()),
        'name_num': name_num,
        'page_info': page_info,
    }
    # 返回前端页面
    return render(request, '系统安全备份-用户操作日志.html', context=context)


# 展示数据库备份方法
@login_required
@permission_required('performance.manage_backups', raise_exception=True)
def show_database_backup(request):
    # 获取当前备份
    backups = DatabaseBackup.get_backups()
    # 获取定期备份信息
    days = SystemConfig.objects.first().days_to_auto_backup
    email = SystemConfig.objects.first().backup_to_email
    # 打包数据
    context = {
        'backups': backups,
        'days': days,
        'email': email,
    }
    # 引导前端页面
    return render(request, '系统安全备份-数据备份还原.html', context=context)


# 备份数据库方法
@login_required
@permission_required('performance.manage_backups', raise_exception=True)
def backup_database(request):
    # 获取备份备注
    remark = request.POST.get('remark')
    # 调用备份方法
    res = DatabaseBackup.backup_database(remark)
    # 根据返回值判断备份是否成功
    if res is True:
        # 写入成功提示
        messages.success(request, '备份成功')
        # 记录日志
        action = '进行了一次数据库备份，备注为:{}'.format(remark)
        add_log(request, action, '成功')
    else:
        # 写入失败提示
        messages.error(request, '出现错误，请刷新重试')
        # 记录日志
        action = '尝试进行一次数据库备份'
        add_log(request, action, '失败')
    # 重定向到展示数据库备份页面
    return redirect('show_database_backup')


# 恢复数据库方法
@login_required
@permission_required('performance.manage_backups', raise_exception=True)
def load_database(request):
    # 获取要恢复的文件名
    file_name = request.POST.get('file_name')
    # 检查后缀是不是json
    # 不是的话返回仅支持json文件
    if file_name.split('.')[-1] != 'json':
        # 写入错误提示
        messages.error(request, '仅支持json文件')
        # 记录日志
        action = '尝试使用非json文件恢复数据库'
        add_log(request, action, '失败')
        # 重定向展示数据库备份页面
        return redirect('show_database_backup')
    # 调用恢复方法
    res = DatabaseBackup.load_database(file_name)
    # 根据返回值判断备份是否成功
    if res is True:
        # 写入成功提示
        messages.success(request, '恢复成功')
        # 记录日志
        action = '将系统数据库通过{}文件进行恢复'.format(file_name)
        add_log(request, action, '成功')
    else:
        # 写入失败提示
        messages.error(request, '出现错误，请刷新重试')
        # 记录日志
        action = '尝试使用{}文件进行一次数据库恢复'.format(file_name)
        add_log(request, action, '失败')
    # 重定向到展示数据库备份页面
    return redirect('show_database_backup')


# 删除数据库备份文件方法
@login_required
@permission_required('performance.manage_backups', raise_exception=True)
def delete_backup(request):
    # 获取要删除的文件名
    file_name = request.POST.get('file_name')
    # 调用删除备份文件方法
    res = DatabaseBackup.delete_backup(file_name)
    # 根据返回值判断备份是否成功
    if res is True:
        # 写入成功提示
        messages.success(request, '删除成功')
        # 记录日志
        action = '删除{}备份文件'.format(file_name)
        add_log(request, action, '成功')
    else:
        # 写入失败提示
        messages.error(request, '出现错误，请刷新重试')
        # 记录日志
        action = '尝试删除{}备份文件'.format(file_name)
        add_log(request, action, '失败')
    # 重定向到展示数据库备份页面
    return redirect('show_database_backup')


# 下载数据库备份方法
def download_backup(request):
    # 获取要下载的文件名
    file_name = request.POST.get('file_name')
    # 调用下载备份方法
    res = DatabaseBackup.download_backup(file_name)
    # 根据返回值判断备份是否成功
    if res is False:
        # 写入失败提示
        messages.error(request, '发生错误，请重试')
        # 重载页面
        return redirect('show_database_backup')
    else:
        # 返回res
        return res


# 上传备份文件
def upload_backup(request):
    # 获取上传文件
    file = request.FILES.get('upload_file')
    # 调用上传备份方法
    res = DatabaseBackup.upload_backup(request, file)
    # 根据返回值判断上传是否成功
    if res is True:
        # 写入上传成功提示
        messages.success(request, '上传成功')
        # 记录日志
        action = '上传{}备份文件'.format(file.name)
        add_log(request, action, '成功')
    else:
        pass
    # 重载页面
    return redirect('show_database_backup')


# 修改自动备份间隔和接收邮箱方法
def change_days_to_auto_backup(request):
    # 从前端获取时间间隔和邮箱
    days = check_data_format(request.POST.get('days'), 'int')
    email = request.POST.get('email')
    try:
        # 更新数据库
        data = SystemConfig.objects.first()
        data.days_to_auto_backup = days
        data.backup_to_email = email
        data.save()
        # 记录日志
        if days <= 0:
            action = '关闭系统自动备份'
        else:
            action = '更改系统自动备份周期为{}天，备份邮箱为{}'.format(days, email)
        add_log(request, action, '成功')
        # 进行一次备份
        DatabaseBackup.auto_backup()
        # 更新任务
        DatabaseBackup.set_auto_backup()
        # 写入成功提示
        messages.success(request, '修改成功')
    except:
        # 记录日志
        if days <= 0:
            action = '尝试关闭系统自动备份'
        else:
            action = '尝试更改系统自动备份周期为{}天，备份邮箱为{}'.format(days, email)
        add_log(request, action, '失败')
        # 写入失败提示
        messages.error(request, '出现错误，请重试')
    # 重载页面
    return redirect('show_database_backup')


# 修改系统登录方式方法
@login_required
@permission_required('performance.manage_user', raise_exception=True)
def change_system_login(request):
    # 获取用户选中的登录方式
    login_ways = request.POST.getlist('login_way', [])
    # 如果啥都没选，返回错误信息
    if not login_ways:
        # 写入不能一个都不选提示
        messages.error(request, '不可以一个都不选')
        # 重定向账户管理页面
        return redirect('user_management')
    # 遍历用户选择方法
    ways = ''
    for way in login_ways:
        ways += '{} '.format(way)
    ways = ways.strip()
    # 取出系统配置表中第一项
    system_config = SystemConfig.objects.first()
    # 如果啥都没取到，新建一个
    # 取到了就更新
    if not system_config:
        SystemConfig.objects.create(
            login_ways=ways,
        )
    else:
        system_config.login_ways = ways
        system_config.save()

    # 记录日志
    action = '将系统登录方式修改为允许{}方式'.format(ways)
    add_log(request, action, '成功')
    # 写入成功提示
    messages.success(request, '修改成功')
    # 重定向账户管理页面
    return redirect('user_management')


# 展示系统开放接口方法
@login_required
@permission_required('performance.manage_open_api', raise_exception=True)
def show_open_api(request):
    if request.method == 'GET':
        # 从数据库中取出所有接口信息
        datas = OpenApi.objects.all()
        api_search = ''
    else:
        api_search = ''
        # 从前端获取action
        action = request.POST.get('action')
        # 判断action
        if action == '接口搜索':
            # 从前端获取筛选字段
            api_search = request.POST.get('api_search')
            # 筛选接口信息
            datas = OpenApi.objects.filter(
                Q(name__contains=api_search) |
                Q(introduction__contains=api_search)
            )
        elif action == '接口修改时间筛选':
            # 获取起止时间
            start_time = str(request.POST.get('start_time')).split('-')
            end_time = str(request.POST.get('end_time')).split('-')
            # 转换日期对象
            start_time = datetime(year=int(start_time[0]), month=int(start_time[1]), day=int(start_time[2]),
                                  hour=int(start_time[3]), minute=int(start_time[4]))
            end_time = datetime(year=int(end_time[0]), month=int(end_time[1]), day=int(end_time[2]),
                                hour=int(end_time[3]), minute=int(end_time[4]))
            # 筛选在起止时间内的接口信息
            datas = OpenApi.objects.filter(change_time__gte=start_time,
                                           change_time__lte=end_time)
        else:
            # 重定向展示系统开放接口页面
            return redirect('show_open_api')
    # 打包信息
    context = {
        'datas': datas,
        'site_url': settings.SITE_URL,
        'api_search': api_search,
    }
    return render(request, '开放接口.html', context=context)


# 增加接口方法
@login_required
@permission_required('performance.manage_open_api', raise_exception=True)
def add_api(request):
    # 从前端获取新增接口信息
    name = request.POST.get('name')
    password = request.POST.get('password')
    introduction = request.POST.get('introduction')
    is_enabled = request.POST.get('is_enabled')
    opened_data_list = request.POST.getlist('opened_data', [])

    # 检查此名字的接口是否已存在
    # 如果已存在返回此名字接口已存在错误
    if OpenApi.objects.filter(name=name).exists():
        messages.error(request, '此名字接口已存在')
        return redirect('show_open_api')
    # 转换is_enabled
    if is_enabled is None:
        is_enabled = False
    else:
        is_enabled = True
    # 转换opened_data_list
    opened_data = ''
    for data in opened_data_list:
        opened_data += '{} '.format(data)
    opened_data = opened_data.strip()

    try:
        # 存入数据库
        OpenApi.objects.create(
            name=name,
            password=password,
            introduction=introduction,
            opened_data=opened_data,
            is_enabled=is_enabled,
            change_time=datetime.now(),
        )
    except:
        # 写入失败提示
        messages.error(request, '保存出错，请重试')
        # 记录日志
        action = '尝试增加名为{}的开放接口'.format(name)
        add_log(request, action, '失败')
        # 重载页面
        return redirect('show_open_api')
    # 写入成功提示
    messages.success(request, '增加成功')
    # 记录日志
    action = '增加了名为{}的开放接口'.format(name)
    add_log(request, action, '成功')
    # 重载页面
    return redirect('show_open_api')


# 删除接口方法
@login_required
@permission_required('performance.manage_open_api', raise_exception=True)
def delete_api(request):
    # 从前端获取要删除的id
    delete_id = check_data_format(request.POST.get('delete_id'), 'int')
    # 取出要删除的接口
    data = OpenApi.objects.get(id=delete_id)
    # 记录日志要用的名字
    name = data.name
    # 删除接口
    data.delete()
    # 写入成功提示
    messages.success(request, '成功删除{}接口'.format(name))
    # 记录日志
    action = '删除了名为{}的开放接口'.format(name)
    add_log(request, action, '成功')
    # 重载页面
    return redirect('show_open_api')


# 修改接口方法
@login_required
@permission_required('performance.manage_open_api', raise_exception=True)
def change_api(request):
    # 从前端获取修改信息
    change_id = request.POST.get('change_id')
    name = request.POST.get('name')
    password = request.POST.get('password')
    introduction = request.POST.get('introduction')
    is_enabled = request.POST.get('is_enabled')
    opened_data_list = request.POST.getlist('opened_data', [])
    # 转换is_enabled
    if is_enabled is None:
        is_enabled = False
    else:
        is_enabled = True
    # 转换opened_data_list
    opened_data = ''
    for data in opened_data_list:
        opened_data += '{} '.format(data)
    opened_data = opened_data.strip()
    # 取出要修改的接口
    data = OpenApi.objects.get(id=change_id)
    # 更新数据
    data.name = name
    data.password = password
    data.introduction = introduction
    data.is_enabled = is_enabled
    data.opened_data = opened_data
    data.save()
    # 写入成功提示
    messages.success(request, '修改成功')
    # 记录日志
    action = '修改了名为{}的接口信息'.format(name)
    add_log(request, action, '成功')
    # 重载页面
    return redirect('show_open_api')


# 从开放接口提供数据方法
def get_api_data(request, api_name):
    # 从前端获取密码
    password = request.GET.get('password')
    # 从数据库中查询此name的接口
    api = get_object_or_404(OpenApi, name=api_name)
    # 验证此接口是否启用
    if not api.is_enabled:
        return HttpResponse('403错误，此接口已禁用')
    # 验证密码
    if api.password != password:
        return HttpResponse('403错误，密码错误无权限')
    #将数据表名字及相应数据项建立一个字典映射关系
    name_data_dict = {
        'monthly_sales_data':[],
        'quarterly_sales_data':[],
        'internal_control_indicators':[],
        'monthly_performance':[],
        'quarterly_performance':[],
        'quarterly_award':[],
    }
    for temp in api.opened_data.split(' '):
        temp_name, temp_data = temp.split('.')
        name_data_dict[temp_name].append(temp_data)
    # 取出相应数据
    api_data = {}  # 存放最终的数据
    # 月度营业数据
    if name_data_dict['monthly_sales_data']:
        api_data['monthly_sales_data'] = {}
        for data_name in name_data_dict['monthly_sales_data']:
            api_data['monthly_sales_data'][data_name] = list(MonthlySalesData.objects.values_list(data_name, flat=True))
    # 季度营业数据
    if name_data_dict['quarterly_sales_data']:
        api_data['quarterly_sales_data'] = {}
        for data_name in name_data_dict['quarterly_sales_data']:
            api_data['quarterly_sales_data'][data_name] = list(QuarterlySalesData.objects.values_list(data_name, flat=True))
    # 内控指标汇总
    if name_data_dict['internal_control_indicators']:
        api_data['internal_control_indicators'] = {}
        for data_name in name_data_dict['internal_control_indicators']:
            api_data['internal_control_indicators'][data_name] = list(InternalControlIndicators.objects.values_list(data_name, flat=True))
    # 月度绩效考核结果
    if name_data_dict['monthly_performance']:
        api_data['monthly_performance'] = {}
        for data_name in name_data_dict['monthly_performance']:
            api_data['monthly_performance'][data_name] = list(MonthlyPerformance.objects.values_list(data_name, flat=True))
    # 季度绩效考核结果
    if name_data_dict['quarterly_performance']:
        api_data['quarterly_performance'] = {}
        for data_name in name_data_dict['quarterly_performance']:
            api_data['quarterly_performance'][data_name] = list(QuarterlyPerformance.objects.values_list(data_name, flat=True))
    # 季度绩效奖金
    if name_data_dict['quarterly_award']:
        api_data['quarterly_award'] = {}
        for data_name in name_data_dict['quarterly_award']:
            api_data['quarterly_award'][data_name] = list(QuarterlyAward.objects.values_list(data_name, flat=True))
    
    # 接口调用次数加一
    api.called_times += 1
    api.save()
    
    return JsonResponse(api_data)
