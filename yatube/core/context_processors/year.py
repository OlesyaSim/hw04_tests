import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    year = datetime.date.today()
    return {'year': year.year}
