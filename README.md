# vjit_network
## Yêu cầu môi trường :fire:
- Python version 3.6.0
- pip version 19.3.1
- gettext version 0.20.1 and iconv version 1.16
## 1. lần đầu clone project về local
sửa local domain [mục 2](README.md#2-sửa-local-domain)\
**chạy script:**\
mở cmd và cd vào root folder project
```
pip install -r 'requirements.txt'
python manage.py makemigrations
python manage.py migrate
python manage.py compilemessages
python manage.py loaddata fixtures/initial_teachers_app.json
```
**start project:**\
```
python manage.py runserver
```
mở browser nhập **[www.mysite.local:8000](http://www.mysite.local:8000/)** :ok_hand:
 ## 2. chỉnh sửa file đa ngôn ngữ
 kiểm tra các ngôn ngữ hỗ trợ trong **[locale](locale/)/** \
 :warning: mặc định là tiếng anh(**en**) \
 :pencil2: label được định nghĩa trong template html. ví dụ: ```{% trans "Home" %}```
 ### thêm một ngôn ngữ mới
 1. chạy script:
     ```
     python manage.py makemessages -l vi -i env
     ```
     **vi** là [language code](http://www.lingoes.net/en/translator/langcode.htm)\
     **[vi/LC_MESSAGES/django.po](locale/vi/LC_MESSAGES/django.po)** sẽ được tạo ra trong **[locale](locale/)**
 2. sửa lại **msgstr** trong file **[vi/LC_MESSAGES/django.po](locale/vi/LC_MESSAGES/django.po)** cho từng label
 3. biên dịch lại file ngôn ngữ, chạy script:
    ```
    python manage.py compilemessages
    ```
 4. restart lại project.
