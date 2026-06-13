import os
import secrets # Adicionado para gerar tokens mais seguros

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib import auth
from django.conf import settings
from django.db import IntegrityError # Adicionado para tratar erros de banco de dados

from .ultis import password_is_valid, email_html
from .models import Ativacao

# Create your views here.
def cadastro(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'cadastro.html')

    elif request.method == 'POST':
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not password_is_valid(request, senha, confirmar_senha):
            return redirect('cadastro')

        # 1. VALIDAÇÃO: Evita o erro de integridade checando se o usuário já existe
        if User.objects.filter(username=usuario).exists():
            messages.add_message(request, constants.ERROR, 'Este nome de usuário já está em uso.')
            return redirect('cadastro')

        if User.objects.filter(email=email).exists():
            messages.add_message(request, constants.ERROR, 'Este e-mail já está cadastrado.')
            return redirect('cadastro')

        try:
            user = User.objects.create_user(
                username=usuario,
                email=email,
                password=senha,
                is_active=False
            )
            user.save()

            # 2. SEGURANÇA: Gera um token aleatório e seguro
            token = secrets.token_hex(32)
            ativacao = Ativacao(token=token, user=user)
            ativacao.save()

            path_template = os.path.join(settings.BASE_DIR, 'autenticacao/templates/emails/cadastro_confirmado.html')
            email_html(path_template, 'Cadastro confirmado', [email], username=user.username, link_ativacao=f"http://127.0.0.1:8000/auth/ativar_conta/{token}")
            print(f"\n[DEV] LINK DE ATIVAÇÃO LIMPO: http://127.0.0.1:8000/auth/ativar_conta/{token}\n")
            
            messages.add_message(request, constants.SUCCESS, 'Usuário criado com sucesso! Verifique seu e-mail.')
            return redirect('/auth/logar')

        except IntegrityError:
            messages.add_message(request, constants.ERROR, 'Erro de integridade nos dados.')
            return redirect('cadastro')

        except Exception as e:
            # 3. DEBUG: Imprime o erro real no terminal para você saber o que quebrou
            print(f"\n=========================================")
            print(f"ERRO REAL NO CADASTRO: {e}")
            print(f"=========================================\n")
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema')
            return redirect('cadastro')


def logar(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'logar.html')
        
    elif request.method == "POST":
        username = request.POST.get('usuario')
        senha = request.POST.get('senha')

        usuario = auth.authenticate(username=username, password=senha)
        if not usuario:
            messages.add_message(request, constants.ERROR, 'Username ou senha inválidos')
            return redirect('/auth/logar')
        else:
            auth.login(request, usuario)
            return redirect('/') 


def sair(request):
    auth.logout(request)
    return redirect('/auth/logar') 


def ativar_conta(request, token):
    # 4. LÓGICA: Variável renomeada para ativacao_obj para não confundir com o texto do token
    ativacao_obj = get_object_or_404(Ativacao, token=token)
    
    if ativacao_obj.ativo:
        messages.add_message(request, constants.WARNING, 'Esse token já foi usado')
        return redirect('/auth/logar')
        
    # 5. OTIMIZAÇÃO: Atualiza o usuário direto pela relação, sem precisar de nova busca no banco
    ativacao_obj.user.is_active = True
    ativacao_obj.user.save()
    
    ativacao_obj.ativo = True
    ativacao_obj.save()
    
    messages.add_message(request, constants.SUCCESS, 'Conta ativa com sucesso')
    return redirect('/auth/logar')