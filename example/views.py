from django.shortcuts import render


def index(request):
    context = {
        'context': 'Place holder',
    }
    return render(request, 'index.html', context)