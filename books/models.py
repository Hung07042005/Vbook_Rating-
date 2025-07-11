from django.db import models
from django.contrib.auth.models import User

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-book')  # FontAwesome icon class
    color = models.CharField(max_length=20, default='primary')  # Bootstrap color class
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Author(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='author_images/', null=True, blank=True)
    bio = models.TextField(blank=True, help_text="Tiểu sử ngắn")
    tieu_su = models.TextField(blank=True, help_text="Tiểu sử chi tiết")
    birth_date = models.DateField(null=True, blank=True)
    birth_year = models.PositiveIntegerField(null=True, blank=True, verbose_name='Năm sinh')
    nationality = models.CharField(max_length=100, blank=True)
    home_town = models.CharField(max_length=255, null=True, blank=True, verbose_name='Quê quán')
    info = models.TextField(blank=True, help_text="Thông tin chi tiết về tác giả")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.FloatField(default=0.0)  # Rating trung bình từ các review
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    published_date = models.DateField(null=True, blank=True)
    external_url = models.URLField(max_length=500, blank=True, null=True, help_text="Link đọc truyện online")
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Giá tham khảo (VNĐ)")
    publish_year = models.PositiveIntegerField(null=True, blank=True, help_text="Năm xuất bản")


    def update_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            avg_rating = sum(review.rating for review in reviews) / reviews.count()
            self.rating = round(avg_rating, 1)
        else:
            self.rating = 0.0
        self.save()

    def __str__(self):
        return self.title

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.TextField()
    rating = models.FloatField(default=0)  # Đánh giá cá nhân từ 0 đến 5
    created_at = models.DateTimeField(auto_now_add=True)
    like_count = models.PositiveIntegerField(default=0)      # Thêm trường like

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if hasattr(self.book, "update_rating"):
            self.book.update_rating()

    def __str__(self):
        return f"Review by {self.user.username if self.user else 'Anonymous'} for {self.book.title}"

class WantToRead(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='want_to_read')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='want_to_read_users')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'book']  # Mỗi user chỉ có thể thêm một cuốn sách một lần

    def __str__(self):
        return f"{self.user.username} wants to read {self.book.title}"

class Reply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.user.username if self.user else 'Anonymous'}"
    
class ReviewLike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['review', 'user']  # Mỗi user chỉ like 1 review 1 lần

    def __str__(self):
        user_str = self.user.username if hasattr(self.user, "username") else str(self.user)
        review_id = self.review.id if hasattr(self.review, "id") else str(self.review)
        return f"{user_str} liked review {review_id}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

class SearchLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    query = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)
    result_count = models.IntegerField(default=0)  # Số lượng kết quả trả về khi tìm kiếm

    def __str__(self):
        return f"{self.user} - {self.query} ({self.searched_at})"
