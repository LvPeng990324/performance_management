from django.contrib import admin
from .models import MonthlyPerformance
from .models import MonthlySalesData
from .models import QuarterlyPerformance
from .models import InternalControlIndicators
from .models import QuarterlySalesData


@admin.register(MonthlyPerformance)
class MonthlyPerformanceInformation(admin.ModelAdmin):
    pass


@admin.register(MonthlySalesData)
class MonthlySalesDataInformation(admin.ModelAdmin):
    pass


@admin.register(QuarterlyPerformance)
class QuarterlyPerformanceInformation(admin.ModelAdmin):
    pass


@admin.register(InternalControlIndicators)
class InternalControlIndicatorsInformation(admin.ModelAdmin):
    pass


@admin.register(QuarterlySalesData)
class QuarterlySalesDataInformation(admin.ModelAdmin):
    pass



