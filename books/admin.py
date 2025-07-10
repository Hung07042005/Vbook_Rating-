from django.contrib import admin
from .models import Author, Book, Review, WantToRead, Genre

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'icon', 'color', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    list_filter = ['color', 'created_at']

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'nationality', 'birth_date', 'created_at']
    search_fields = ['name', 'nationality', 'bio']
    ordering = ['name']
    list_filter = ['nationality', 'birth_date', 'created_at']
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'image', 'nationality', 'birth_date')
        }),
        ('Tiểu sử', {
            'fields': ('bio',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'rating', 'created_at', 'published_date', 'price']
    list_filter = ['author', 'genre', 'rating', 'created_at']
    search_fields = ['title', 'content', 'author__name', 'genre__name']
    ordering = ['-created_at']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['book', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['book__title', 'user__username', 'comment']
    ordering = ['-created_at']

@admin.register(WantToRead)
class WantToReadAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'book__title']
    ordering = ['-added_at']
    date_hierarchy = 'added_at'