
Web Bán Hàng (webbanhang2)
Đồ án Quản Lý Dự Án (QLDA) — Nhóm G8 (CyberBug)

Ứng dụng web bán hàng mẫu được xây dựng bằng Django. Dự án tích hợp nhiều tính năng thực tế: quản lý sản phẩm, giỏ hàng, thanh toán đơn giản, tài khoản người dùng, giao diện admin, và một chatbot tích hợp với nhiều dịch vụ (OpenAI, HuggingFace, Deepseek, Dialogflow) để hỗ trợ người dùng.

## Tính năng chính

- Trang chủ, danh mục, trang chi tiết sản phẩm
- Giỏ hàng, thanh toán (mô phỏng), lịch sử đơn hàng
- Quản trị: quản lý sản phẩm, đơn hàng, khách hàng, đánh giá
- Hệ thống đánh giá, hình ảnh sản phẩm
- Chatbot tích hợp: các biến thể và adapter để gọi API OpenAI, HuggingFace, Deepseek, Dialogflow

## Kiến trúc & Công nghệ

- Backend: Django
- Database: SQLite (tập tin `db.sqlite3` trong repo, phù hợp môi trường phát triển)
- Frontend: HTML/CSS/JS thuần (thư mục `app/static` và `app/templates`)
- Thư viện/SDK tích hợp API: các module trong `app/` như `openai_api.py`, `huggingface_api.py`, `deepseek_api.py`, `dialogflow_chatbot.py`.

## Cấu trúc thư mục chính

- `manage.py` — entrypoint Django
- `webbanhang/` — cấu hình Django (settings, urls, wsgi, asgi)
- `app/` — ứng dụng chính chứa models, views, static, templates, và các module chatbot
- `credentials/` — chứa file credential cho Dialogflow/Google (ví dụ: `djangochatbot-459709-57f95d12af87.json`)
- `db.sqlite3` — database SQLite (dùng cho dev)
- `requirements.txt` — danh sách phụ thuộc Python

## Yêu cầu

- Python 3.8+ (khuyến nghị 3.9/3.10)
- virtualenv hoặc venv

## Hướng dẫn cài đặt (phát triển)

1. Tạo môi trường ảo và kích hoạt (Windows PowerShell):

	python -m venv .venv
	.\.venv\Scripts\Activate.ps1

2. Cài đặt phụ thuộc:

	pip install -r requirements.txt

3. Cấu hình biến môi trường (tùy cần):

	- `DJANGO_SECRET_KEY` (tùy chọn, nếu muốn override)
	- API keys: `OPENAI_API_KEY`, `HUGGINGFACE_API_KEY`, `DEEPSEEK_API_KEY`, ...
	- Nếu dùng Dialogflow/Google service account, đặt `GOOGLE_APPLICATION_CREDENTIALS` trỏ tới file JSON trong thư mục `credentials/`:

	  (PowerShell) $env:GOOGLE_APPLICATION_CREDENTIALS = "<đường_dẫn_absolute>\\credentials\\djangochatbot-459709-57f95d12af87.json"

4. Áp migration và tạo superuser:

	python manage.py migrate
	python manage.py createsuperuser

5. Chạy server phát triển:

	python manage.py runserver

Truy cập: http://127.0.0.1:8000/

## Cấu hình chatbot & API

Các adapter và ví dụ demo nằm trong `app/`:

- `openai_api.py` — wrapper gọi OpenAI
- `huggingface_api.py` / `huggingface_api_demo.py` — gọi model HuggingFace
- `deepseek_api.py` & `smart_chatbot_deepseek.py` — tích hợp dịch vụ Deepseek
- `dialogflow_chatbot.py` — tích hợp Dialogflow

Để chatbot hoạt động, cần cung cấp khóa API tương ứng (ví dụ `OPENAI_API_KEY`) hoặc cấu hình service account cho Dialogflow. Kiểm tra các file tương ứng để biết biến môi trường/đường dẫn cần đặt.

## Chạy test

- Repo có một số file test (ví dụ `test_chatbot_api.py`, `test_deepseek_direct.py`). Bạn có thể chạy:

  python manage.py test

Hoặc nếu bạn dùng pytest (cài đặt thêm `pytest`):

  pytest -q

## Ghi chú bảo mật

- Không commit API keys hoặc credentials vào Git. Trong repo hiện tại có thư mục `credentials/` với file JSON — chỉ nên dùng cho phát triển cục bộ. Nếu đẩy lên remote, hãy loại trừ các file bí mật bằng `.gitignore`.

## Triển khai

- Đây là dự án demo; để triển khai lên production cần làm thêm các bước: chuyển DB, cấu hình biến môi trường an toàn, HTTPS, cấu hình static/media (nginx/Cloud Storage), và tinh chỉnh settings (DEBUG=False, ALLOWED_HOSTS, v.v.).

## Góp ý & Phát triển thêm

- Nâng cấp hệ thống thanh toán thực sự
- Thêm pagination, lọc nâng cao cho tìm kiếm
- Cải thiện bảo mật và kiểm thử end-to-end

## Liên hệ

- Nhóm: QLDA_22NH11_G8_CyberBug
- Repo: tên nhánh `main` trong workspace hiện tại

---

Nếu bạn muốn, tôi có thể thêm phần hướng dẫn cấu hình chi tiết cho từng API (OpenAI / HuggingFace / Deepseek / Dialogflow) hoặc tạo file `.env.example` và scripts khởi tạo môi trường. Chỉ cần nói rõ bạn muốn phần nào tiếp theo.
# QLDA_22NH11_G8_CyberBug
Quản Lý Dự Án Công Nghệ Thông Tin
