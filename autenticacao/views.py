from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        return HttpResponse(f'{usuario} - {email} - {senha} - {confirmar_senha}')


    return render(request, 'cadastro.html')

def logar(request):
    return render(request, 'logar.html')