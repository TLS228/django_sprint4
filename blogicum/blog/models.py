from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    """
    Абстрактная модель.
    Добавляет к модели дату создания и отметку о публикации.
    """

    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено')

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True, verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(max_length=256, verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(BaseModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    image = models.ImageField(blank=True, upload_to='posts_images',
                              verbose_name='Фото')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем '
        '— можно делать отложенные публикации.')
    author = models.ForeignKey(User, related_name='posts',
                               on_delete=models.CASCADE,
                               verbose_name='Автор публикации')
    category = models.ForeignKey(Category, null=True,
                                 related_name='posts',
                                 on_delete=models.SET_NULL,
                                 verbose_name='Категория')
    location = models.ForeignKey(Location, null=True, blank=True,
                                 related_name='posts',
                                 on_delete=models.SET_NULL,
                                 verbose_name='Местоположение')

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        constraints = (models.UniqueConstraint(
            fields=('title', 'text', 'author'),
            name='Unique post constraint',),)

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments',)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено')
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)
