# conversations/views_backup.py
"""
Database Backup and Restore Views
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from django.conf import settings
from django.http import FileResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


# مجلد النسخ الاحتياطية
BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backups')

# إنشاء المجلد إذا لم يكن موجوداً
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_backup(request):
    """
    إنشاء نسخة احتياطية من قاعدة البيانات
    POST /api/backup/create/
    
    ✅ يقوم بنسخ ملف db.sqlite3
    ✅ يحفظ النسخة في مجلد backups
    ✅ يضيف timestamp للاسم
    """
    # التحقق من صلاحيات الأدمن
    if request.user.role != 'admin':
        return Response({
            'success': False,
            'error': 'ليس لديك صلاحية لإنشاء نسخة احتياطية'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # مسار قاعدة البيانات الحالية
        db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        
        if not os.path.exists(db_path):
            return Response({
                'success': False,
                'error': 'ملف قاعدة البيانات غير موجود'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # إنشاء اسم الملف مع timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.sqlite3'
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        # نسخ قاعدة البيانات
        shutil.copy2(db_path, backup_path)
        
        # حساب حجم الملف
        file_size = os.path.getsize(backup_path)
        file_size_mb = round(file_size / (1024 * 1024), 2)
        
        # حفظ معلومات النسخة الاحتياطية
        metadata = {
            'filename': backup_filename,
            'created_at': timestamp,
            'created_by': request.user.username,
            'size_bytes': file_size,
            'size_mb': file_size_mb
        }
        
        metadata_path = os.path.join(BACKUP_DIR, f'backup_{timestamp}.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return Response({
            'success': True,
            'message': 'تم إنشاء النسخة الاحتياطية بنجاح',
            'backup': {
                'filename': backup_filename,
                'size_mb': file_size_mb,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'حدث خطأ أثناء إنشاء النسخة الاحتياطية: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restore_backup(request):
    """
    استعادة نسخة احتياطية
    POST /api/backup/restore/
    
    Body:
    {
        "filename": "backup_20250113_120000.sqlite3"
    }
    
    ✅ يستعيد قاعدة البيانات من النسخة الاحتياطية
    ✅ يحفظ نسخة احتياطية من البيانات الحالية قبل الاستعادة
    """
    # التحقق من صلاحيات الأدمن
    if request.user.role != 'admin':
        return Response({
            'success': False,
            'error': 'ليس لديك صلاحية لاستعادة نسخة احتياطية'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        filename = request.data.get('filename')
        
        if not filename:
            return Response({
                'success': False,
                'error': 'يرجى تحديد اسم الملف'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # مسار النسخة الاحتياطية
        backup_path = os.path.join(BACKUP_DIR, filename)
        
        if not os.path.exists(backup_path):
            return Response({
                'success': False,
                'error': 'النسخة الاحتياطية غير موجودة'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # مسار قاعدة البيانات الحالية
        db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        
        # إنشاء نسخة احتياطية من البيانات الحالية قبل الاستعادة
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pre_restore_backup = os.path.join(BACKUP_DIR, f'pre_restore_{timestamp}.sqlite3')
        shutil.copy2(db_path, pre_restore_backup)
        
        # استعادة النسخة الاحتياطية
        shutil.copy2(backup_path, db_path)
        
        return Response({
            'success': True,
            'message': 'تم استعادة النسخة الاحتياطية بنجاح',
            'restored_from': filename,
            'pre_restore_backup': f'pre_restore_{timestamp}.sqlite3'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'حدث خطأ أثناء استعادة النسخة الاحتياطية: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_backups(request):
    """
    عرض قائمة النسخ الاحتياطية
    GET /api/backup/list/
    
    ✅ يعرض جميع النسخ الاحتياطية المتاحة
    ✅ يعرض معلومات كل نسخة (الحجم، التاريخ، إلخ)
    """
    # التحقق من صلاحيات الأدمن
    if request.user.role != 'admin':
        return Response({
            'success': False,
            'error': 'ليس لديك صلاحية لعرض النسخ الاحتياطية'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        backups = []
        
        # قراءة جميع ملفات النسخ الاحتياطية
        for filename in os.listdir(BACKUP_DIR):
            if filename.endswith('.sqlite3'):
                file_path = os.path.join(BACKUP_DIR, filename)
                file_size = os.path.getsize(file_path)
                file_size_mb = round(file_size / (1024 * 1024), 2)
                
                # محاولة قراءة الـ metadata
                metadata_filename = filename.replace('.sqlite3', '.json')
                metadata_path = os.path.join(BACKUP_DIR, metadata_filename)
                
                created_by = 'Unknown'
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            created_by = metadata.get('created_by', 'Unknown')
                    except:
                        pass
                
                # الحصول على تاريخ التعديل
                modified_time = os.path.getmtime(file_path)
                modified_date = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S')
                
                backups.append({
                    'filename': filename,
                    'size_mb': file_size_mb,
                    'created_at': modified_date,
                    'created_by': created_by
                })
        
        # ترتيب النسخ حسب التاريخ (الأحدث أولاً)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return Response({
            'success': True,
            'backups': backups,
            'total': len(backups)
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'حدث خطأ أثناء عرض النسخ الاحتياطية: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_backup(request):
    """
    حذف نسخة احتياطية
    POST /api/backup/delete/
    
    Body:
    {
        "filename": "backup_20250113_120000.sqlite3"
    }
    """
    # التحقق من صلاحيات الأدمن
    if request.user.role != 'admin':
        return Response({
            'success': False,
            'error': 'ليس لديك صلاحية لحذف النسخ الاحتياطية'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        filename = request.data.get('filename')
        
        if not filename:
            return Response({
                'success': False,
                'error': 'يرجى تحديد اسم الملف'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # مسار النسخة الاحتياطية
        backup_path = os.path.join(BACKUP_DIR, filename)
        
        if not os.path.exists(backup_path):
            return Response({
                'success': False,
                'error': 'النسخة الاحتياطية غير موجودة'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # حذف الملف
        os.remove(backup_path)
        
        # حذف ملف الـ metadata إذا كان موجوداً
        metadata_filename = filename.replace('.sqlite3', '.json')
        metadata_path = os.path.join(BACKUP_DIR, metadata_filename)
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        
        return Response({
            'success': True,
            'message': 'تم حذف النسخة الاحتياطية بنجاح'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'حدث خطأ أثناء حذف النسخة الاحتياطية: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

