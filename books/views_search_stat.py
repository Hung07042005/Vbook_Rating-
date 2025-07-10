from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from .models import SearchLog

def is_search_statistician(user):
    return user.groups.filter(name='Thống kê tìm kiếm').exists() or user.is_superuser

@user_passes_test(is_search_statistician)
def search_statistics(request):
    logs = SearchLog.objects.select_related('user').order_by('-searched_at')[:100]
    return render(request, 'books/search_statistics.html', {'logs': logs})
