from django.contrib import admin

from blog.models import Category, Location, Post


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (PostInline,)
    list_display = ('is_published', 'title', 'slug')
    list_editable = ('is_published', 'slug',)
    list_display_links = ('title',)


class LocationAdmin(admin.ModelAdmin):
    inlines = (PostInline,)
    list_display = ('is_published', 'name')
    list_editable = ('is_published',)
    list_display_links = ('name',)


class PostAdmin(admin.ModelAdmin):
    list_display = ('is_published', 'title', 'author',
                    'category', 'location', 'pub_date')
    list_editable = ('is_published',)
    search_fields = ('title', 'author',
                     'location', 'category')
    list_filter = ('is_published', 'author',
                   'location', 'category', 'pub_date')
    list_display_links = ('title',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
