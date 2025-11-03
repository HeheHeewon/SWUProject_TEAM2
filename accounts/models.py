from django.db import models
from django.contrib.auth.models import User

# 사용자의 추가 정보를 저장하는 Profile 모델
class Profile(models.Model):
    # User 모델과 1:1로 연결 (User 삭제 시 Profile도 삭제)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # 마이페이지에서 관리할 수 있는 추가 필드
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    
    # 커피찌꺼기 순환 서비스와 관련된 필드 (예: 누적 거래 횟수)
    total_transactions = models.IntegerField(default=0) 

    def __str__(self):
        return f'{self.user.username} Profile'

