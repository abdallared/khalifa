"""
إصلاح wa_id للعملاء الذين لديهم @lid
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer

# قائمة العملاء الذين يجب تحديثهم
lid_customers = [
    {'id': 105, 'wa_id': '108164473172053@lid'},
    {'id': 106, 'wa_id': '89197931184280@lid'},
]

print("=" * 60)
print("🔧 إصلاح wa_id للعملاء الذين لديهم @lid")
print("=" * 60)

for customer_data in lid_customers:
    try:
        customer = Customer.objects.get(id=customer_data['id'])
        old_wa_id = customer.wa_id
        new_wa_id = customer_data['wa_id']
        
        customer.wa_id = new_wa_id
        customer.save(update_fields=['wa_id'])
        
        print(f"\n✅ تم تحديث العميل #{customer.id}:")
        print(f"   الاسم: {customer.name}")
        print(f"   القديم: {old_wa_id}")
        print(f"   الجديد: {new_wa_id}")
        
    except Customer.DoesNotExist:
        print(f"\n❌ العميل #{customer_data['id']} غير موجود")
    except Exception as e:
        print(f"\n❌ خطأ في تحديث العميل #{customer_data['id']}: {e}")

print("\n" + "=" * 60)
print("✅ تم الانتهاء من الإصلاح")
print("=" * 60)

# عرض العملاء المحدثين
print("\n📊 العملاء بعد التحديث:")
for customer_data in lid_customers:
    try:
        customer = Customer.objects.get(id=customer_data['id'])
        print(f"   {customer.id} | {customer.name} | {customer.wa_id}")
    except:
        pass

