from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('authors/', views.author_list, name='author_list'),
    path('about/', views.about, name='about'),
    path('review/<int:review_id>/reply/', views.reply_review, name='reply_review'),
    path('notifications/', views.notifications, name='notifications'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('reply/<int:reply_id>/delete/', views.delete_reply, name='delete_reply'),
    path('search-statistics/', views.search_statistics, name='search_statistics'),

]