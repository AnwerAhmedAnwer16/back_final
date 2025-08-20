from django.db import models
from django.conf import settings
from django.utils import timezone


class SearchHistory(models.Model):
    """تاريخ البحث للمستخدمين"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_history',
        null=True,
        blank=True  # للسماح بالبحث للمستخدمين غير المسجلين
    )
    query = models.CharField(max_length=100, db_index=True)
    search_type = models.CharField(
        max_length=20,
        choices=[
            ('unified', 'Unified Search'),
            ('users', 'Users Only'),
            ('tags', 'Tags Only'),
            ('quick', 'Quick Search')
        ],
        default='unified'
    )
    results_count = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['query', '-created_at']),
            models.Index(fields=['search_type', '-created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user or 'Anonymous'} searched for '{self.query}'"


class PopularSearch(models.Model):
    """الكلمات الشائعة في البحث"""
    query = models.CharField(max_length=100, unique=True, db_index=True)
    search_count = models.IntegerField(default=1)
    last_searched = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['-search_count']),
            models.Index(fields=['-last_searched']),
        ]
        ordering = ['-search_count', '-last_searched']

    def __str__(self):
        return f"'{self.query}' ({self.search_count} searches)"
