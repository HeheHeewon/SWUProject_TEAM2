from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import Cart, CartItem
from posts.models import Post   # ★ 담아둘 대상은 Post

# 장바구니 상세 보기
@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("post").all()

    # 유료 합계 (공급글만, 유료만)
    total_price = 0
    for it in items:
        p = it.post
        if p.type == Post.Type.SUPPLY and p.price_type == Post.PriceType.PAID:
            total_price += (p.price or 0)

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

    # 내 글 담기 방지
    if post.author_id == request.user.id:
        messages.warning(request, "본인이 작성한 글은 장바구니에 담을 수 없습니다.")
        return redirect("posts:detail", pk=post.id)

    # (선택) 수요글 담기 방지 – 필요 없으면 이 블록 제거
    if post.type == Post.Type.DEMAND:
        messages.warning(request, "수요글은 장바구니 대상이 아닙니다.")
        return redirect("posts:detail", pk=post.id)

    CartItem.objects.get_or_create(cart=cart, post=post)
    messages.success(request, "장바구니에 담았습니다.")
    return redirect("cart:cart_detail")

# 제거
@login_required
def cart_remove(request, post_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    CartItem.objects.filter(cart=cart, post_id=post_id).delete()
    messages.info(request, "장바구니에서 제거했습니다.")
    return redirect("cart:cart_detail")