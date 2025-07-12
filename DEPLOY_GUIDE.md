# Hướng dẫn Deploy Django App lên Render

## Bước 1: Chuẩn bị Repository

1. Đảm bảo code đã được push lên GitHub/GitLab
2. Kiểm tra các file đã được cấu hình:
   - `render.yaml` - Cấu hình deployment
   - `requirements.txt` - Dependencies
   - `build.sh` - Script build
   - `bookrating_project/settings.py` - Settings đã được cập nhật

## Bước 2: Tạo tài khoản Render

1. Truy cập [render.com](https://render.com)
2. Đăng ký tài khoản mới hoặc đăng nhập
3. Kết nối với GitHub/GitLab account

## Bước 3: Deploy ứng dụng

### Cách 1: Sử dụng Blueprint (Khuyến nghị)

1. Trên dashboard Render, click "New +"
2. Chọn "Blueprint"
3. Kết nối repository GitHub/GitLab
4. Chọn repository chứa code Django
5. Render sẽ tự động detect `render.yaml` và deploy

### Cách 2: Deploy thủ công

1. Trên dashboard Render, click "New +"
2. Chọn "Web Service"
3. Kết nối repository
4. Cấu hình:
   - **Name**: vbook-rating
   - **Environment**: Python
   - **Build Command**: `chmod a+x build.sh && ./build.sh`
   - **Start Command**: `gunicorn bookrating_project.wsgi:application`
   - **Plan**: Free (hoặc chọn plan phù hợp)

## Bước 4: Cấu hình Environment Variables

Trong service settings, thêm các environment variables:

- `DJANGO_SETTINGS_MODULE`: `bookrating_project.settings`
- `DEBUG`: `False`
- `SECRET_KEY`: (Render sẽ tự động generate)

## Bước 5: Cấu hình Database (Tùy chọn)

Nếu muốn sử dụng PostgreSQL:

1. Tạo PostgreSQL database trên Render
2. Copy connection string
3. Thêm environment variable `DATABASE_URL` với connection string

## Bước 6: Kiểm tra Deployment

1. Sau khi deploy thành công, truy cập URL được cung cấp
2. Kiểm tra các chức năng:
   - Trang chủ
   - Đăng ký/Đăng nhập
   - Xem sách
   - Upload ảnh

## Troubleshooting

### Lỗi thường gặp:

1. **Static files không load**:
   - Kiểm tra `STATIC_ROOT` và `STATICFILES_STORAGE`
   - Đảm bảo `python manage.py collectstatic` chạy thành công

2. **Database errors**:
   - Kiểm tra migrations: `python manage.py migrate`
   - Kiểm tra database connection

3. **Import errors**:
   - Kiểm tra `requirements.txt` có đầy đủ dependencies
   - Kiểm tra Python version compatibility

### Logs:

- Xem logs trong Render dashboard
- Kiểm tra build logs và runtime logs
- Debug bằng cách set `DEBUG=True` tạm thời

## Cấu trúc file quan trọng:

```
├── render.yaml          # Cấu hình deployment
├── requirements.txt     # Python dependencies
├── build.sh           # Build script
├── manage.py          # Django management
├── bookrating_project/
│   ├── settings.py    # Django settings
│   ├── urls.py        # URL configuration
│   └── wsgi.py        # WSGI application
└── books/             # Django app
    ├── models.py
    ├── views.py
    └── urls.py
```

## Lưu ý quan trọng:

1. **Security**: Không commit SECRET_KEY vào repository
2. **Static files**: Sử dụng WhiteNoise để serve static files
3. **Database**: SQLite cho development, PostgreSQL cho production
4. **Media files**: Cân nhắc sử dụng cloud storage (AWS S3, Cloudinary)
5. **Environment**: Luôn set DEBUG=False trong production

## Cập nhật ứng dụng:

1. Push code mới lên repository
2. Render sẽ tự động detect và redeploy
3. Hoặc manual trigger redeploy từ dashboard 