from django.contrib import admin
from django.urls import path, include
from books import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('book/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('admin/', admin.site.urls),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    path('accounts/', include('django.contrib.auth.urls')),  # Thêm URL cho authentication
    path('accounts/register/', views.register, name='register'),  # URL cho đăng ký
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
    path('review/<int:review_id>/like/', views.like_review, name='like_review'),
    path('review/<int:review_id>/reply/', views.reply_review, name='reply_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('reply/<int:reply_id>/delete/', views.delete_reply, name='delete_reply'),

    # Want to Read URLs
    path('book/<int:book_id>/add-to-want-to-read/', views.add_to_want_to_read, name='add_to_want_to_read'),
    path('book/<int:book_id>/remove-from-want-to-read/', views.remove_from_want_to_read, name='remove_from_want_to_read'),
    path('my-books/', views.my_books, name='my_books'),
    path('about/', views.about, name='about'),
    # Browse URLs
    path('authors/', views.author_list, name='author_list'),
    path('genres/', views.genres, name='genres'),
    path('genre/<int:genre_id>/', views.genre_detail, name='genre_detail'),
    path('popular/', views.popular_books, name='popular_books'),
    path('new/', views.new_books, name='new_books'),
    path('notifications/', views.notifications, name='notifications'),
    path('search-statistics/', views.search_statistics, name='search_statistics'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)