"""
Filters for the todos app.

This module contains filter classes for Todo queryset filtering.
"""

import django_filters

from .models import Todo


class TodoFilter(django_filters.FilterSet):
    """
    FilterSet for Todo model.

    Supports filtering by:
    - completed: Boolean filter for completion status
    - priority: Exact match filter for priority level
    - due_date_from: Filter todos with due_date >= given date
    - due_date_to: Filter todos with due_date <= given date
    """

    due_date_from = django_filters.DateTimeFilter(
        field_name="due_date",
        lookup_expr="gte",
        help_text="Filter todos with due date on or after this datetime",
    )
    due_date_to = django_filters.DateTimeFilter(
        field_name="due_date",
        lookup_expr="lte",
        help_text="Filter todos with due date on or before this datetime",
    )

    class Meta:
        model = Todo
        fields = {
            "completed": ["exact"],
            "priority": ["exact"],
        }
