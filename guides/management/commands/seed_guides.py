# guides/management/commands/seed_guides.py
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from guides.models import Guide, GuideStep

User = get_user_model()

BASE_DIR = Path(__file__).resolve().parents[3]
SEED_THUMB_DIR = BASE_DIR / "static" / "img" / "guides"

GUIDE_FIXTURES = [
    {
        "nickname": "커피를 좋아하는 이씨",   # ← 실제 가입한 닉네임과 똑같이
        "title": "커피방향제 DIY",
        "summary": "집에서 간단히 만드는 커피방향제",
        "steps": [
            {
                "title": "재료준비",
                "note": "커피박과 굵은소금, 에센셜 오일, 거름망 또는 작은 주머니 등을 준비합니다.",
            },
            {
                "title": "과정 1",
                "note": "완전히 건조한 커피박에 굵은소금을 섞고, 좋아하는 향의 에센셜 오일을 몇 방울 떨어뜨립니다.",
            },
            {
                "title": "과정 2",
                "note": "골고루 섞은 혼합물을 거름망이나 작은 천 주머니에 담아 모양을 잡아줍니다.",
            },
            {
                "title": "결과",
                "note": "신발장·옷장·화장실 등에 걸어두면 은은한 커피향과 함께 탈취 효과를 얻을 수 있습니다.",
            },
        ],
        "thumb": "coffee4.png",
    },
    {
        "nickname": "동네카페 사장 최씨",
        "title": "무료 커피비료 만들기",
        "summary": "남은 커피박으로 만드는 친환경 비료",
        "steps": [
            {
                "title": "재료준비",
                "note": "커피박과 마른 낙엽, 배양토, 물뿌리개를 준비합니다. 곰팡이가 핀 커피박은 사용하지 않습니다.",
            },
            {
                "title": "혼합",
                "note": "커피박과 낙엽, 배양토를 1:2:2 비율로 섞어 통기성이 좋게 가볍게 뒤섞어 줍니다.",
            },
            {
                "title": "건조",
                "note": "통풍이 잘 되는 그늘에서 1~2주 정도 말리며, 중간중간 뒤집어 골고루 건조시킵니다.",
            },
            {
                "title": "완성",
                "note": "완전히 마르면 화분 흙과 섞거나 상단에 얇게 뿌려 서서히 분해되는 비료로 사용합니다.",
            },
        ],
        "thumb": "coffee3.png",
    },
    {
        "nickname": "실험하는 김연구원",
        "title": "냉장고 냄새 제거 비법",
        "summary": "커피박으로 만드는 탈취 팁",
        "steps": [
            {
                "title": "재료준비",
                "note": "건조한 커피박과 얕은 접시 또는 작은 용기, 키친타월 한 장을 준비합니다.",
            },
            {
                "title": "포장",
                "note": "용기 바닥에 키친타월을 깔고 그 위에 커피박을 고루 펴서 1~2cm 두께로 올립니다.",
            },
            {
                "title": "배치",
                "note": "냉장고 선반 한쪽에 두거나, 작은 용기에 나누어 칸마다 배치하면 효과가 더 좋아집니다.",
            },
            {
                "title": "교체주기",
                "note": "커피향이 약해지거나 습기를 머금었을 때 2~3주 간격으로 새 커피박으로 교체합니다.",
            },
        ],
        "thumb": "coffee2.png",
    },
    {
        "nickname": "농사하는 박씨",
        "title": "원예용 커피박 활용 BEST",
        "summary": "분갈이/퇴비 활용 노하우",
        "steps": [
            {
                "title": "재료준비",
                "note": "완전히 건조한 커피박과 배양토·마사토(또는 펄라이트)를 깨끗한 용기에 준비합니다.",
            },
            {
                "title": "혼합비율",
                "note": "커피박:배양토:마사토(또는 펄라이트)를 1:3:1 비율로 섞어 통기성과 배수를 맞춰 줍니다.",
            },
            {
                "title": "적용",
                "note": "화분의 배수층 위에 혼합한 흙을 채우고 뿌리 주변을 가볍게 눌러 분갈이 혹은 퇴비로 사용합니다.",
            },
            {
                "title": "관리",
                "note": "과습을 피하고 2~3개월 간격으로 소량씩 커피박 혼합흙을 보충해 주며 상태를 점검합니다.",
            },
        ],
        "thumb": "coffee1.png",
    },
]

class Command(BaseCommand):
    help = "Demo guides + steps seeder (idempotent)"

    def handle(self, *args, **options):
        created_guides = 0

        for idx, item in enumerate(GUIDE_FIXTURES, start=1):
            nickname = item["nickname"]

            # 1) 닉네임으로 먼저 찾고, 없으면 새로 만든다
            user, _ = User.objects.get_or_create(
                nickname=nickname,
                defaults={
                    "username": f"guide_{slugify(nickname) or idx}",
                    "email": f"guide{idx}@example.com",
                },
            )

            # 2) Guide 생성/획득
            guide, was_created = Guide.objects.get_or_create(
                author=user,
                title=item["title"],
                defaults={
                    "summary": item["summary"],
                    "is_published": True,
                },
            )

            # 3) 썸네일 설정
            thumb_name = item.get("thumb")
            if thumb_name:
                thumb_path = SEED_THUMB_DIR / thumb_name
                if thumb_path.exists() and (was_created or not guide.thumbnail):
                    with thumb_path.open("rb") as f:
                        guide.thumbnail.save(thumb_name, File(f), save=True)

            # 4) 기존 단계 리셋 후 다시 채우기
            guide.steps.all().delete()
            for order, step in enumerate(item["steps"], start=1):
                if isinstance(step, str):
                    title = step
                    note = ""
                else:
                    title = step.get("title", "")
                    note = step.get("note", "")

                GuideStep.objects.create(
                    guide=guide,
                    order=order,
                    title=title,
                    icon=str(order),
                    note=note,
                )

            created_guides += int(was_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete. guides_created={created_guides}, "
                f"total_guides={Guide.objects.count()}"
            )
        )
