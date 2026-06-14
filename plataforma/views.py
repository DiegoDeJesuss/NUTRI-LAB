# from urllib import request  <- Comentei essa linha já que você queria remover

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants
from .models import Pacientes

@login_required(login_url='/auth/logar/')
def pacientes(request):
    if request.method == "GET":
        return render(request, 'pacientes.html')
        
    elif request.method == "POST":
        nome = request.POST.get('nome')
        sexo = request.POST.get('sexo')
        idade = request.POST.get('idade')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        
        # Validação de campos vazios
        if (len(nome.strip()) == 0) or (len(sexo.strip()) == 0) or (len(idade.strip()) == 0) or (len(email.strip()) == 0) or (len(telefone.strip()) == 0):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect('/pacientes/')
            
        # Validação de idade numérica
        if not idade.isnumeric():
            messages.add_message(request, constants.ERROR, 'Digite uma idade válida')
            return redirect('/pacientes/')
            
        # Validação de e-mail duplicado
        pacientes_db = Pacientes.objects.filter(email=email)
        if pacientes_db.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um paciente com esse E-mail')
            return redirect('/pacientes/')
        
        # Bloco Try...Except corrigido
        try:
            paciente = Pacientes(nome=nome,
                                 sexo=sexo,
                                 idade=idade,
                                 email=email,
                                 telefone=telefone,
                                 nutri=request.user) # <--- A CORREÇÃO ESTÁ AQUI!
            paciente.save()
            
            # Estas linhas de sucesso agora estão DENTRO do bloco try
            messages.add_message(request, constants.SUCCESS, 'Paciente cadastrado com sucesso')
            return redirect('/pacientes/')
            
        except Exception as e: # O except agora está perfeitamente alinhado com o try
            print(f"\n=============================")
            print(f"ERRO AO SALVAR: {e}")
            print(f"=============================\n")
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema')
            return redirect('/pacientes/')