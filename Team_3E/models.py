from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class UsersManager(BaseUserManager):
    def create_user(self, user_id, password=None, **extra_fields):
        """사용자 생성 메서드"""
        if not user_id:
            raise ValueError("The User ID must be set")
        user = self.model(user_id=user_id, **extra_fields)  # 수정: *ㄹ* → **extra_fields
        user.set_password(password)  # 비밀번호 해시화
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, password=None, **extra_fields):
        """관리자 사용자 생성 메서드"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(user_id, password, **extra_fields)


class Users(AbstractBaseUser):
    user_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=200)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    coins = models.IntegerField(default=100)  # 기본 코인
    energy_count = models.IntegerField(default=0)
    challenge_level = models.IntegerField(default=0)  # 도전한 레벨 (새로 추가)
    coin = models.IntegerField(default=0)  # 추가된 coin 필드
    energy_1 = models.IntegerField(default=0)
    energy_2 = models.IntegerField(default=0)
    energy_3 = models.IntegerField(default=0)
    energy_4 = models.IntegerField(default=0)

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['name', 'email']

    objects = UsersManager()  # 사용자 매니저 설정


class Character(models.Model):
    name = models.CharField(max_length=100)  # 캐릭터 이름
    description = models.TextField(null=True, blank=True)  # 캐릭터 설명 (null 및 blank 허용)
    level = models.IntegerField(default=1)  # 캐릭터 기본 레벨
    attack_power = models.IntegerField(default=10)  # 캐릭터 공격력
    defense = models.IntegerField(default=0)  # 캐릭터 방어력
    health = models.IntegerField(default=100)  # 캐릭터 체력
    image = models.ImageField(upload_to='character_images/', null=True, blank=True)  # 캐릭터 이미지
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 캐릭터 가격

    def __str__(self):
        return self.name


class Friendship(models.Model):
    connected_user = models.ForeignKey(Users, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(Users, related_name='friend_of', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted')])


# Inventory 모델: 사용자가 구매한 캐릭터를 보관
class Inventory(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)  # 캐릭터의 주인 (유저)
    character_name = models.CharField(max_length=100)  # 구매한 캐릭터 이름
    level = models.IntegerField(default=1)  # 인벤토리 내 캐릭터의 현재 레벨
    total_experience = models.IntegerField(default=0)  # 총 경험치 (카테고리별 경험치의 합계)
    attack_power = models.IntegerField()  # 캐릭터의 현재 공격력
    defense = models.IntegerField()  # 캐릭터의 현재 방어력
    health = models.IntegerField()  # 캐릭터의 현재 체력
    is_main_character = models.BooleanField(default=False)  # 대표 캐릭터 여부
    experience_start = models.IntegerField(default=0)
    gain_exp = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.is_main_character:
            # 이 유저의 기존 대표 캐릭터의 is_main_character를 False로 설정
            Inventory.objects.filter(user=self.user, is_main_character=True).update(is_main_character=False)
        
        # 현재 캐릭터를 대표 캐릭터로 저장
        super().save(*args, **kwargs)


class Opponent(models.Model):
    name = models.CharField(max_length=100)  # 상대 이름
    challenge_level = models.IntegerField(default=1)  # 상대의 도전 레벨
    attack_power = models.IntegerField()  # 상대의 공격력
    defense = models.IntegerField()  # 상대의 방어력
    health = models.IntegerField()  # 상대의 체력
    coin = models.IntegerField(default=0)  # 추가된 coin 필드


class EnergyHistory(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    exp = models.IntegerField()
    savings = models.IntegerField()
    start_time = models.DateTimeField(auto_now_add=True)



class LastestEnergyHistory(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)  # 자동으로 생성된 시간 기록
    energy_1 = models.IntegerField(default=0)
    energy_2 = models.IntegerField(default=0)
    energy_3 = models.IntegerField(default=0)
    energy_4 = models.IntegerField(default=0)
    exp = models.IntegerField()  # 경험치량
    gain_exp = models.IntegerField()
    start_time = models.DateTimeField(null=True, blank=True)  # 수동으로 설정 가능하도록 변경
    end_time = models.DateTimeField(null=True, blank=True)    # 수동으로 설정 가능하도록 변경


class DailyMission(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)  # 외래키로 User 모델과 연결
    clear_count = models.IntegerField(default=0)  # 미션 클리어 시 카운트 획득
    daily_count = models.IntegerField(default=0)  # 하루가 시작되면 증가하는 카운트
    last_clear_date = models.DateField(null=True, blank=True)  # 마지막 클리어 날짜

    def __str__(self):
        return f"{self.user.username}'s Daily Mission Status"

    def increment_daily_count(self):
        """하루가 시작될 때 호출하여 daily_count를 증가시킵니다."""
        self.daily_count += 1
        self.save()
    

class EnergySavingQuiz(models.Model):
    question = models.CharField(max_length=255)  # 질문 텍스트
    option_a = models.CharField(max_length=100)  # 선택지 A
    option_b = models.CharField(max_length=100)  # 선택지 B
    option_c = models.CharField(max_length=100)  # 선택지 C
    option_d = models.CharField(max_length=100)  # 선택지 D
    answer = models.CharField(max_length=1)  # 정답 (A, B, C, D)


#윤창현
class MissionTemplate(models.Model):
    MISSION_CHOICES = (
        ('plug_off', '안 쓰는 콘센트 뽑기'),
        ('light_off', '사용 안 하는 전등 끄기'),
    )
    mission_type = models.CharField(max_length=50, choices=MISSION_CHOICES, unique=True)
    description = models.TextField()  # 미션 설명

    def __str__(self):
        return self.get_mission_type_display()


# 사용자가 할당받은 미션을 관리하는 모델
class UserMission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 로그인한 사용자와 연결
    mission_template = models.ForeignKey(MissionTemplate, on_delete=models.CASCADE)  # 고정된 미션과 연결
    is_completed = models.BooleanField(default=False)  # 미션 완료 여부
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.user_id} - {self.mission_template.get_mission_type_display()} (완료: {self.is_completed})"
    


class DailyMissionCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    completion_date = models.DateField(default=timezone.now)  # 미션 완료 날짜 기록

    def __str__(self):
        return f"{self.user} - {self.completion_date}"

