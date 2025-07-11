from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Review, Author, WantToRead, Genre, SearchLog
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg, F
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from datetime import datetime, timedelta
from django.views.decorators.http import require_POST
from .models import Review, ReviewLike
import json
from .models import Review, Reply
from django.contrib.auth.models import User
from .models import Notification
from datetime import datetime
from .views_search_stat import search_statistics
from django.contrib.auth.decorators import user_passes_test
from django.core import serializers
import unicodedata
import re
from django.contrib.admin.views.decorators import staff_member_required
from django import forms

def index(request):
    books = Book.objects.all().order_by('-created_at')
    authors = Author.objects.none()
    genres = Genre.objects.none()
    query = request.GET.get('q')
    result_count = 0
    if query:
        books_qs = books.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query) |
            Q(content__icontains=query) |
            Q(genre__name__icontains=query)
        ).distinct()
        authors_qs = Author.objects.filter(
            Q(name__icontains=query) |
            Q(bio__icontains=query) |
            Q(nationality__icontains=query)
        ).distinct()
        genres_qs = Genre.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
        result_count = books_qs.count() + authors_qs.count() + genres_qs.count()
        # Ghi log tìm kiếm với số lượng kết quả
        if request.user.is_authenticated:
            SearchLog.objects.create(user=request.user, query=query, result_count=result_count)
        else:
            SearchLog.objects.create(user=None, query=query, result_count=result_count)
        books = books_qs
        authors = authors_qs
        genres = genres_qs
    
    # Kiểm tra xem user đã đăng nhập và đã thêm sách nào vào want to read chưa
    if request.user.is_authenticated:
        want_to_read_books = WantToRead.objects.filter(user=request.user).values_list('book_id', flat=True)
        for book in books:
            book.is_in_want_to_read = book.id in want_to_read_books
    else:
        for book in books:
            book.is_in_want_to_read = False
    
    # Lấy tác giả nổi bật (có nhiều sách nhất và rating cao)
    featured_authors = Author.objects.annotate(
        book_count=Count('books'),
        avg_rating=Avg('books__rating')
    ).filter(
        book_count__gte=1
    ).order_by('-book_count', '-avg_rating')[:6]
    
    # Lấy thể loại nổi bật (có nhiều sách nhất)
    featured_genres = Genre.objects.annotate(
        book_count=Count('books')
    ).filter(
        book_count__gte=1
    ).order_by('-book_count')[:8]
    
    context = {
        'books': books,
        'authors': authors,
        'genres': genres,
        'query': query,
        'featured_authors': featured_authors,
        'featured_genres': featured_genres
    }
    
    return render(request, 'books/index.html', context)

@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    
    # Kiểm tra xem user đã thêm sách này vào want to read chưa
    book.is_in_want_to_read = WantToRead.objects.filter(user=request.user, book=book).exists()
    
    if request.method == 'POST':
        if 'comment' in request.POST:
            comment = request.POST['comment']
            try:
                rating = float(request.POST.get('rating', 0.0))
            except ValueError:
                rating = 0.0
            review = Review(book=book, user=request.user, comment=comment, rating=rating)
            review.save()
            return redirect('book_detail', book_id=book.id)
        elif 'title' in request.POST:
            book.title = request.POST['title']
            book.content = request.POST['content']
            try:
                book.rating = float(request.POST.get('rating', 0.0))
            except ValueError:
                book.rating = 0.0
            if request.FILES.get('image'):
                book.image = request.FILES['image']
            book.save()
            return redirect('book_detail', book_id=book.id)
    
    return render(request, 'books/book_detail.html', {'book': book})

@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        book.title = request.POST['title']
        book.content = request.POST['content']
        try:
            book.rating = float(request.POST.get('rating', 0.0))
        except ValueError:
            book.rating = 0.0

        # Thêm xử lý giá sách
        try:
            book.price = float(request.POST.get('price', 0.0))
        except ValueError:
            book.price = 0.0

        # Thêm xử lý ngày xuất bản
        published_date_str = request.POST.get('published_date')
        if published_date_str:
            try:
                book.published_date = datetime.strptime(published_date_str, '%Y-%m-%d').date()
            except ValueError:
                book.published_date = None

        # Xử lý ảnh
        if request.FILES.get('image'):
            book.image = request.FILES['image']

        book.save()
        return redirect('book_detail', book_id=book.id)
    
    return render(request, 'books/book_detail.html', {'book': book, 'edit_mode': True})
def author_detail(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    books = author.books.all()
    # Lấy danh sách thể loại duy nhất
    genres = Genre.objects.filter(books__author=author).distinct()
    # Tính điểm trung bình các sách của tác giả (chỉ tính sách có review)
    ratings = [book.rating for book in books if book.reviews.count() > 0]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else None
    # Kiểm tra want to read cho mỗi sách
    if request.user.is_authenticated:
        want_to_read_books = WantToRead.objects.filter(user=request.user).values_list('book_id', flat=True)
        for book in books:
            book.is_in_want_to_read = book.id in want_to_read_books
    else:
        for book in books:
            book.is_in_want_to_read = False
    return render(request, 'books/author_detail.html', {'author': author, 'books': books, 'genres': genres, 'avg_rating': avg_rating})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to BookRating.')
            return redirect('index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'books/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')

def home(request):
    return render(request, 'home.html')

def book_list(request):
    return render(request, 'book_list.html')

def author_list(request):
    # Lấy danh sách tất cả tác giả với số lượng sách
    authors = Author.objects.annotate(book_count=Count('books')).order_by('-book_count')
    
    # Thêm thông tin về rating trung bình của tác giả
    for author in authors:
        author.avg_rating = author.books.aggregate(Avg('rating'))['rating__avg'] or 0.0
        author.avg_rating = round(author.avg_rating, 1)
    
    return render(request, 'books/author_list.html', {'authors': authors})

def genres(request):
    # Lấy danh sách thể loại từ database
    genres_list = Genre.objects.annotate(book_count=Count('books')).order_by('-book_count')
    
    return render(request, 'books/genres.html', {'genres': genres_list})

def genre_detail(request, genre_id):
    genre = get_object_or_404(Genre, pk=genre_id)
    books = genre.books.all()
    
    # Kiểm tra want to read cho mỗi sách
    if request.user.is_authenticated:
        want_to_read_books = WantToRead.objects.filter(user=request.user).values_list('book_id', flat=True)
        for book in books:
            book.is_in_want_to_read = book.id in want_to_read_books
    else:
        for book in books:
            book.is_in_want_to_read = False
    
    return render(request, 'books/genre_detail.html', {'genre': genre, 'books': books})

def popular_books(request):
    # Lấy sách phổ biến dựa trên rating và số lượng review
    popular_books = Book.objects.annotate(
        review_count=Count('reviews')
    ).filter(
        rating__gte=3.0,
        review_count__gte=1
    ).order_by('-rating', '-review_count')[:12]
    
    # Kiểm tra want to read cho mỗi sách
    if request.user.is_authenticated:
        want_to_read_books = WantToRead.objects.filter(user=request.user).values_list('book_id', flat=True)
        for book in popular_books:
            book.is_in_want_to_read = book.id in want_to_read_books
    else:
        for book in popular_books:
            book.is_in_want_to_read = False
    
    return render(request, 'books/popular.html', {'books': popular_books})

def new_books(request):
    # Lấy sách mới (thêm trong 30 ngày gần đây)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    new_books = Book.objects.filter(created_at__gte=thirty_days_ago).order_by('-created_at')
    
    # Kiểm tra want to read cho mỗi sách
    if request.user.is_authenticated:
        want_to_read_books = WantToRead.objects.filter(user=request.user).values_list('book_id', flat=True)
        for book in new_books:
            book.is_in_want_to_read = book.id in want_to_read_books
    else:
        for book in new_books:
            book.is_in_want_to_read = False
    
    return render(request, 'books/new_books.html', {'books': new_books})

def about(request):
    return render(request, 'books/about.html')

@login_required
def add_to_want_to_read(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Book, pk=book_id)
        want_to_read, created = WantToRead.objects.get_or_create(user=request.user, book=book)
        
        if created:
            messages.success(request, f'"{book.title}" đã được thêm vào danh sách Muốn đọc của bạn!')
        else:
            messages.info(request, f'"{book.title}" đã có trong danh sách Muốn đọc của bạn!')
        # Nếu request là AJAX, trả về JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'"{book.title}" đã được thêm vào danh sách Muốn đọc của bạn!' if created else f'"{book.title}" đã có trong danh sách Muốn đọc của bạn!',
                'is_in_list': True
            })
        
        return redirect('index')
    
    return redirect('index')

@login_required
def remove_from_want_to_read(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Book, pk=book_id)
        try:
            want_to_read = WantToRead.objects.get(user=request.user, book=book)
            want_to_read.delete()
            messages.success(request, f'"{book.title}" đã được xóa khỏi danh sách Muốn đọc của bạn!')
            # Nếu request là AJAX, trả về JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'"{book.title}" đã được xóa khỏi danh sách Muốn đọc của bạn!',
                    'is_in_list': False
                })
        except WantToRead.DoesNotExist:
            messages.error(request, f'"{book.title}" was not in your Want to Read list!')
        
        return redirect('index')
    
    return redirect('index')

@login_required
def my_books(request):
    want_to_read_books = WantToRead.objects.filter(user=request.user).select_related('book', 'book__author').order_by('-added_at')
    return render(request, 'books/my_books.html', {'want_to_read_books': want_to_read_books})

@login_required
@require_POST
def like_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    user = request.user

    # Toggle like
    from books.models import ReviewLike  # Ensure import at the top if not already

    like = ReviewLike.objects.filter(review=review, user=user).first()
    if like:
        like.delete()
        liked = False
    else:
        ReviewLike.objects.create(review=review, user=user)
        liked = True
        liked = True

    # Cập nhật lại số like cho review
    review.like_count = review.likes.count()
    review.save(update_fields=['like_count'])

    # Trả về JSON nếu là AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'like_count': review.like_count,
            'liked': liked
        })

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@require_POST
def reply_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    reply_text = request.POST.get('reply')
    if not reply_text:
        return JsonResponse({'success': False, 'error': 'Reply cannot be empty.'}, status=400)
    reply = Reply.objects.create(
        review=review,
        user=request.user,
        content=reply_text
    )
    # Tạo notification cho chủ review (nếu không phải tự trả lời mình)
    if review.user != request.user:
        Notification.objects.create(
            user=review.user,
            message=f"{request.user.username} đã bình luận vào đánh giá của bạn.",
            url=f"/book/{review.book.id}/#review-{review.id}"
        )
    # Trả về JSON nếu là AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'reply': {
                'id': reply.id,
                'user': reply.user.username if reply.user else 'Anonymous',
                'content': reply.content,
                'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def notifications(request):
    notifications = request.user.notifications.order_by('-created_at')
    notifications.update(is_read=True)  # Đánh dấu đã đọc khi vào trang
    return render(request, 'books/notifications.html', {'notifications': notifications})
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if review.user != request.user:
     return HttpResponseForbidden("Bạn không có quyền xóa bình luận này.")
    book_id = review.book.id
    review.delete()
    return redirect('book_detail', book_id=book_id)
@login_required
@require_POST
def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)
    if reply.user != request.user:
        return HttpResponseForbidden("Bạn không có quyền xóa phản hồi này.")
    
    review_id = reply.review.id
    reply.delete()
    
    return redirect('book_detail', book_id=reply.review.book.id)

def search_books(request):
    tu_khoa_tim_kiem = request.GET.get('q', '')
    ket_qua_sach = Book.objects.filter(
        Q(title__icontains=tu_khoa_tim_kiem) |
        Q(author__name__icontains=tu_khoa_tim_kiem) |
        Q(content__icontains=tu_khoa_tim_kiem) |
        Q(genre__name__icontains=tu_khoa_tim_kiem)
    ).distinct()

    # Lưu lịch sử tìm kiếm
    if request.user.is_authenticated:
        SearchLog.objects.create(user=request.user, query=tu_khoa_tim_kiem)
    else:
        SearchLog.objects.create(user=None, query=tu_khoa_tim_kiem)

    return render(request, 'books/search_results.html', {
        'books': ket_qua_sach,
        'query': tu_khoa_tim_kiem
    })

def normalize_query(q):
    if not q:
        return ''
    q = q.lower().strip()
    q = unicodedata.normalize('NFD', q)
    q = ''.join([c for c in q if unicodedata.category(c) != 'Mn'])  # remove accents
    q = re.sub(r'\s+', ' ', q)  # remove extra spaces
    return q

def is_search_statistician(user):
    return user.is_superuser or user.groups.filter(name='Thống kê tìm kiếm').exists()

@user_passes_test(is_search_statistician)
def search_statistics(request):
    logs = SearchLog.objects.select_related('user').order_by('-searched_at')[:100]
    # Gom nhóm từ khóa tương đương
    all_logs = SearchLog.objects.exclude(query='').exclude(query__isnull=True)
    keyword_counter = {}
    no_result_counter = {}
    for log in all_logs:
        norm = normalize_query(log.query)
        if not norm:
            continue
        # Đếm tổng số lần tìm kiếm
        if norm not in keyword_counter:
            keyword_counter[norm] = {'query': log.query, 'count': 0}
        keyword_counter[norm]['count'] += 1
        # Kiểm tra có phải là từ khóa không có kết quả không
        book_count = Book.objects.filter(
            Q(title__icontains=log.query) |
            Q(author__name__icontains=log.query) |
            Q(content__icontains=log.query) |
            Q(genre__name__icontains=log.query)
        ).count()
        author_count = Author.objects.filter(
            Q(name__icontains=log.query) |
            Q(bio__icontains=log.query) |
            Q(nationality__icontains=log.query)
        ).count()
        genre_count = Genre.objects.filter(
            Q(name__icontains=log.query) |
            Q(description__icontains=log.query)
        ).count()
        if book_count == 0 and author_count == 0 and genre_count == 0:
            if norm not in no_result_counter:
                no_result_counter[norm] = {'query': log.query, 'count': 0}
            no_result_counter[norm]['count'] += 1
    # Lấy 10 từ khóa nhiều nhất
    top_keywords = sorted(keyword_counter.values(), key=lambda x: -x['count'])[:10]
    # Lấy 10 từ khóa không có kết quả nhiều nhất
    no_result_keywords = sorted(no_result_counter.values(), key=lambda x: -x['count'])[:10]
    # Tác giả được xem nhiều nhất (dựa trên số sách của tác giả được thêm vào WantToRead)
    top_authors_qs = (Author.objects.annotate(
        view_count=Count('books__want_to_read_users', distinct=True)
    ).order_by('-view_count')[:10])
    top_authors = list(top_authors_qs.values('name', 'view_count'))
    # Sách được xem nhiều nhất (dựa trên số user thêm vào WantToRead)
    top_books = (Book.objects.annotate(
        view_count=Count('want_to_read_users', distinct=True)
    ).order_by('-view_count')[:10])
    # Thể loại được tìm nhiều nhất (dựa trên số sách thuộc thể loại được thêm vào WantToRead)
    top_genres = (Genre.objects.annotate(
        search_count=Count('books__want_to_read_users', distinct=True)
    ).order_by('-search_count')[:10])
    return render(request, 'books/search_statistics.html', {
        'logs': logs,
        'top_keywords': top_keywords,
        'no_result_keywords': no_result_keywords,
        'top_authors': top_authors,
        'top_books': top_books,
        'top_genres': top_genres,
    })

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'bio', 'nationality', 'info', 'tieu_su', 'image', 'birth_year', 'home_town']

@staff_member_required
def admin_author_list(request):
    authors = Author.objects.all().order_by('-id')
    return render(request, 'books/admin_author_list.html', {'authors': authors})

@staff_member_required
def admin_author_add(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tác giả đã được thêm thành công!')
            return redirect('admin_author_list')
    else:
        form = AuthorForm()
    return render(request, 'books/admin_author_form.html', {'form': form, 'action': 'add'})

@staff_member_required
def admin_author_edit(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    if request.method == 'POST':
        form = AuthorForm(request.POST, request.FILES, instance=author)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tác giả đã được cập nhật!')
            return redirect('admin_author_list')
    else:
        form = AuthorForm(instance=author)
    return render(request, 'books/admin_author_form.html', {'form': form, 'action': 'edit', 'author': author})

@staff_member_required
def admin_author_delete(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    if request.method == 'POST':
        author.delete()
        messages.success(request, 'Tác giả đã được xóa!')
        return redirect('admin_author_list')
    return render(request, 'books/admin_author_confirm_delete.html', {'author': author})