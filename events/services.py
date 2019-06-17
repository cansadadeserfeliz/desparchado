def get_event_press_articles(event):
    press_articles = event.press_articles.all()
    for book in event.books.all():
        press_articles |= book.press_articles.all()
    return press_articles
