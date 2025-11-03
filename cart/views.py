from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import Cart, CartItem
from posts.models import Post   # ★ 담아둘 대상은 Post

# 장바구니 상세 보기
@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("post").all()

    # (선택) 유료 글 합계
    total_price = sum(
        (it.post.price or 0)
        for it in items
        if it.post.price_type == "유료"
    )

    return render(request, "cart/cart_detail.html", {
        "cart": cart,
        "cart_items": items,
        "total_price": total_price,
    })

# 담기
@login_required
def cart_add(request, post_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    post = get_object_or_404(Post, id=post_id)
    CartItem.objects.get_or_create(cart=cart, post=post)
    return redirect("cart:cart_detail")

# 제거
@login_required
def cart_remove(request, post_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    CartItem.objects.filter(cart=cart, post_id=post_id).delete()
    return redirect("cart:cart_detail")
