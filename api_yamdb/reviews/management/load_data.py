import csv

from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, MyUser, Review, Title


class Command(BaseCommand):
    help = 'Load data from CSV files'

    def import_categories(self):
        with open('static/data/category.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Category.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
        self.stdout.write('Categories imported successfully.')

    def import_genres(self):
        with open('static/data/genre.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Genre.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
        self.stdout.write('Genres imported successfully.')

    def import_titles(self):
        with open('static/data/titles.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                category = Category.objects.get(id=row['category'])
                Title.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category=category
                )
        self.stdout.write('Titles imported successfully.')

    def import_users(self):
        with open('static/data/users.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                MyUser.objects.get_or_create(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio']
                )
        self.stdout.write('Users imported successfully.')

    def import_reviews(self):
        with open('static/data/review.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = Title.objects.get(id=row['title_id'])
                author = MyUser.objects.get(id=row['author'])
                Review.objects.get_or_create(
                    id=row['id'],
                    title=title,
                    text=row['text'],
                    author=author,
                    score=row['score'],
                    pub_date=row['pub_date']
                )
        self.stdout.write('Reviews imported successfully.')

    def import_comments(self):
        with open('static/data/comments.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                review = Review.objects.get(id=row['review_id'])
                author = MyUser.objects.get(id=row['author'])
                Comment.objects.get_or_create(
                    id=row['id'],
                    review=review,
                    text=row['text'],
                    author=author,
                    pub_date=row['pub_date']
                )
        self.stdout.write('Comments imported successfully.')

    def import_genre_title(self):
        with open('static/data/genre_title.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                title.genre.add(genre)
        self.stdout.write('Genre-Title relationships imported successfully.')
