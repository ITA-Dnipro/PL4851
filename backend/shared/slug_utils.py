from django.db import IntegrityError, transaction
from django.utils.text import slugify

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

    while True:
        instance.slug = generate_unique_slug(
            value,
            queryset,
            max_length,
            fallback,
            exclude_pk=instance.pk,
        )
        try:
            with transaction.atomic():
                save()
            return
        except IntegrityError:
            slug_exists = (
                queryset.filter(slug=instance.slug).exclude(pk=instance.pk).exists()
            )
            if not slug_exists:
                raise
