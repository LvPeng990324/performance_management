# 日志相关方法
from ..models import Logs


# 增加日志
def add_log(request, action, result):
    user_name = request.user.last_name
    job_number = request.user.extension.job_number
    # 记录到数据库
    Logs.objects.create(
        user_name=user_name,
        job_number=job_number,
        action=action,
        result=result,
    )

