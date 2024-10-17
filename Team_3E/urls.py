from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    
    ## Basic

    # 홈페이지
    path('',                                  views.Home,                        name='홈페이지'),
    
    # 회원
    path('find_id/',                          views.Find_Id,                     name='아이디 찾기'),
    path('find_pw/',                          views.Find_Pw,                     name='비밀번호 찾기'),
    path('find_info/',                        views.Find_Info,                   name='회원정보_찾기'),
    path('register/',                         views.Register,                    name='회원가입'),
    path('register_action/',                  views.Register_Action,             name='회원가입_액션'),
    path('login/',                            views.Login,                       name='로그인'),
    path('login_action/',                     views.Login_Action,                name='로그인_액션'),
    path('logout/',                           views.Logout,                      name='로그아웃'),
   

    ## 마이페이지
    path('mypage/',                           views.Mypage,                      name='마이페이지'),
    # 회원정보 수정
    path('mypage_edit_info/',                 views.Mypage_Edit_Info,            name='회원정보수정 페이지'),
    # 에너지 절약량 확인
    path('mypage_energy_savings/',            views.Mypage_Energy_Savings,       name='에너지 절약량 확인페이지'),
    # 일일 미션 출석부
    path('mypage_attendance_register/',       views.Mypage_Attendance_Resister,  name='일일 미션 출석부 페이지'),


    path('mypage/info/edit/',                 views.Mypage_info_edit,            name='회원정보수정'),
    path('mypage/delete_user/',               views.Delete_User,                 name='회원탈퇴'),
    

    ### 게임

    ## 메인 페이지
    path('game_main/',                        views.Game_Main,               name='게임_메인'),


    ## 랭킹 페이지
    path('rangking/',                           views.Rangking,              name='랭킹'),
    # 도전랭킹
    path('challenge/rangking/',                 views.Challenge_Rangking,    name='도전랭킹'),
    # 랭킹_방문하기
    path('rangking_visit/<int:character_id>/', views.Rangking_Visit,       name='랭킹_방문하기'),
    # 도전랭킹_방문하기
    path('challenge_rangking_visit/<int:user_id>/', views.Challenge_Rangking_Visit, name='도전랭킹_방문하기'),
    # 랭킹_친구추가
    # path('rangking_friend_request/', views.Rangking_Friend_Request, name='랭킹_친구 신청'),



    ## 친구 페이지
    path('friend/',                         views.Friend,           name='친구'),
    # 친구_방문하기
    path('friend_visit/<int:friend_id>/',   views.Friend_Visit,     name='방문하기'),
    # 친구_유저 검색 칸
    path('friend_search/',                  views.Friend_Search,    name='유저 검색 칸'),
    # 친구_유저 검색
    path('search_user/',                         views.Search_User,           name='유저 검색'),
    # 친구 신청하기
    path('add_friend_request/<int:user_id>/',    views.Add_Friend_Request,    name='친구 신청'),
    # 친구 신청 수락하기
    path('add_friend_accept/<int:connected_user_id>/', views.Add_Friend_Accept, name='친구 수락'),
    # 친구 신청 거절하기
    path('add_friend_refuse/<int:connected_user_id>/', views.Add_Friend_Refuse, name='친구 거절'),
    # 친구 삭제하기
    path('delete_friend/<int:user_id>/',         views.Delete_Friend,         name='친구 삭제'),
    # 친구에게 도전하기
    path('challenge_friend/<int:friend_id>',     views.Challenge_Friend,      name='친구에게 도전'),
    # 친구_배틀 초기화
    path('challenge_friend_reset/<int:friend_character_id>', views.Challenge_Friend_Reset, name='친구에게 도전_초기화'),



    ## 도전 페이지
    path('challenge/',                       views.Challenge,                name='도전'),
    # 배틀
    path('challenge_battle/<int:level>/',    views.Challenge_battle,         name='배틀'),
    # 배틀 초기화
    path('game_battle_reset/<int:level>/',   views.Game_battle_reset,        name='배틀_초기화'),


    ## 일일 미션 페이지
    path('daily_mission/',   views.Daily_Mission,        name='일일 미션 페이지'),


    ## 상점 페이지
    path('shop/',                            views.Shop,                     name='상점'),
    # 캐릭터 뽑기
    path('shop/draw/', views.draw_character, name='캐릭터_뽑기'),
    # 캐릭터 구매
    path('shop/buy/<int:character_id>/', views.add_to_inventory, name='캐릭터_구매'),
    # 경험치 구매
    path('shop/experience_buy/', views.Experience_buy, name = '경험치 구매'),
    # 경험치 이전 페이지
    path('shop/exp_transfer/', views.Exp_Transfer, name = '경험치 이전 페이지'),
    # 경험치 이전_액션
    path('shop/exp_transfer_action/', views.Exp_Transfer_Action, name = '경험치 이전_액션'),


    ## 캐릭터 변경 페이지
    path('character_change/',                         views.Character_Change_Page,    name='캐릭터 선택 페이지'),
    # 대표 캐릭터 설정하기
    path('select_main_character/<int:character_id>',  views.Select_Main_Character,    name='대표 캐릭터 설정'),


    ## 레벨업 페이지
    path('level_up/',                        views.Level_Up_Page,                name='레벨업 페이지'),
    # 레벨업 하기
    path('level_up_action/',                 views.Level_Up_Action,              name='레벨업 하기'),
    

    ## 에너지 절약 페이지
    path('energy_saving/',                   views.Energy_Saving_Page,       name='에너지 절약 페이지'),
    # 에너지 절약하기
    path('energy_saving_action/<int:number>/',            views.Energy_Saving_Action,     name='에너지 절약하기'),
    # 에너지 절약하기(off)
    path('energy_saving_action_off/<int:number>/',        views.Energy_Saving_Action_Off, name='에너지 절약하기_끄기'),


    ## 퀴즈 페이지
    path('quiz/', views.Quiz, name='퀴즈 페이지'),
    # 퀴즈 1 페이지
    path('quiz_room_1/', views.Quiz_Room_1, name='퀴즈 페이지_1'),
    # 퀴즈 2 페이지
    path('quiz_room_2/', views.Quiz_Room_2, name='퀴즈 페이지_2'),
    # 퀴즈 3 페이지
    path('quiz_room_3/', views.Quiz_Room_3, name='퀴즈 페이지_3'),
    # 퀴즈 정답 확인
    path('check_answer/<int:quiz_id>', views.Check_Answer, name='정답 확인'),



    #1009윤창현
    path('missions/assign/', views.assign_missions, name='assign_missions'),
    
    # 미션 수행
    path('missions/<int:mission_id>/perform/', views.perform_mission, name='perform_mission'),
    
    # 미션 완료 (사진 업로드 후 결과 확인)
    path('missions/<int:mission_id>/result/<int:num_plug_off>/<int:num_light_off>/<str:result_image_path>/',views.mission_result, name='mission_result'),
    
    path('missions/<int:mission_id>/complete/', views.complete_mission, name='complete_mission'),  # 미션 완료 경로

    path('missions/completions/', views.mission_completion_dates, name='mission_completion_dates'),
    


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)