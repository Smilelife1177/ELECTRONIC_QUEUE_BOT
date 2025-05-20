# Звіт про використані команди

## Підготовка

- `git config --global user.name "Oleg Shapran"
  `Налаштування імені користувача для Git.
- `git config --global user.email "shapran1177@gmail.com"`
  Налаштування email користувача для Git.

## Базова гілка

- `git checkout main`Перехід на гілку main.
- `echo "Pet2025" > README.md`Створення файлу README.md із коротким описом проєкту.
- `git add README.md`Додавання файлу README.md до індексу Git.
- `git commit -m "first commit added readme.md"`
  Створення коміта з повідомленням про додавання README.md.

## Створення й робота з функціональними гілками

- `git checkout -b alpha_read `Створення та перехід на гілку feature/one.
- `git checkout -b  fix_+admin   `Створення та перехід на гілку feature/two.
- `rm pravki.txt  `Видалення не потрібного файлу
- `git add .`Додавання всього.
- `git commit -m "added_new_admin"`Створення коміта для гілки fix_+admin.

## Додавання віддаленого репозиторію

- `git remote add origin git@github.com:<Smilelife1177>/<Pet2025>.git`
  Додавання віддаленого репозиторію GitHub як origin.

## Публікація вибраних гілок

- `git push -u origin main`Відправлення гілки main на GitHub і налаштування відстежування.
