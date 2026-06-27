from datetime import datetime
from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants
from .models import Opcao, Pacientes, DadosPaciente, Refeicao
from django.views.decorators.csrf import csrf_exempt

@login_required(login_url='/auth/logar/')
def pacientes(request):
    if request.method == "GET":
        dados_paciente = DadosPaciente.objects.filter(paciente__nutri=request.user).order_by('-data')
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'pacientes.html', {'pacientes': pacientes, 'dados_paciente': dados_paciente})
        
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
        
        # Salvando o paciente
        try:
            paciente = Pacientes(nome=nome,
                                 sexo=sexo,
                                 idade=idade,
                                 email=email,
                                 telefone=telefone,
                                 nutri=request.user)
            paciente.save()
            
            messages.add_message(request, constants.SUCCESS, 'Paciente cadastrado com sucesso')
            return redirect('/pacientes/')
            
        except Exception as e:
            print(f"\n=============================")
            print(f"ERRO AO SALVAR: {e}")
            print(f"=============================\n")
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema')
            return redirect('/pacientes/')


@login_required(login_url='/auth/logar/')
def dados_paciente_listar(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'dados_paciente_listar.html', {'pacientes': pacientes})


@login_required(login_url='/auth/logar/')
def dados_paciente(request, id):            
    paciente = get_object_or_404(Pacientes, id=id)
    
    # Validação de segurança
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/pacientes/')
           
    if request.method == "GET":
        # Buscando o histórico do paciente para preencher a tabela dinâmica
        dados_paciente = DadosPaciente.objects.filter(paciente=paciente)
        return render(request, 'dados_paciente.html', {'paciente': paciente, 'dados_paciente': dados_paciente})
           
    elif request.method == "POST":
        # O replace(',', '.') garante que se o usuário digitar 1,75 o Python transforme em 1.75
        peso = request.POST.get('peso', '').replace(',', '.')
        altura = request.POST.get('altura', '').replace(',', '.')
        gordura = request.POST.get('gordura', '').replace(',', '.')
        musculo = request.POST.get('musculo', '').replace(',', '.')
        hdl = request.POST.get('hdl', '').replace(',', '.')
        ldl = request.POST.get('ldl', '').replace(',', '.')
        colesterol_total = request.POST.get('ctotal', '').replace(',', '.')
        trigliceridios = request.POST.get('trigliceridios', '').replace(',', '.')

        try:
            # Salvando os novos dados
            novo_dado = DadosPaciente(
                paciente=paciente,
                data=datetime.now(),
                peso=peso,
                altura=altura,
                percentual_gordura=gordura,
                percentual_musculo=musculo,
                colesterol_hdl=hdl,
                colesterol_ldl=ldl,
                colesterol_total=colesterol_total,
                trigliceridios=trigliceridios
            )
            novo_dado.save()
            messages.add_message(request, constants.SUCCESS, 'Dados cadastrados com sucesso')
        except Exception as e:
            # Caso o banco de dados recuse o formato do número
            print(f"ERRO AO SALVAR DADOS DO PACIENTE: {e}")
            messages.add_message(request, constants.ERROR, 'Erro ao salvar. Verifique se os números estão corretos.')

        # Redirecionando de volta para a mesma página com o ID correto
        return redirect(f'/dados_paciente/{id}/')
    


@login_required(login_url='/auth/logar/')
@csrf_exempt
def grafico_peso(request, id):
    paciente = Pacientes.objects.get(id=id)
    dados = DadosPaciente.objects.filter(paciente=paciente).order_by("data")
    
    
    
    pesos = [dado.peso for dado in dados]
    labels = list(range(len(pesos)))
    data = {'peso': pesos,
    'labels': labels}
    return JsonResponse(data)


def plano_alimentar_listar(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'plano_alimentar_listar.html', {'pacientes': pacientes})
    

def plano_alimentar(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/plano_alimentar_listar/')
    if request.method == "GET":
        r1 = Refeicao.objects.filter(paciente=paciente).order_by('horario')
        return render(request, 'plano_alimentar.html', {'paciente': paciente, 'refeicao':r1})     
       
    
def refeicao(request, id_paciente):
    paciente = get_object_or_404(Pacientes, id=id_paciente)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/dados_paciente/')
    if request.method == "POST":
        titulo = request.POST.get('titulo')
        horario = request.POST.get('horario')
        carboidratos = request.POST.get('carboidratos')
    proteinas = request.POST.get('proteinas')
    gorduras = request.POST.get('gorduras')
    
    
    r1 = Refeicao(paciente=paciente,
        titulo=titulo,
        horario=horario,
        carboidratos=carboidratos,
        proteinas=proteinas,
        gorduras=gorduras)
    r1.save()

    messages.add_message(request, constants.SUCCESS, 'Refeição cadastrada')
    return redirect(f'/plano_alimentar/{id_paciente}')


def opcao(request, id_paciente):
    if request.method == "POST":
        id_refeicao = request.POST.get('refeicao')
        imagem = request.FILES.get('imagem')
        descricao = request.POST.get("descricao")
        
        o1 = Opcao(refeicao_id=id_refeicao,
        imagem=imagem,
        descricao=descricao)
        o1.save()
        
        
        messages.add_message(request, constants.SUCCESS, 'Opcao cadastrada')
        return redirect(f'/plano_alimentar/{id_paciente}')


    
    
