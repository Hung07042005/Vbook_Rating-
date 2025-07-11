from django.urls import path
from . import views

urlpatterns = [
    # ...existing code...
    path('books/', views.book_list, name='book_list'),
    path('authors/', views.author_list, name='author_list'),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    path('about/', views.about, name='about'),
    path('review/<int:review_id>/reply/', views.reply_review, name='reply_review'),
    path('notifications/', views.notifications, name='notifications'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('reply/<int:reply_id>/delete/', views.delete_reply, name='delete_reply'),
    path('search-statistics/', views.search_statistics, name='search_statistics'),
    path('admin/authors/', views.admin_author_list, name='admin_author_list'),
    path('admin/authors/add/', views.admin_author_add, name='admin_author_add'),
    path('admin/authors/edit/<int:author_id>/', views.admin_author_edit, name='admin_author_edit'),
    path('admin/authors/delete/<int:author_id>/', views.admin_author_delete, name='admin_author_delete'),
    path('genre/<int:genre_id>/', views.genre_detail, name='genre_detail'),
]