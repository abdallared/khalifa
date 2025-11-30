# conversations/views_analytics.py
"""
KPI & Analytics Views
"""

from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, F
from datetime import datetime, timedelta

from .models import *
from .serializers import *
from .permissions import *
from .utils import *


# ============================================================================
# KPI VIEWS
# ============================================================================

class AgentKPIViewSet(viewsets.ReadOnlyModelViewSet):
    """
    عرض مؤشرات الأداء اليومية
    """
    queryset = AgentKPI.objects.select_related('agent__user').all()
    serializer_class = AgentKPISerializer
    permission_classes = [CanViewAnalytics]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user or not user.is_authenticated:
            return queryset.none()

        # الموظفون: فقط مؤشراتهم الخاصة
        if user.role == 'agent':
            try:
                agent = user.agent
                queryset = queryset.filter(agent=agent)
            except:
                return queryset.none()

        # المديرون: جميع المؤشرات

        # التصفية حسب التاريخ
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)

        if date_from:
            queryset = queryset.filter(kpi_date__gte=date_from)

        if date_to:
            queryset = queryset.filter(kpi_date__lte=date_to)

        return queryset.order_by('-kpi_date')


class AgentKPIMonthlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    عرض مؤشرات الأداء الشهرية
    """
    queryset = AgentKPIMonthly.objects.select_related('agent__user').all()
    serializer_class = AgentKPIMonthlySerializer
    permission_classes = [CanViewAnalytics]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user or not user.is_authenticated:
            return queryset.none()

        # الموظفون: فقط مؤشراتهم الخاصة
        if user.role == 'agent':
            try:
                agent = user.agent
                queryset = queryset.filter(agent=agent)
            except:
                return queryset.none()

        # المديرون: جميع المؤشرات

        return queryset.order_by('-month', 'rank')


class CustomerSatisfactionViewSet(viewsets.ModelViewSet):
    """
    إدارة تقييمات رضا العملاء
    """
    queryset = CustomerSatisfaction.objects.select_related('ticket', 'agent__user').all()
    serializer_class = CustomerSatisfactionSerializer
    permission_classes = [IsAdminOrAgent]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # التصفية حسب الموظف
        agent_id = self.request.query_params.get('agent', None)
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)
        
        # التصفية حسب التقييم
        rating = self.request.query_params.get('rating', None)
        if rating:
            queryset = queryset.filter(rating=rating)
        
        return queryset.order_by('-created_at')


# ============================================================================
# DASHBOARD & ANALYTICS VIEWS
# ============================================================================

class DashboardView(views.APIView):
    """
    لوحة التحكم الرئيسية
    GET /api/dashboard/
    """
    permission_classes = [IsAdminOrAgent]
    
    def get(self, request):
        # استخدام request.user بدلاً من session
        user = request.user

        if not user or not user.is_authenticated:
            return Response({
                'error': 'غير مصرح'
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            if user.role == 'admin':
                # لوحة تحكم المدير
                data = self._get_admin_dashboard()
            else:
                # لوحة تحكم الموظف
                agent = user.agent
                data = self._get_agent_dashboard(agent)

            return Response(data)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_admin_dashboard(self):
        """
        بيانات لوحة تحكم المدير
        """
        today = timezone.now().date()
        
        # إحصائيات عامة
        total_tickets = Ticket.objects.count()
        open_tickets = Ticket.objects.filter(status='open').count()
        delayed_tickets = Ticket.objects.filter(is_delayed=True).count()
        closed_today = Ticket.objects.filter(
            status='closed',
            closed_at__date=today
        ).count()
        
        # إحصائيات الموظفين
        total_agents = Agent.objects.count()
        online_agents = Agent.objects.filter(is_online=True).count()
        available_agents = Agent.objects.filter(
            is_online=True,
            status='available',
            current_active_tickets__lt=F('max_capacity')
        ).count()
        
        # إحصائيات العملاء
        total_customers = Customer.objects.count()
        new_customers_today = Customer.objects.filter(
            created_at__date=today
        ).count()
        
        # متوسط وقت الاستجابة
        avg_response_time = Ticket.objects.filter(
            response_time_seconds__isnull=False,
            created_at__date=today
        ).aggregate(Avg('response_time_seconds'))['response_time_seconds__avg'] or 0
        
        # أفضل 5 موظفين
        top_agents = AgentKPI.objects.filter(
            kpi_date=today
        ).order_by('-overall_kpi_score')[:5]
        
        top_agents_data = []
        for kpi in top_agents:
            top_agents_data.append({
                'agent_name': kpi.agent.user.full_name,
                'kpi_score': kpi.overall_kpi_score,
                'total_tickets': kpi.total_tickets,
                'closed_tickets': kpi.closed_tickets,
            })
        
        return {
            'tickets': {
                'total': total_tickets,
                'open': open_tickets,
                'delayed': delayed_tickets,
                'closed_today': closed_today,
            },
            'agents': {
                'total': total_agents,
                'online': online_agents,
                'available': available_agents,
            },
            'customers': {
                'total': total_customers,
                'new_today': new_customers_today,
            },
            'performance': {
                'avg_response_time_seconds': int(avg_response_time),
                'avg_response_time_minutes': int(avg_response_time / 60),
            },
            'top_agents': top_agents_data,
        }
    
    def _get_agent_dashboard(self, agent):
        """
        بيانات لوحة تحكم الموظف
        """
        today = timezone.now().date()
        
        # تذاكر الموظف
        my_tickets = Ticket.objects.filter(
            Q(assigned_agent=agent) | Q(current_agent=agent)
        )
        
        total_tickets = my_tickets.count()
        open_tickets = my_tickets.filter(status='open').count()
        delayed_tickets = my_tickets.filter(is_delayed=True).count()
        closed_today = my_tickets.filter(
            status='closed',
            closed_at__date=today
        ).count()
        
        # مؤشرات الأداء
        kpi_data = calculate_agent_kpi(agent, today)
        
        # آخر 5 تذاكر
        recent_tickets = my_tickets.select_related(
            'customer', 'assigned_agent__user'
        ).order_by('-created_at')[:5]
        
        recent_tickets_data = []
        for ticket in recent_tickets:
            recent_tickets_data.append({
                'id': ticket.id,
                'ticket_number': ticket.ticket_number,
                'customer_name': ticket.customer.name,
                'status': ticket.status,
                'priority': ticket.priority,
                'is_delayed': ticket.is_delayed,
                'created_at': ticket.created_at,
            })
        
        return {
            'agent': {
                'name': agent.user.full_name,
                'max_capacity': agent.max_capacity,
                'current_active_tickets': agent.current_active_tickets,
                'available_capacity': agent.max_capacity - agent.current_active_tickets,
                'status': agent.status,
            },
            'tickets': {
                'total': total_tickets,
                'open': open_tickets,
                'delayed': delayed_tickets,
                'closed_today': closed_today,
            },
            'kpi': kpi_data,
            'recent_tickets': recent_tickets_data,
        }


class ReportsView(views.APIView):
    """
    التقارير
    GET /api/reports/
    """
    permission_classes = [CanViewAnalytics]
    
    def get(self, request):
        report_type = request.query_params.get('type', 'daily')
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)

        # معالجة date_from
        if not date_from or date_from.strip() == '':
            date_from = timezone.now().date()
        else:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                date_from = timezone.now().date()

        # معالجة date_to
        if not date_to or date_to.strip() == '':
            date_to = date_from
        else:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                date_to = date_from
        
        if report_type == 'daily':
            data = self._get_daily_report(date_from, date_to)
        elif report_type == 'agent':
            data = self._get_agent_report(date_from, date_to)
        elif report_type == 'customer':
            data = self._get_customer_report(date_from, date_to)
        elif report_type == 'user_period_summary':
            data = self._get_user_period_summary(date_from, date_to)
        elif report_type == 'user_ticket_summary':
            data = self._get_user_ticket_summary(date_from, date_to)
        else:
            return Response({
                'error': 'نوع التقرير غير صحيح'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data)
    
    def _get_daily_report(self, date_from, date_to):
        """
        تقرير يومي
        """
        # تحويل التواريخ إلى datetime مع timezone
        from datetime import datetime, time

        start_datetime = timezone.make_aware(datetime.combine(date_from, time.min))
        end_datetime = timezone.make_aware(datetime.combine(date_to, time.max))

        tickets = Ticket.objects.filter(
            created_at__gte=start_datetime,
            created_at__lte=end_datetime
        )
        
        # Calculate aggregated agent performance for the period
        agent_stats = AgentKPI.objects.filter(
            kpi_date__gte=date_from,
            kpi_date__lte=date_to
        ).values(
            'agent__user__full_name',
            'agent__user__username'
        ).annotate(
            total_tickets=Sum('total_tickets'),
            closed_tickets=Sum('closed_tickets'),
            messages_sent=Sum('messages_sent'),
            avg_response_time=Avg('avg_response_time_seconds'),
            avg_satisfaction=Avg('customer_satisfaction_score'),
            avg_score=Avg('overall_kpi_score')
        ).order_by('-avg_score')
        
        agents_data = []
        for stat in agent_stats:
            agents_data.append({
                'name': stat['agent__user__full_name'] or stat['agent__user__username'],
                'total_tickets': stat['total_tickets'],
                'closed_tickets': stat['closed_tickets'],
                'messages_sent': stat['messages_sent'],
                'avg_response_time': stat['avg_response_time'],
                'satisfaction': stat['avg_satisfaction'],
                'score': stat['avg_score']
            })

        return {
            'period': {
                'from': date_from,
                'to': date_to,
            },
            'tickets': {
                'total': tickets.count(),
                'open': tickets.filter(status='open').count(),
                'closed': tickets.filter(status='closed').count(),
                'delayed': tickets.filter(is_delayed=True).count(),
            },
            'performance': {
                'avg_response_time': tickets.filter(
                    response_time_seconds__isnull=False
                ).aggregate(Avg('response_time_seconds'))['response_time_seconds__avg'] or 0,
                'avg_handling_time': tickets.filter(
                    handling_time_seconds__isnull=False
                ).aggregate(Avg('handling_time_seconds'))['handling_time_seconds__avg'] or 0,
            },
            'agents': agents_data
        }
    
    def _get_agent_report(self, date_from, date_to):
        """
        تقرير الموظفين
        """
        kpis = AgentKPI.objects.filter(
            kpi_date__gte=date_from,
            kpi_date__lte=date_to
        ).select_related('agent__user')
        
        agents_data = []
        for kpi in kpis:
            agents_data.append({
                'agent_name': kpi.agent.user.full_name,
                'date': kpi.kpi_date,
                'total_tickets': kpi.total_tickets,
                'closed_tickets': kpi.closed_tickets,
                'kpi_score': kpi.overall_kpi_score,
            })
        
        return {
            'period': {
                'from': date_from,
                'to': date_to,
            },
            'agents': agents_data,
        }
    
    def _get_customer_report(self, date_from, date_to):
        """
        تقرير العملاء
        """
        # تحويل التواريخ إلى datetime مع timezone
        from datetime import datetime, time

        start_datetime = timezone.make_aware(datetime.combine(date_from, time.min))
        end_datetime = timezone.make_aware(datetime.combine(date_to, time.max))

        customers = Customer.objects.filter(
            created_at__gte=start_datetime,
            created_at__lte=end_datetime
        )
        
        return {
            'period': {
                'from': date_from,
                'to': date_to,
            },
            'customers': {
                'total': customers.count(),
                'new': customers.count(),
                'regular': customers.filter(customer_type='regular').count(),
                'vip': customers.filter(customer_type='vip').count(),
            }
        }

    def _get_user_period_summary(self, date_from, date_to):
        """
        User Period Summary: (Agent, Customer, Order)
        """
        from datetime import datetime, time
        start_datetime = timezone.make_aware(datetime.combine(date_from, time.min))
        end_datetime = timezone.make_aware(datetime.combine(date_to, time.max))

        tickets = Ticket.objects.filter(
            created_at__gte=start_datetime,
            created_at__lte=end_datetime
        ).select_related('assigned_agent__user', 'customer').order_by('assigned_agent__user__full_name', '-created_at')

        data = []
        for ticket in tickets:
            agent_name = ticket.assigned_agent.user.full_name if ticket.assigned_agent else "Unassigned"
            customer_name = ticket.customer.name if ticket.customer else "Unknown"
            
            data.append({
                'agent': agent_name,
                'customer': customer_name,
                'order': ticket.ticket_number,
                'created_at': ticket.created_at
            })

        return {
            'period': {
                'from': date_from,
                'to': date_to,
            },
            'summary': data
        }

    def _get_user_ticket_summary(self, date_from, date_to):
        """
        User Ticket Summary: (Agent, Ticket, Total Number Delay, Avg Delay)
        """
        from datetime import datetime, time
        start_datetime = timezone.make_aware(datetime.combine(date_from, time.min))
        end_datetime = timezone.make_aware(datetime.combine(date_to, time.max))

        # Get all agents who have tickets in this period
        agents = Agent.objects.filter(
            assigned_tickets__created_at__gte=start_datetime,
            assigned_tickets__created_at__lte=end_datetime
        ).distinct()

        data = []
        for agent in agents:
            agent_tickets = Ticket.objects.filter(
                assigned_agent=agent,
                created_at__gte=start_datetime,
                created_at__lte=end_datetime
            )
            
            total_tickets = agent_tickets.count()
            delayed_tickets_count = agent_tickets.filter(is_delayed=True).count()
            
            # Calculate average delay for delayed tickets
            avg_delay = agent_tickets.filter(is_delayed=True).aggregate(Avg('total_delay_minutes'))['total_delay_minutes__avg'] or 0
            
            data.append({
                'agent': agent.user.full_name,
                'ticket_count': total_tickets,
                'total_number_delay': delayed_tickets_count,
                'avg_delay': round(avg_delay, 2)
            })
            
        return {
            'period': {
                'from': date_from,
                'to': date_to,
            },
            'summary': data
        }

