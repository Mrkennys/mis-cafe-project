import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from django.shortcuts import render
from django.db.models import Sum, Count
from .models import BkLedger
from pos.models import PosOrder, PosOrderItem

def is_manager(user): return user.groups.filter(name='Manager').exists()

@never_cache
@login_required
@user_passes_test(is_manager, login_url='/login/')
def ledger_dashboard(request):
    entries = BkLedger.objects.all().order_by('-date')
    paid_orders = PosOrder.objects.filter(status='Paid')
    
    total_sales = paid_orders.exclude(payment_method='Due').aggregate(Sum('total'))['total__sum'] or 0.00
    total_due = paid_orders.filter(payment_method='Due').aggregate(Sum('total'))['total__sum'] or 0.00
    
    top_item_query = PosOrderItem.objects.filter(order__status='Paid').values('item__name').annotate(total_qty=Sum('quantity')).order_by('-total_qty').first()
    top_item = top_item_query['item__name'] if top_item_query else "N/A"
    
    top_table_query = paid_orders.values('table__number').annotate(total_orders=Count('id')).order_by('-total_orders').first()
    top_table = f"Table {top_table_query['table__number']}" if top_table_query else "N/A"

    return render(request, 'bookkeeping/ledger_dashboard.html', {
        'entries': entries, 'total_sales': total_sales, 'total_due': total_due, 
        'top_item': top_item, 'top_table': top_table
    })

@never_cache
@login_required
@user_passes_test(is_manager, login_url='/login/')
def export_ledger_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="lekali_java_financial_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date & Time', 'Transaction Details', 'Amount (Rs.)'])
    for entry in BkLedger.objects.all().order_by('-date'):
        writer.writerow([entry.date.strftime("%Y-%m-%d %H:%M:%S"), entry.description, entry.amount])
    return response