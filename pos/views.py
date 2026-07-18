import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import PosTable, PosMenuItem, PosOrder, PosOrderItem
from bookkeeping.models import BkLedger

def is_manager(user): return user.groups.filter(name='Manager').exists()
def is_cashier(user): return user.groups.filter(name='Cashier').exists()
def is_waiter(user): return not (is_manager(user) or is_cashier(user))

@never_cache
@login_required
def route_user(request):
    if is_manager(request.user): return redirect('ledger_dashboard')
    elif is_cashier(request.user): return redirect('cashier_dashboard')
    else: return redirect('waiter_dashboard')

@never_cache
@login_required
@user_passes_test(is_waiter, login_url='/login/')
def waiter_dashboard(request):
    tables = PosTable.objects.all().order_by('number')
    menu_items = PosMenuItem.objects.all()
    return render(request, 'pos/waiter_dashboard.html', {'tables': tables, 'menu_items': menu_items})

@never_cache
@login_required
@user_passes_test(is_cashier, login_url='/login/')
def cashier_dashboard(request):
    occupied_tables = PosTable.objects.filter(is_occupied=True).order_by('number')
    pending_orders = PosOrder.objects.filter(status='Pending').order_by('table__number')
    return render(request, 'pos/cashier_dashboard.html', {'occupied_tables': occupied_tables, 'pending_orders': pending_orders})

@never_cache
@login_required
@user_passes_test(is_waiter, login_url='/login/')
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            table = PosTable.objects.get(id=data.get('table_id'))
            if table.is_occupied: return JsonResponse({'status': 'error', 'message': 'Table occupied.'}, status=400)

            table.is_occupied = True
            table.save()
            order = PosOrder.objects.create(table=table, status='Pending')
            total_price = 0

            for item_data in data.get('items'):
                qty = int(item_data['qty'])
                if qty <= 0: raise ValueError("Invalid quantity")
                menu_item = PosMenuItem.objects.get(id=item_data['item_id'])
                PosOrderItem.objects.create(order=order, item=menu_item, quantity=qty)
                total_price += (menu_item.price * qty)

            order.total = total_price
            order.save()
            return JsonResponse({'status': 'success', 'order_id': order.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

@never_cache
@login_required
@user_passes_test(is_cashier, login_url='/login/')
def settle_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = PosOrder.objects.get(id=data.get('order_id'))
            payment_method = data.get('payment_method')

            if order.status != 'Pending': return JsonResponse({'status': 'error', 'message': 'Already settled.'}, status=400)

            order.status = 'Paid'
            order.payment_method = payment_method
            order.save()

            table = order.table
            table.is_occupied = False
            table.save()

            customer_name = data.get('customer_name', '')
            customer_phone = data.get('customer_phone', '')
            desc = f"Payment via {payment_method} for Table {table.number}"
            if payment_method == 'Due':
                desc = f"DUE ACCOUNT (Table {table.number}) | Customer: {customer_name} | Contact: {customer_phone}"

            BkLedger.objects.create(order=order, amount=order.total, description=desc)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)