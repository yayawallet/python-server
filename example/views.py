from django.shortcuts import render


def index(request):
    context = {
        'title': 'Home Page',
        'heading': 'Welcome to Home page!',
        'content': 'This is some content for Home page.',
    }
    return render(request, 'index.html', context)