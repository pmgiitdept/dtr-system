from .models import Settings

def general_settings(request):
    try:
        settings = Settings.objects.get(id=1)
    except Settings.DoesNotExist:
        settings = None
    return {
        "theme_mode": settings.theme_mode if settings else "light",
        "font_size": settings.font_size if settings else "medium",
        "layout_spacing": settings.layout_spacing if settings else "comfortable",
    }
