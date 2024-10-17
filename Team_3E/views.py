from django.shortcuts import render, redirect, get_object_or_404                         # 렌더링, 리디렉션                                    # DB 모델
from .models import Users,Character,Friendship,Inventory,Opponent,EnergyHistory,LastestEnergyHistory                                    # Character 모델 import 추가
from .models import EnergySavingQuiz,DailyMission,MissionTemplate,UserMission,DailyMissionCompletion
from django.contrib.auth import login                                 # Django 내장 시스템 (사용자 세션 로그인)
from django.contrib.auth.decorators import login_required             # 로그인한 사용자만 접근 가능하도록 제한
from django.contrib.auth.hashers import make_password, check_password # 비밀번호 암호화, 암호화된 비밀번호와 기본 비밀번호 크로스체크
from django.contrib import messages                                   # Django 내장 시스템 (성공, 오류 등 피드백 전달용)
from django.views.decorators.csrf import csrf_exempt  # csrf_exempt 임포트 추가
from django.http import JsonResponse, HttpResponse
from django.db import connection
from datetime import datetime, timedelta
from django.db.models import Max
import random
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
import matplotlib.pyplot as plt
import os
import matplotlib.pyplot as plt
from django.conf import settings



## 메인 페이지
def Home (request):
    return render(request, "main.html")

# 아이디 및 비밀번호 찾기 페이지
def Find_Info(request):
    return render(request, 'find_info.html')

# 아이디 찾기
@csrf_exempt  # CSRF 검증을 비활성화 (배포할 때는 주의 필요)
def Find_Id(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')

        # DB에서 사용자 아이디를 검색하는 로직
        user = Users.objects.filter(name=name, email=email).first()  # 'name' 필드 사용
        if user:
            send_mail(
                '아이디찾기',
                f'당신의 아이디는 {user.user_id}입니다.',
                'from@example.com',
                [email],
                fail_silently=False,
            )
            return JsonResponse({'message': '이메일로 아이디가 발송되었습니다.'})
        else:
            return JsonResponse({'message': '해당 정보를 가진 사용자가 없습니다.'})

    return JsonResponse({'message': '잘못된 요청입니다.'})

# 비밀번호 찾기
@csrf_exempt  # CSRF 검증을 비활성화 (배포할 때는 주의 필요)
def Find_Pw(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('id')
        email = data.get('email')

        # DB에서 비밀번호 재설정 요청 처리
        user = Users.objects.filter(user_id=user_id, email=email).first()  # 'user_id' 필드 사용
        if user:
            # 비밀번호 재설정 토큰 생성 및 이메일 발송 로직
            reset_token = "임시 비밀번호 토큰 생성 로직"  # 실제 토큰 생성 로직으로 대체 필요
            send_mail(
                '비밀번호 재설정',
                f'비밀번호를 재설정하려면 아래 링크를 클릭하세요: http://example.com/reset_password?token={reset_token}',
                'from@example.com',
                [email],
                fail_silently=False,
            )
            return JsonResponse({'message': '이메일로 비밀번호 재설정 링크가 발송되었습니다.'})
        else:
            return JsonResponse({'message': '해당 정보를 가진 사용자가 없습니다.'})

    return JsonResponse({'message': '잘못된 요청입니다.'})



## 회원가입 페이지
def Register (request):
    return render(request, "register.html")


# 회원가입 액션 처리
def Register_Action (request):
    # 입력받은 값 정의
    var_user_id  = request.POST.get('input_user_id')
    var_password = request.POST.get('input_password')
    var_name     = request.POST.get('input_name')
    var_email    = request.POST.get('input_email')

    # 빈 필드가 없는지 검증
    if not (var_user_id and var_password and var_name and var_email):
        messages.error(request, '모든 필드를 입력해주세요.')
        return redirect('회원가입')

    # 아이디 중복확인
    if Users.objects.filter(user_id=var_user_id).exists():
        messages.error(request, '이미 존재하는 아이디입니다.')
        return redirect('회원가입')

    # 이메일 중복확인
    if Users.objects.filter(email=var_email).exists():
        messages.error(request, '이미 존재하는 이메일입니다.')
        return redirect('회원가입')
    

    user_object = Users.objects.create(
        user_id  = var_user_id,
        password = var_password,
        name     = var_name,
        email    = var_email
    )

    Inventory.objects.create(
        character_name = "기본 캐릭터 1",
        attack_power = 15,
        defense = 0,
        health = 100,
        is_main_character = True,
        user = user_object
    )

    Inventory.objects.create(
        character_name = "기본 캐릭터 2",
        attack_power = 10,
        defense = 5,
        health = 100,
        user = user_object
    )

    Inventory.objects.create(
        character_name = "기본 캐릭터 3",
        attack_power = 10,
        defense = 0,
        health = 150,
        user = user_object
    )

    EnergyHistory.objects.create(
        amount = 0,
        exp = 0,
        savings = 0,
        user = user_object
    )

    LastestEnergyHistory.objects.create(
        user=user_object,
        energy_1=0,
        energy_2=0,
        energy_3=0,
        energy_4=0,
        exp=0,
        gain_exp=0,
        start_time=timezone.now(),
        end_time=timezone.now()
    )

    DailyMission.objects.create(
        clear_count = 0,
        daily_count = 1,
        user=user_object
    )

    # 회원가입 완료 후 로그인 페이지로 이동
    messages.success(request, '회원가입이 완료되었습니다. 로그인 해주세요.')
    return render(request, "login.html")


## 로그인 페이지
def Login (request):
    return render(request, "login.html")


# 로그인 액션 처리
def Login_Action(request):
    if request.method == 'POST':
        # 입력받은 값 정의
        var_user_id = request.POST.get('input_user_id')
        var_password = request.POST.get('input_password')

        # 빈 필드가 없는지 검증
        if not (var_user_id and var_password):
            messages.error(request, '아이디와 비밀번호를 모두 입력해주세요.')
            return redirect('로그인')

        # 입력된 아이디로 유저 조회
        select_user = Users.objects.filter(user_id=var_user_id).first()

        if not select_user:
            messages.error(request, '존재하지 않는 아이디입니다.')
            return redirect('로그인')

        # 비밀번호가 일치하는지 확인
        # 비밀번호 확인 로직 수정
        if select_user.password != var_password:  # 비밀번호가 일치하지 않을 때
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return redirect('로그인')
        
        # daily_count 증가 로직
        # 마지막 로그인 날짜(last_login)과 현재시간(currnet_date) 를 비교해서 차이를 daily_count에 더함
        if select_user.last_login is not None:  # last_login이 None이 아닐 경우만 처리
            last_login_date = select_user.last_login.date()
            current_date = timezone.now().date()
            date_difference = (current_date - last_login_date).days
            print(f'date_difference = {date_difference}')
    
            if date_difference > 0:
                daily_mission_object = DailyMission.objects.get(user=select_user)
                daily_mission_object.daily_count += date_difference
                daily_mission_object.save()

        # 유저 로그인
        login(request, select_user)
        # messages.success(request, f'{var_user_id}님, 환영합니다!')


        # 로그인 후 사용자 정보를 기반으로 리다이렉트
        if Inventory.objects.filter(user = request.user, is_main_character = True).exists():
            return redirect('게임_메인')  # 대표 캐릭터가 존재할 경우
        else:
            return redirect('캐릭터 선택 페이지')  # 대표 캐릭터가 없을 경우

    else:
        return render(request, 'user_login.html')  # GET 요청 시 로그인 페이지 반환


# 로그아웃 처리
def Logout (request):
    # 세션 초기화
    request.session.flush()
    # messages.success(request, '로그아웃되었습니다.')
    return redirect('홈페이지')


## 마이페이지
@login_required
def Mypage (request):
    energy_savings_object = EnergyHistory.objects.get(user=request.user).savings

    # 그래프 생성 (절약량을 기반으로)
    generate_graph(energy_savings_object)

    saved_pees = energy_savings_object * 200

    return render(request, 'mypage/mypage.html', {
        'savings': energy_savings_object,
        'graph_url': '/media/savings_graph1.jpg',  # 올바른 이미지 URL
        'saved_pees': saved_pees
    })


# 회원정보 수정 페이지
def Mypage_Edit_Info(request):
    return render(request, 'mypage/edit_info.html')


# 에너지 절약량 확인
def Mypage_Energy_Savings(request):
    energy_savings_object = EnergyHistory.objects.get(user=request.user).savings

    # 그래프 생성 (절약량을 기반으로)
    generate_graph(energy_savings_object)

    saved_pees = energy_savings_object * 200

    dictionary = {
        'savings': energy_savings_object,
        'graph_url': '/media/savings_graph1.jpg',  # 올바른 이미지 URL
        'saved_pees': saved_pees
    }

    return render(request, 'mypage/energy_savings.html', dictionary)


# 일일 미션 출석부
def Mypage_Attendance_Resister(request):
    completions = DailyMissionCompletion.objects.filter(user=request.user)
    return render(request, 'mypage/attendance_register.html', {'completions': completions})



# 회원정보 수정 처리
@login_required
def Mypage_info_edit (request):
    # 입력받은 값 정의
    var_user_id = request.POST.get('input_user_id')
    var_name    = request.POST.get('input_name')
    var_email   = request.POST.get('input_email')

    # 빈 필드가 없는지 검증
    if not (var_user_id and var_name and var_email):
        messages.error(request, '모든 필드를 입력해주세요.')
        return redirect('마이페이지')

    # 아이디 중복 확인
    if Users.objects.filter(user_id=var_user_id).exists():
        messages.error(request, '이미 존재하는 아이디입니다.')
        return redirect('마이페이지')

    # 이메일 중복 확인
    if Users.objects.filter(email=var_email).exists():
        messages.error(request, '이미 존재하는 이메일입니다.')
        return redirect('마이페이지')

    # 유저 정보 수정
    try:
        user = Users.objects.get(id=request.user.id)
        user.user_id = var_user_id
        user.name    = var_name
        user.email   = var_email
        user.save()
        messages.success(request, '회원정보가 성공적으로 수정되었습니다.')
    except Users.DoesNotExist:
        messages.error(request, '유저를 찾을 수 없습니다.')
        return redirect('마이페이지')

    return render(request, 'mypage.html')

# 회원탈퇴
def Delete_User(request):
    user_object = request.user
    delete_user = Users.objects.get(id = user_object.id)
    delete_user.delete()
    messages.info(request,'회원탈퇴가 완료되었습니다.')

    return redirect('로그인')


## 게임_메인 페이지
def Game_Main(request):
    user = request.user
    character_object = Inventory.objects.filter(user=user, is_main_character=True).first()

    current_experience = character_object.total_experience
    required_experience = character_object.level * 100
    energy_history = EnergyHistory.objects.filter(user = user).first()

    # 최신 에너지 절약 기록 가져오기
    latest_energy_history = LastestEnergyHistory.objects.filter(user = user).order_by('-date')  # 최신 5개 기록 가져오기
    time_object = LastestEnergyHistory.objects.filter(user = user).order_by('-end_time').first()

    # 경험치 비율 계산
    if required_experience > 0:
        experience_ratio = (current_experience / required_experience) * 100
    else:
        experience_ratio = 0  # 필요 경험치가 0일 경우 비율을 0으로 설정

    # 일일 미션 클리어했는지 확인
    daily_mission_object = DailyMission.objects.get(user = user)
    mission_clear_date = daily_mission_object.last_clear_date
    current_time = timezone.now().date()
    daily_mission_cleared = mission_clear_date == current_time

    # 미션 클리어율 나타내기
    clear_count = daily_mission_object.clear_count
    daily_count = daily_mission_object.daily_count
    
    clear_rate = int((clear_count / daily_count) * 100)

    # 친구 신청이 왔을 경우 느낌표 띄우기
    friend_status = Friendship.objects.filter(connected_user=request.user).first()
    if friend_status is None:
        friend_status = None
    else:
        friend_status = friend_status.status

    context = {
        'user': user,
        'character': character_object,
        'current_experience': current_experience,
        'required_experience': required_experience,
        'energy_history': energy_history,
        'experience_ratio': experience_ratio,  # 경험치 비율 추가
        'latest_energy_history': latest_energy_history,  # 최신 에너지 절약 기록 추가
        'time_object' : time_object,
        'daily_mission_cleared' : daily_mission_cleared,
        'clear_rate' : clear_rate,
        'friend_status' : friend_status,
    }

    return render(request, 'game/game_main.html', context)


## 랭킹 조회 페이지
def Rangking(request):
    # 모든 사용자의 가장 높은 레벨 캐릭터 가져오기
    highest_level_characters = Inventory.objects.values('user').annotate(max_level = Max('level'))

    # 유저별 가장 높은 레벨 캐릭터 객체를 저장할 리스트
    characters_object = []

    for character in highest_level_characters:
        # 사용자 ID로 캐릭터를 가져옴
        user_inventory = Inventory.objects.filter(user = character['user'], level = character['max_level'])
        if user_inventory.exists():
            characters_object.append(user_inventory.first())  # 가장 높은 레벨 캐릭터 추가

    request_user = request.user.id  # 현재 로그인한 사용자 ID
    user_object = Users.objects.get(id=request_user)  # 사용자 객체 가져오기

    characters_object = sorted(characters_object, key=lambda character: character.level, reverse=True)

    dictionary = {
        'characters': characters_object,  # 유저별 가장 높은 레벨 캐릭터 목록
        'user': user_object,               # 현재 사용자 정보
    }

    return render(request, 'game/rangking/rangking.html', dictionary)


# 랭킹 페이지에서 방문하기
def Rangking_Visit(request, character_id):
    character_object = Inventory.objects.get(id = character_id)
    user_object = Users.objects.get(id = character_object.user.id)
    character_objects = Inventory.objects.filter(user = user_object)
    main_character_object = character_objects.filter(is_main_character = True).first()

    dictionary = {
        'user' : user_object,
        'characters' : character_objects,
        'main_character' : main_character_object,
    }
    return render(request, 'game/rangking/rangking_visit.html', dictionary)


# 도전랭킹
def Challenge_Rangking(request):
    user = Users.objects.order_by('-challenge_level')
    return render(request,'game/rangking/rangking.html',{'users' : user})


# 도전랭킹 페이지에서 방문하기
def Challenge_Rangking_Visit(request, user_id):
    user_object = Users.objects.get(id = user_id)
    character_objects = Inventory.objects.filter(user = user_object)
    main_character_object = character_objects.filter(is_main_character = True).first()

    dictionary = {
        'challenge_user' : user_object,
        'challenge_characters' : character_objects,
        'challenge_main_character' : main_character_object,
    }
    return render(request, 'game/rangking/rangking_visit.html', dictionary)


## 친구 페이지
def Friend(request):
    

    friend_objects = Friendship.objects.filter(connected_user = request.user, status = 'accepted')


    # 첫번째 줄
    request_user = Friendship.objects.filter(friend = request.user, status = 'request')
    # 두번째 줄
    pending_request = Friendship.objects.filter(connected_user = request.user, status = 'pending')


    dictionary = {
        'friends' : friend_objects,
        'requests' : request_user,
        'requester' : pending_request
    }

    return render(request, 'game/friend/friend.html', dictionary)


# 친구_방문하기
def Friend_Visit(request, friend_id):
    user_object = Users.objects.get(id = friend_id)
    character_objects = Inventory.objects.filter(user = user_object)
    main_character_object = character_objects.filter(is_main_character = True).first()

    dictionary = {
        'user' : user_object,
        'characters' : character_objects,
        'main_character' : main_character_object,
    }
    return render(request, 'game/friend/friend_visit.html', dictionary)


# 친구_유저 검색 칸
def Friend_Search(request):
    trigger = request.user
    return render(request, 'game/friend/friend.html', {'trigger' : trigger})


# 친구_유저 검색
def Search_User(request):
    var_user_id = request.POST.get('input_user_id')
    user_object = Users.objects.filter(user_id__icontains = var_user_id).exclude(user_id = request.user.user_id)

    return render(request, 'game/friend/friend.html', {'users' : user_object})


# 친구 신청하기
def Add_Friend_Request(request, user_id):
    requester = request.user
    addressee = get_object_or_404(Users, id = user_id)

    # 이미 친구 관계가 존재하는지 확인
    if Friendship.objects.filter(connected_user = requester, friend = addressee).exists():
        messages.error(request, '해당 유저와 이미 친구입니다.')
        return redirect('유저 검색 칸')
    else:
        Friendship.objects.create(
            connected_user = requester,
            friend = addressee,
            status = 'request'
        )

        Friendship.objects.create(
            connected_user = addressee,
            friend = requester,
            status = 'pending'
        )

        messages.success(request, '친구 신청을 보냈습니다.')
        return redirect('친구')
    

# 친구 신청 수락하기
def Add_Friend_Accept(request, connected_user_id):

    user_object = request.user

    requester = Users.objects.get(id = connected_user_id)
    addressee = Users.objects.get(id = user_object.id)
    
    requester_object = Friendship.objects.get(connected_user = requester, friend = addressee)
    addressee_object = Friendship.objects.get(connected_user = addressee, friend = requester)

    requester_object.status = 'accepted'
    requester_object.save()

    addressee_object.status = 'accepted'
    addressee_object.save()

    messages.success(request, '친구 수락 완료되었습니다.')
    return redirect('친구')


# 친구 신청 거절하기
def Add_Friend_Refuse(request, connected_user_id):

    user_object = request.user

    requester = Users.objects.get(id = connected_user_id)
    addressee = Users.objects.get(id = user_object.id)

    requester_object = Friendship.objects.get(connected_user = requester, friend = addressee)
    addressee_object = Friendship.objects.get(connected_user = addressee, friend = requester)

    requester_object.delete()

    addressee_object.delete()

    messages.info(request, '친구 수락을 거절했습니다.')
    return redirect('친구')



# 친구 삭제하기
def Delete_Friend(request, user_id):
    delete_user = Users.objects.get(id = user_id)
    delete_user_object = Friendship.objects.filter(connected_user = request.user, friend = delete_user).first()
    delete_user_object.delete()

    delete_opponent_object = Friendship.objects.filter(connected_user = delete_user, friend = request.user).first()
    delete_opponent_object.delete()

    return redirect('친구')


# 친구에게 도전하기
def Challenge_Friend(request, friend_id):
    # 친구 객체 가져오기
    friend_object = Users.objects.get(id=friend_id)
    friend_character = Inventory.objects.get(user=friend_object, is_main_character=True)

    # 로그인한 사용자의 메인 캐릭터 정보를 Inventory에서 가져오기
    main_character = Inventory.objects.get(user=request.user, is_main_character=True)

    player_attack_power = main_character.attack_power
    player_defense = main_character.defense
    player_health = main_character.health
    player_name = main_character.character_name

    # 친구 캐릭터 정보
    opponent_attack_power = friend_character.attack_power
    opponent_defense = friend_character.defense
    opponent_health = friend_character.health
    opponent_name = friend_character.character_name

    # 전투 초기화: 플레이어 및 상대방의 HP를 세션에 저장
    if 'player_hp' not in request.session:
        request.session['player_hp'] = player_health
        request.session['opponent_hp'] = opponent_health
        request.session['battle_logs'] = []
        request.session['turn_counter'] = 1

    player_hp = request.session['player_hp']
    opponent_hp = request.session['opponent_hp']
    battle_logs = request.session['battle_logs']
    turn_counter = request.session['turn_counter']

    battle_result = None  # 전투 결과를 저장할 변수

    if request.method == 'POST':
        # 플레이어 공격 처리 로직
        damage_to_opponent = player_attack_power - opponent_defense
        if damage_to_opponent < 1:
            damage_to_opponent = 1
        battle_logs.append(f"{turn_counter}번째 턴: 플레이어가 {opponent_name}에게 {damage_to_opponent}의 피해를 입혔습니다!")
        
        # 상대방의 HP 감소
        opponent_hp -= damage_to_opponent
        if opponent_hp <= 0:
            opponent_hp = 0
            battle_result = 'win'
        
        # 상대방이 아직 살아있는 경우 플레이어에게 피해를 입힘
        if opponent_hp > 0:
            damage_to_player = opponent_attack_power - player_defense
            if damage_to_player < 1:
                damage_to_player = 1
            battle_logs.append(f"{turn_counter}번째 턴: {opponent_name}이(가) 플레이어에게 {damage_to_player}의 피해를 입혔습니다!")
            
            # 플레이어의 HP 감소
            player_hp -= damage_to_player
            if player_hp <= 0:
                player_hp = 0
                battle_result = 'lose'

        # 턴 증가
        turn_counter += 1

        # 세션에 최신 전투 정보 저장
        request.session['player_hp'] = player_hp
        request.session['opponent_hp'] = opponent_hp
        request.session['battle_logs'] = battle_logs
        request.session['turn_counter'] = turn_counter

    # 전투 결과에 따른 처리
    if battle_result is not None:
        # 전투가 끝난 후 두 캐릭터를 초기 상태로 돌리기
        friend_character.health = opponent_health # 친구 캐릭터의 초기 체력으로 복원
        main_character.health = player_health  # 플레이어 캐릭터의 초기 체력으로 복원
        friend_character.save()  # 친구 캐릭터의 변경사항 저장
        main_character.save()  # 플레이어 캐릭터의 변경사항 저장

        # 세션 정보 초기화
        del request.session['player_hp']
        del request.session['opponent_hp']
        del request.session['battle_logs']
        del request.session['turn_counter']

        # 메인페이지로 리다이렉트
        return redirect('게임_메인')  # 메인페이지 URL로 변경

    context = {
        'player_hp': player_hp,
        'opponent_hp': opponent_hp,
        'battle_logs': battle_logs,
        'battle_result': battle_result,
        'player_name': player_name,
        'opponent_name': opponent_name,
        'friend_character': friend_character,
        'main_character' : main_character,
    }

    return render(request, 'game/friend/friend_challenge.html', context)



# 친구에게 도전_초기화
def Challenge_Friend_Reset(request, friend_character_id):
    user_id = request.user.user_id  # 로그인한 사용자 ID 가져오기

    # 로그인한 사용자의 메인 캐릭터의 체력을 가져오기
    try:
        main_character = Inventory.objects.get(user__user_id=user_id, is_main_character=True)
        player_health = main_character.health  # 메인 캐릭터의 체력
    except Inventory.DoesNotExist:
        player_health = 100  # 메인 캐릭터가 없을 경우 기본 체력 설정

    # 친구의 캐릭터 정보를 가져오기
    try:
        opponent = Inventory.objects.get(id=friend_character_id)
        opponent_health = opponent.health  # 상대방의 체력
    except Inventory.DoesNotExist:
        opponent_health = 150  # 상대방 정보가 없을 경우 기본 체력 설정

    # 전투 상태를 초기화
    request.session['player_hp'] = player_health
    request.session['opponent_hp'] = opponent_health
    request.session['battle_logs'] = []
    request.session['turn_counter'] = 1

    return redirect('친구에게 도전', opponent.user.id)



# 전투 페이지 뷰 함수
def Challenge_battle(request, level):
    user_id = request.user.user_id  # 로그인한 사용자 ID를 가져옴


    # 로그인한 사용자의 메인 캐릭터 정보를 Inventory에서 가져오기
    try:
        main_character = Inventory.objects.get(user__user_id=user_id, is_main_character=True)
        player_attack_power = main_character.attack_power  # 메인 캐릭터의 공격력
        player_defense = main_character.defense  # 메인 캐릭터의 방어력
        player_health = main_character.health  # 메인 캐릭터의 체력
        player_name = main_character.character_name  # 메인 캐릭터의 체력
    except Inventory.DoesNotExist:
        # 메인 캐릭터가 없을 경우 기본값 설정
        player_attack_power = 10
        player_defense = 5
        player_health = 100

    # 상대 정보를 가져오기 (해당 레벨에 맞는 상대)
    try:
        opponent = Opponent.objects.get(challenge_level=level)
        opponent_attack_power = opponent.attack_power
        opponent_defense = opponent.defense
        opponent_health = opponent.health
        opponent_name = opponent.name
        opponent_coin = opponent.coin  # 상대의 코인 저장
    except Opponent.DoesNotExist:
        # 상대가 없을 경우 기본값 설정
        opponent_attack_power = 30
        opponent_defense = 10
        opponent_health = 150
        opponent_name = "기본 상대"

    # 전투 초기화: 플레이어 및 상대방의 HP를 세션에 저장
    if 'player_hp' not in request.session:
        request.session['player_hp'] = player_health  # 플레이어의 HP (메인 캐릭터의 체력)
        request.session['opponent_hp'] = opponent_health  # 상대방 HP는 레벨에 맞게 설정
        request.session['battle_logs'] = []
        request.session['turn_counter'] = 1

    player_hp = request.session['player_hp']
    opponent_hp = request.session['opponent_hp']
    battle_logs = request.session['battle_logs']
    turn_counter = request.session['turn_counter']

    battle_result = None  # 전투 결과를 저장할 변수

    if request.method == 'POST':
        # 플레이어 공격 처리 로직
        damage_to_opponent = player_attack_power - opponent_defense
        if damage_to_opponent < 1:
            damage_to_opponent = 1  # 데미지가 음수일 경우 1로 고정
        battle_logs.append(f"{turn_counter}번째 턴: 플레이어가 {opponent_name}에게 {damage_to_opponent}의 피해를 입혔습니다!")
        
        # 상대방의 HP 감소
        opponent_hp -= damage_to_opponent
        if opponent_hp <= 0:
            opponent_hp = 0
            battle_result = 'win'  # 플레이어 승리

            # 플레이어의 도전 레벨을 +1 증가
            request.user.challenge_level += 1
            request.user.save()  # challenge_level 업데이트 후 저장

                # 상대의 코인을 플레이어의 코인에 추가
            request.user.coins += opponent.coin  # opponent의 코인을 플레이어의 coins에 더함
            request.user.save()  # coins 업데이트 후 저장

        # 상대방이 아직 살아있는 경우 플레이어에게 피해를 입힘
        if opponent_hp > 0:
            damage_to_player = opponent_attack_power - player_defense
            if damage_to_player < 1:
                damage_to_player = 1  # 데미지가 음수일 경우 1로 고정
            battle_logs.append(f"{turn_counter}번째 턴: {opponent_name}이(가) 플레이어에게 {damage_to_player}의 피해를 입혔습니다!")
            
            # 플레이어의 HP 감소
            player_hp -= damage_to_player
            if player_hp <= 0:
                player_hp = 0
                battle_result = 'lose'  # 플레이어 패배

        # 턴 증가
        turn_counter += 1

        # 세션에 최신 전투 정보 저장
        request.session['player_hp'] = player_hp
        request.session['opponent_hp'] = opponent_hp
        request.session['battle_logs'] = battle_logs
        request.session['turn_counter'] = turn_counter

    context = {
        'player_hp': player_hp,
        'opponent_hp': opponent_hp,
        'battle_logs': battle_logs,
        'battle_result': battle_result,  # 전투 결과 추가
        'level': level,  # 레벨 정보 추가
        'opponent_name': opponent_name,  # 상대 이름 추가
        'player_name' : player_name,
        'main_character' : main_character,
        'opponent' : opponent,
    }

    return render(request, 'game/challenge/challenge_battle.html', context)


## 도전 페이지
def Challenge(request):
    user = request.user  # 로그인한 사용자 가져오기
    try:
        
        # 로그인한 사용자의 challenge_level을 가져옴
        user_info = Users.objects.get(user_id=user.user_id)
        challenge_level = user_info.challenge_level
    except Users.DoesNotExist:
        # 사용자가 없을 경우 기본값 설정
        challenge_level = 0

    # 클리어한 레벨이 없을 경우 기본값으로 1단계를 처리
    max_level = challenge_level
    next_level = max_level + 1

    context = {
        'cleared_levels': [challenge_level],
        'max_level': max_level,
        'next_level': next_level,
        'levels': reversed(range(1, 11))  # 1단계와 2단계만 표시 (테스트용)
    }

    return render(request, 'game/challenge/challenge.html', context)


# 전투 상태 초기화 뷰
def Game_battle_reset(request, level):
    user_id = request.user.user_id  # 로그인한 사용자 ID 가져오기

    # 로그인한 사용자의 메인 캐릭터의 체력을 가져오기
    try:
        main_character = Inventory.objects.get(user__user_id=user_id, is_main_character=True)
        player_health = main_character.health  # 메인 캐릭터의 체력
    except Inventory.DoesNotExist:
        player_health = 100  # 메인 캐릭터가 없을 경우 기본 체력 설정

    # 해당 레벨에 맞는 상대방의 체력을 가져오기
    try:
        opponent = Opponent.objects.get(challenge_level=level)
        opponent_health = opponent.health  # 상대방의 체력
    except Opponent.DoesNotExist:
        opponent_health = 150  # 상대방 정보가 없을 경우 기본 체력 설정

    # 전투 상태를 초기화
    request.session['player_hp'] = player_health
    request.session['opponent_hp'] = opponent_health
    request.session['battle_logs'] = []
    request.session['turn_counter'] = 1

    # 초기화 후 해당 레벨의 전투 페이지로 이동
    return redirect('배틀', level=level)


## 일일 미션 페이지
def Daily_Mission(request):
    mission_templates = MissionTemplate.objects.all()
    for template in mission_templates:
        UserMission.objects.get_or_create(user=request.user, mission_template=template)
    missions = UserMission.objects.filter(user=request.user)


    dictionary = {
        'missions' : missions,
    }

    return render(request, 'game/daily_mission/daily_mission.html', dictionary)


## 상점 페이지
@login_required
def Shop(request):
   user_object = request.user
   return render(request, 'game/shop/shop.html', {'user' : user_object})


# 캐릭터 랜덤 뽑기 뷰
@login_required
def draw_character(request):
    characters = Character.objects.all()
    if not characters:
        return redirect('상점')  # 캐릭터가 없으면 상점으로 리다이렉트

    random_character = random.choice(characters)  # 랜덤으로 캐릭터 선택
    user = request.user
    
    # 사용자의 인벤토리 가져오기
    user_inventory = Inventory.objects.filter(user = user)

    # 유저의 코인 확인 후 캐릭터 추가
    cost = 50  # 캐릭터 뽑기 비용 설정 (예: 50 코인)

    # 중복 캐릭터 확인
    if user_inventory.filter(character_name = random_character.name).exists():
        messages.warning(request, "이미 보유한 캐릭터입니다.")  # 중복 캐릭터 알림
        return redirect('상점')

    # 코인 확인
    if user.coins >= cost:
        user.coins -= cost
        user.save()  # 코인 차감 후 저장

        # 인벤토리에 랜덤 캐릭터 추가
        inventory = Inventory(
            user=user,
            character_name=random_character.name,
            level=random_character.level,
            total_experience=0,
            attack_power=random_character.attack_power,
            defense=random_character.defense,
            health=random_character.health,
            is_main_character=False  # 기본적으로 비대표 캐릭터로 추가
        )
        inventory.save()
        
        messages.success(request, f"축하합니다! {random_character.name} 캐릭터를 획득했습니다.")
    else:
        messages.warning(request, "코인이 부족합니다.")

    return redirect('상점')  # 캐릭터를 획득한 후 상점으로 리다이렉트


# 캐릭터 구매 처리 뷰
@login_required
def add_to_inventory(request, character_id):
    character = get_object_or_404(Character, id=character_id)
    user = request.user  # 현재 로그인한 사용자

    # 유저의 인벤토리에서 중복 캐릭터 확인
    character_objects = Inventory.objects.filter(user=user)
    duplicate = character_objects.filter(character_name=character.name).exists()
    
    if duplicate:
        messages.warning(request, "이미 보유한 캐릭터입니다.")  # 중복 캐릭터에 대한 피드백
        return redirect('상점')

    # 유저의 코인 확인 및 구매 처리
    if user.coins >= character.price:
        user.coins -= character.price
        user.save()  # 코인 차감 후 저장

        # 인벤토리에 캐릭터 추가
        inventory = Inventory(
            user=user,
            character_name=character.name, 
            level=character.level, 
            total_experience=0, 
            attack_power=character.attack_power, 
            defense=character.defense, 
            health=character.health, 
            is_main_character=False  # 기본적으로 비대표 캐릭터로 추가
        )
        inventory.save()
        messages.success(request, f"{character.name} 캐릭터를 구매하였습니다.")  # 구매 성공 메시지
    else:
        messages.error(request, "코인이 부족합니다.")  # 코인 부족에 대한 피드백
        return redirect('상점')

    return redirect('캐릭터 선택 페이지')  # 구매 후 인벤토리 페이지로 이동


# 경험치 구매
def Experience_buy(request):
    user_object = request.user
    character_object = Inventory.objects.get(user = request.user, is_main_character = True)

    if user_object.coins >= 500:
        user_object.coins -= 500
        user_object.save()
        character_object.total_experience += 500
        character_object.save()
        messages.info(request, '대표 캐릭터의 경험치가 500 상승하였습니다.')
    else:
        messages.error(request, '코인이 부족합니다.')
    
    return redirect('상점')


# 경험치 이전 페이지
def Exp_Transfer(request):
    
    user_object = Users.objects.get(id = request.user.id)
    
    if user_object.coins >= 1000:
        user_object.coins -= 1000
        user_object.save()
    else:
        messages.error(request, '코인이 부족합니다.')
        return redirect('상점')
    
    main_character = Inventory.objects.get(user = request.user, is_main_character = True)
    other_characters = Inventory.objects.filter(user = request.user, is_main_character = False)

    dictionary = {
        'trigger_before' : request.user,
        'main_character' : main_character,
        'other_characters' : other_characters,
    }

    return render(request, 'game/shop/exp_transfer.html', dictionary)


# 경험치 이전_액션
def Exp_Transfer_Action(request):
    subject_character = Inventory.objects.get(user = request.user, is_main_character = True)

    object_character_id = request.POST.get('input_character_id')
    object_character = Inventory.objects.get(id = object_character_id)

    before_object_character_level = object_character.level
    before_object_character_total_experience = object_character.total_experience
    before_object_character_attack_power = object_character.attack_power
    before_object_character_defense = object_character.defense
    before_object_character_health = object_character.health

    object_character.level = subject_character.level
    object_character.total_experience = subject_character.total_experience
    object_character.attack_power = subject_character.attack_power
    object_character.defense = subject_character.defense
    object_character.health = subject_character.health
    object_character.save()

    subject_character.level = before_object_character_level
    subject_character.total_experience = before_object_character_total_experience
    subject_character.attack_power = before_object_character_attack_power
    subject_character.defense = before_object_character_defense
    subject_character.health = before_object_character_health
    subject_character.save()

    dictionary = {
        'trigger_after' : request.user,
        'subject_character' : subject_character,
        'object_character' : object_character
    }

    return render(request, 'game/shop/exp_transfer.html' , dictionary)


## 캐릭터 변경 페이지
def Character_Change_Page(request):
    character_object = Inventory.objects.filter(user = request.user)
    main_character_object = character_object.filter(is_main_character = True).first()

    dictionary = {
        'characters' : character_object,
        'main_character' : main_character_object
    }

    return render(request, 'game/home/character_change.html', dictionary)


# 대표 캐릭터 설정하기
def Select_Main_Character(request, character_id):
    request_user_characters = Inventory.objects.filter(user = request.user)
    character_object = request_user_characters.get(id = character_id)

    if character_object.is_main_character:
        messages.info = (request, '이미 대표 캐릭터 입니다.')
        return redirect('캐릭터 선택 페이지')
    else:
        request_user_characters.filter(is_main_character = True).update(is_main_character = False)

        character_object.is_main_character = True
        character_object.save()
    
    return redirect('캐릭터 선택 페이지')


## 레벨업 페이지
def Level_Up_Page(request):
    character_object = Inventory.objects.get(user = request.user, is_main_character = True)

    dictionary = {
        'character' : character_object,
        'current_experience' : character_object.total_experience,
        'required_experience' : character_object.level * 100,
        'before_level' : character_object.level,
        'before_health' : character_object.health,
        'before_attack_power' : character_object.attack_power,
        'before_defense' : character_object.defense,
        'after_level' : character_object.level + 1,
        'after_health' : character_object.health + 1,
        'after_attack_power' : character_object.attack_power + 1,
        'after_defense' : character_object.defense + 1,
    }

    return render(request, 'game/home/level_up.html', dictionary)


# 레벨업 하기
def Level_Up_Action(request):
    # 사용자의 인벤토리에서 대표 캐릭터 가져오기
    try:
        character_object = Inventory.objects.get(user=request.user, is_main_character=True)
    except Inventory.DoesNotExist:
        return render(request, 'game/home/level_up.html', {'error': "대표 캐릭터가 없습니다."})

    # 현재 레벨과 총 경험치 가져오기
    current_experience = character_object.total_experience
    current_level = character_object.level
    current_health = character_object.health
    current_attack_power = character_object.attack_power
    current_defense = character_object.defense

    # 레벨업을 위한 필요 경험치 계산
    level_up_occurred = False

    # 경험치가 여러 레벨을 초과할 수 있으므로 반복적으로 확인
    level_up_occurred = current_experience >= (current_level * 100)

    # 레벨업 적용
    if level_up_occurred:
        current_experience -= current_level * 100
        current_level += 1 # 캐릭터의 레벨을 1 증가
        current_health += 1 # 캐릭터의 생명력을 1 증가
        current_attack_power += 1 # 캐릭터의 공격력을 1 증가
        current_defense += 1 # 캐릭터의 방어력을 1 증가
        level_up_occurred = True  # 레벨업이 발생했음을 기록
        messages.success(request,'레벨업이 성공적으로 이루어졌습니다!')
    else:
        messages.error(request,'경험치가 부족합니다')
        return redirect('레벨업 페이지')

    # 캐릭터 정보를 갱신하고 저장
    character_object.total_experience = current_experience
    character_object.level = current_level
    character_object.health = current_health
    character_object.attack_power = current_attack_power
    character_object.defense = current_defense
    character_object.save()

    # 업그레이드 전후의 상태 저장
    dictionary = {
        'character': character_object,
        'current_experience' : current_experience,
        'required_experience' : character_object.level * 100,
        'before_level': current_level,
        'after_level': current_level + 1,
        'before_health': current_health,
        'after_health': current_health + 10,
        'before_attack_power': current_attack_power,
        'after_attack_power': current_attack_power + 1,
        'before_defense': current_defense,
        'after_defense': current_defense + 1,
        'level_up_occurred': level_up_occurred,
    }

    return render(request, 'game/home/level_up.html', dictionary)




experience_multiplier = 1

def exp_auto():
    # 모든 사용자에 대해 처리
    users = Users.objects.all()
    for user in users:
        try:
            # 사용자의 대표 캐릭터 가져오기
            character_object = Inventory.objects.get(user=user, is_main_character=True)
            energy_count = user.energy_1 + user.energy_2 + user.energy_3 + user.energy_4
            # 사용자별 경험치 계산 로직 (user.energy_count에 따라 조정)
            if energy_count == 1:
                experience = 10
            elif energy_count == 2:
                experience = 20
            elif energy_count == 3:
                experience = 30
            elif energy_count == 4:
                experience = 40
            else:
                experience = 0  # 기본 경험치

            # 배율 적용 후 경험치 추가
            character_object.total_experience += experience * experience_multiplier
            character_object.save()
            # 절약한 전력량 추가
            energy_history_object = EnergyHistory.objects.get(user = user)
            energy_history_object.savings += experience * 0.001
            energy_history_object.save()

            
             

            # print(f"[{timezone.now()}] {user.user_id}의 대표 캐릭터에게 경험치 {experience * experience_multiplier}이 추가되었습니다.")
        
        except Inventory.DoesNotExist:
            print(f"{user.user_id}에게 대표 캐릭터가 없습니다.")
    
    # print(f"[{timezone.now()}] exp_auto 함수가 실행되었습니다.")

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(exp_auto, 'interval', seconds=60)
    scheduler.start()
    # print(f"[{timezone.now()}] 스케줄러가 시작되었습니다.")



def Energy_Saving_Page(request):
    energy_savings_object = EnergyHistory.objects.get(user=request.user).savings

    # 그래프 생성 (절약량을 기반으로)
    generate_graph(energy_savings_object)

    saved_pees = energy_savings_object * 200

    return render(request, 'game/home/energy_saving.html', {
        'savings': energy_savings_object,
        'graph_url': '/media/savings_graph1.jpg',  # 올바른 이미지 URL
        'saved_pees': saved_pees
    })


# 에너지 절약하기
def Energy_Saving_Action(request, number):
    user_object = request.user
    current_time = timezone.now()

    # EnergyHistory 가져오기
    energy_history = EnergyHistory.objects.get(user=user_object)

    main_character_object = Inventory.objects.filter(user = user_object, is_main_character = True).first()
    # 획득한 경험치
    main_character_object.gain_exp = main_character_object.total_experience - main_character_object.experience_start
    main_character_object.experience_start = main_character_object.total_experience
    main_character_object.save()

    energy_history_objects = LastestEnergyHistory.objects.filter(user = request.user).order_by('-end_time')
    time_object = energy_history_objects[0]

    # 에너지 기록 추가 (상태 업데이트 전)
    LastestEnergyHistory.objects.create(
        user=user_object,
        start_time=time_object.end_time,
        end_time=current_time,  # 현재 시간 기록
        exp=energy_history.exp,  # 현재 경험치량을 기록
        energy_1=user_object.energy_1,
        energy_2=user_object.energy_2,
        energy_3=user_object.energy_3,
        energy_4=user_object.energy_4,
        gain_exp=main_character_object.gain_exp,
    )

    # 에너지 상태 업데이트
    if number == 1:
        user_object.energy_1 = 1
    elif number == 2:
        user_object.energy_2 = 1
    elif number == 3:
        user_object.energy_3 = 1
    elif number == 4:
        user_object.energy_4 = 1

    user_object.save()  # 변경 사항 저장

    # EnergyHistory 업데이트
    energy_history.date = current_time
    energy_history.amount += 1
    energy_history.exp += 10
    energy_history.save()

    dictionary = {
        'user': user_object,
    }

    return redirect('게임_메인')


def Energy_Saving_Action_Off(request, number):
    user_object = request.user
    current_time = timezone.now()

    # EnergyHistory 가져오기
    energy_history = EnergyHistory.objects.get(user=user_object)

    main_character_object = Inventory.objects.filter(user = user_object, is_main_character = True).first()
    # 획득한 경험치
    main_character_object.gain_exp = main_character_object.total_experience - main_character_object.experience_start
    main_character_object.experience_start = main_character_object.total_experience
    main_character_object.save()

    energy_history_objects = LastestEnergyHistory.objects.filter(user = request.user).order_by('-end_time')
    time_object = energy_history_objects[0]

    # 에너지 기록 추가 (상태 업데이트 전)
    LastestEnergyHistory.objects.create(
        user=user_object,
        start_time=time_object.end_time,
        end_time=current_time,  # 현재 시간 기록
        exp=energy_history.exp,  # 현재 경험치량을 기록
        energy_1=user_object.energy_1,
        energy_2=user_object.energy_2,
        energy_3=user_object.energy_3,
        energy_4=user_object.energy_4,
        gain_exp=main_character_object.gain_exp,
    )

    # 에너지 상태 업데이트
    if number == 1:
        user_object.energy_1 = 0
    elif number == 2:
        user_object.energy_2 = 0
    elif number == 3:
        user_object.energy_3 = 0
    elif number == 4:
        user_object.energy_4 = 0

    user_object.save()  # 변경 사항 저장

    # EnergyHistory 업데이트
    energy_history.date = current_time
    energy_history.amount = max(0, energy_history.amount - 1)  # 최소 0으로 유지
    energy_history.exp = max(0, energy_history.exp - 10)  # 최소 0으로 유지
    energy_history.save()

    dictionary = {
        'user': user_object,
    }

    return redirect('게임_메인')



def generate_graph(savings):
    monthly_consumption = 350  # 이번 달 전력 사용량 (예시값)

    # 절약모드 사용 시 전력 사용량
    savings_with_mode = max(0, monthly_consumption - savings)  # 음수가 되지 않도록 처리

    # 데이터 준비
    labels = ['Energy Saving Mode', 'Without Energy Saving Mode']
    values = [savings_with_mode, monthly_consumption]

    # 그래프 그리기
    plt.figure(figsize=(6, 4))
    bars = plt.bar(labels, values, color=['lightblue', 'salmon'])
    
    # y축 레이블, 제목, y축 범위 설정
    plt.ylabel('Electricity Usage (kWh)')
    plt.title('Electricity Usage Comparison with Energy Saving Mode')
    plt.ylim(0, max(values) + 50)  # 최대값에 따라 y축 범위 조정

    # 기준선 추가
    # plt.axhline(y=monthly_consumption, color='gray', linestyle='--', label='Monthly Consumption')
    # plt.legend()
    # plt.grid(axis='y')

    # 바 위에 값 표시
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval:.1f} kWh', ha='center', va='bottom')

    # 이미지 저장 (상대 경로로)
    image_path = os.path.join(settings.MEDIA_ROOT, 'savings_graph1.jpg')  # 상대 경로
    try:
        plt.savefig(image_path, format='jpg')  # JPG 형식으로 저장
    except Exception as e:
        print(f"Error saving graph: {e}")

    plt.close()  # 그래프 닫기
    print(f"Graph image successfully saved at {image_path}.")  # 디버깅을 위한 로그


## 퀴즈 페이지
def Quiz(request):
    
    quizzes = EnergySavingQuiz.objects.all()
    
    if request.method == "POST":
        # POST 요청이 있을 경우 새로운 퀴즈 선택
        selected_quiz = random.choice(quizzes) if quizzes else None
    else:
        # GET 요청 시 랜덤 퀴즈 선택
        selected_quiz = random.choice(quizzes) if quizzes else None

    return render(request, 'game/home/quiz.html', {'quiz': selected_quiz})


# 퀴즈 room_1
def Quiz_Room_1(request):
    trigger_1 = request.user

    quizzes = EnergySavingQuiz.objects.all()
    
    if request.method == "POST":
        # POST 요청이 있을 경우 새로운 퀴즈 선택
        selected_quiz = random.choice(quizzes) if quizzes else None
    else:
        # GET 요청 시 랜덤 퀴즈 선택
        selected_quiz = random.choice(quizzes) if quizzes else None
    
    dictionary = {
        'trigger_1' : trigger_1,
        'quiz': selected_quiz
    }

    return render(request, 'game/home/quiz_room.html', dictionary )


# 퀴즈 room_2
def Quiz_Room_2(request):
    trigger_2 = request.user

    quizzes = EnergySavingQuiz.objects.all()
    
    if request.method == "POST":
        # POST 요청이 있을 경우 새로운 퀴즈 선택
        selected_quiz = random.choice(quizzes) if quizzes else None
    else:
        # GET 요청 시 랜덤 퀴즈 선택
        selected_quiz = random.choice(quizzes) if quizzes else None
    
    dictionary = {
        'trigger_2' : trigger_2,
        'quiz': selected_quiz
    }

    return render(request, 'game/home/quiz_room.html', dictionary )


# 퀴즈 room_3
def Quiz_Room_3(request):
    trigger_3 = request.user

    quizzes = EnergySavingQuiz.objects.all()
    
    if request.method == "POST":
        # POST 요청이 있을 경우 새로운 퀴즈 선택
        selected_quiz = random.choice(quizzes) if quizzes else None
    else:
        # GET 요청 시 랜덤 퀴즈 선택
        selected_quiz = random.choice(quizzes) if quizzes else None
    
    dictionary = {
        'trigger_3' : trigger_3,
        'quiz': selected_quiz
    }

    return render(request, 'game/home/quiz_room.html', dictionary )


# 퀴즈 정답 확인
def Check_Answer(request,quiz_id):
    var_answer = request.POST.get('answer')
    quiz_object = EnergySavingQuiz.objects.get(id = quiz_id)
    character_object = Inventory.objects.get(user = request.user, is_main_character = True)
    daily_mission_object = DailyMission.objects.get(user = request.user)
    current_time = timezone.now().date()

    if var_answer == quiz_object.answer:
        character_object.total_experience += 500
        character_object.save()
        daily_mission_object.clear_count += 1
        daily_mission_object.last_clear_date = current_time
        daily_mission_object.save()
        messages.success(request, '정답입니다! 경험치 500획득 오늘의 일일 미션을 완료하였습니다.')
    else:
        messages.error(request, f'틀렸습니다.')
        return redirect('퀴즈 페이지')

    return redirect('게임_메인')



#윤창현
# 고정된 미션 목록
from .forms import MissionImageForm
from ultralytics import YOLO
import os


MISSION_CHOICES = [
    ('plug_off', '안 쓰는 콘센트 뽑기'),
    ('light_off', '사용 안 하는 전등 끄기'),
]

# 미션 목록을 보여주는 뷰 (모든 사용자가 같은 미션 목록)
@login_required
def assign_missions(request):
    # 모든 사용자에게 고정된 미션을 할당
    mission_templates = MissionTemplate.objects.all()
    for template in mission_templates:
        UserMission.objects.get_or_create(user=request.user, mission_template=template)
    
    return redirect('일일 미션 페이지')


# @login_required
# def mission_list(request):
#     # 현재 로그인한 사용자의 미션 목록을 가져옴
#     missions = UserMission.objects.filter(user=request.user)
#     return render(request, 'game/daily_mission/daily_mission.html', {'missions': missions})


@login_required
def perform_mission(request, mission_id):
    mission = get_object_or_404(UserMission, id=mission_id, user=request.user)
    form = MissionImageForm(request.POST or None, request.FILES or None)
    result_image_path_before = None
    result_image_path_after = None
    num_plug_off_before = 0
    num_light_off_before = 0
    num_plug_off_after = 0
    num_light_off_after = 0

    if request.method == 'POST' and form.is_valid():
        # 업로드된 '이전' 사진 저장
        before_image = form.cleaned_data['before_image']
        before_image_path = os.path.join('media', 'uploaded_images', before_image.name)
        with open(before_image_path, 'wb+') as destination:
            for chunk in before_image.chunks():
                destination.write(chunk)

        # 업로드된 '이후' 사진 저장
        after_image = form.cleaned_data['after_image']
        after_image_path = os.path.join('media', 'uploaded_images', after_image.name)
        with open(after_image_path, 'wb+') as destination:
            for chunk in after_image.chunks():
                destination.write(chunk)

        # YOLO 모델로 '이전' 사진 분석
        if mission.mission_template.mission_type == 'plug_off':
            # plug_model = YOLO(r"C:/Users/user/Desktop/1014_노광우/Team_3E/runs/detect/multi_tab_model/weights/best.pt")
            plug_model = YOLO(r"./Team_3E/runs/detect/multi_tab_model/weights/best.pt")
            results_before = plug_model(before_image_path)
            num_plug_off_before = len([det for det in results_before[0].boxes if int(det.cls.item()) == 0])

            results_after = plug_model(after_image_path)
            num_plug_off_after = len([det for det in results_after[0].boxes if int(det.cls.item()) == 0])
        elif mission.mission_template.mission_type == 'light_off':
            # light_model = YOLO(r"C:/Users/user/Desktop/1014_노광우/Team_3E/runs/detect/light_switch_model/weights/best.pt")
            light_model = YOLO(r"./Team_3E/runs/detect/light_switch_model/weights/best.pt")
            results_before = light_model(before_image_path)
            num_light_off_before = len([det for det in results_before[0].boxes if int(det.cls.item()) == 1])

            results_after = light_model(after_image_path)
            num_light_off_after = len([det for det in results_after[0].boxes if int(det.cls.item()) == 1])

        # 결과 이미지 저장
        result_image_path_before = os.path.join('media', 'result_images', 'result_before_' + before_image.name)
        result_image_path_after = os.path.join('media', 'result_images', 'result_after_' + after_image.name)
        results_before[0].save(result_image_path_before)
        results_after[0].save(result_image_path_after)

    return render(request, 'game/daily_mission/perform_mission.html', {
        'mission': mission,
        'form': form,
        'result_image_path_before': result_image_path_before,
        'result_image_path_after': result_image_path_after,
        'num_plug_off_before': num_plug_off_before,
        'num_light_off_before': num_light_off_before,
        'num_plug_off_after': num_plug_off_after,
        'num_light_off_after': num_light_off_after,
    })




@login_required
def complete_mission(request, mission_id):
    mission = get_object_or_404(UserMission, id=mission_id, user=request.user)
    mission.is_completed = True  # 미션 완료 처리
    mission.save()

    return redirect('일일 미션 페이지')  # 미션 목록으로 리다이렉트


@login_required
def mission_result(request, mission_id, num_plug_off, num_light_off, result_image_path):
    mission = get_object_or_404(UserMission, id=mission_id, user=request.user)
    return render(request, 'game/daily_mission/mission_result.html', {
        'mission': mission,
        'num_plug_off': num_plug_off,
        'num_light_off': num_light_off,
        'result_image_path': result_image_path,
    })


@login_required
def complete_mission(request, mission_id):
    mission = get_object_or_404(UserMission, id=mission_id, user=request.user)
    mission.is_completed = True  # 미션 완료 처리
    mission.save()

    # 사용자의 모든 미션이 완료되었는지 확인
    all_missions = UserMission.objects.filter(user=request.user)
    if all(mission.is_completed for mission in all_missions):
        # 오늘 날짜를 기록 (모든 미션 완료 시)
        DailyMissionCompletion.objects.get_or_create(
            user=request.user,
            completion_date=timezone.now().date()
        )

    return redirect('일일 미션 페이지')  # 미션 목록으로 리다이렉트


@login_required
def mission_completion_dates(request):
    completions = DailyMissionCompletion.objects.filter(user=request.user)
    return render(request, 'game/daily_mission/completion_dates.html', {'completions': completions})