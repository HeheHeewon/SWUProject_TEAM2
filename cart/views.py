from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Product # Product는 임시 모델

# 장바구니 상세 보기 뷰 (로그인 필요)
@login_required
def cart_detail(request):
    # 로그인한 사용자의 장바구니를 가져오거나 없으면 생성
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # 장바구니에 담긴 아이템 목록 가져오기
    cart_items = cart.items.all() 
    
    # 총 합계 계산 (간단 예시)
    total_price = sum(item.total_price for item in cart_items)

    return render(request, 'cart/cart_detail.html', {
        'cart': cart, 
        'cart_items': cart_items, 
        'total_price': total_price
    })

# 장바구니에 상품 추가 뷰
@login_required
def cart_add(request, product_id):
    # 실제 프로젝트의 Product 모델 사용
    product = get_object_or_404(Product, id=product_id) 
    
    # 사용자 장바구니 가져오기
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # 이미 장바구니에 있는 상품인지 확인
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        defaults={'quantity': 1}
    )
    
    if not item_created:
        # 이미 있다면 수량 1 증가
        cart_item.quantity += 1
        cart_item.save()
        
    return redirect('cart:cart_detail') # 장바구니 목록으로 리다이렉트

# 장바구니에서 상품 제거 뷰
@login_required
def cart_remove(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    
    # 해당 상품 아이템 찾기
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    
    # 아이템 삭제
    cart_item.delete()
        
    return redirect('cart:cart_detail')