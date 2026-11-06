from django.db import IntegrityError, connections, transaction
from django.utils.text import slugify

MAX_SLUG_SAVE_RETRIES = 3

UKRAINIAN_TRANSLIT = {
    'а': 'a',
    'б': 'b',
    'в': 'v',
    'г': 'h',
    'ґ': 'g',
    'д': 'd',
    'е': 'e',
    'є': 'ye',
    'ж': 'zh',
    'з': 'z',
    'и': 'y',
    'і': 'i',
    'ї': 'yi',
    'й': 'y',
    'к': 'k',
    'л': 'l',
    'м': 'm',
    'н': 'n',
    'о': 'o',
    'п': 'p',
    'р': 'r',
    'с': 's',
    'т': 't',
    'у': 'u',
    'ф': 'f',
    'х': 'kh',
    'ц': 'ts',
    'ч': 'ch',
    'ш': 'sh',
    'щ': 'shch',
    'ь': '',
    'ю': 'yu',
    'я': 'ya',
}


def custom_slugify(text):
    if not text:
        return ''

    translit_text = ''.join(UKRAINIAN_TRANSLIT.get(char, char) for char in text.lower())
    return slugify(translit_text)


def generate_unique_slug(value, queryset, max_length, fallback, exclude_pk=None):
    base_slug = custom_slugify(value) or fallback
    base_slug = base_slug[:max_length].rstrip('-') or fallback[:max_length]
    unique_slug = base_slug
    counter = 1

    existing = queryset.filter(slug=unique_slug)
    if exclude_pk is not None:
        existing = existing.exclude(pk=exclude_pk)

    while existing.exists():
        suffix = f'-{counter}'
        allowed_base_length = max_length - len(suffix)
        unique_slug = f'{base_slug[:allowed_base_length].rstrip("-")}{suffix}'
        counter += 1

        existing = queryset.filter(slug=unique_slug)
        if exclude_pk is not None:
            existing = existing.exclude(pk=exclude_pk)

    return unique_slug


def save_with_unique_slug(instance, save, value, queryset, max_length, fallback):
    if instance.slug:
        save()
        return

    for attempt in range(MAX_SLUG_SAVE_RETRIES + 1):
        instance.slug = generate_unique_slug(
            value,
            queryset,
            max_length,
            fallback,
            exclude_pk=instance.pk,
        )
        try:
            with transaction.atomic(using=queryset.db):
                save()
            return
        except IntegrityError as error:
            cause = error.__cause__
            diagnostic = getattr(cause, 'diag', None)
            violated_constraint = getattr(diagnostic, 'constraint_name', None)
            model = queryset.model
            slug_field = model._meta.get_field('slug')
            if violated_constraint:
                connection = connections[queryset.db]
                with connection.cursor() as cursor:
                    constraints = connection.introspection.get_constraints(
                        cursor, model._meta.db_table
                    )
                is_slug_conflict = (
                    violated_constraint in constraints
                    and constraints[violated_constraint]['unique']
                    and constraints[violated_constraint]['columns']
                    == [slug_field.column]
                )
            else:
                is_slug_conflict = str(cause) == (
                    f'UNIQUE constraint failed: {model._meta.db_table}.'
                    f'{slug_field.column}'
                )
            if not is_slug_conflict:
                raise

            if attempt == MAX_SLUG_SAVE_RETRIES:
                raise
