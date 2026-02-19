from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Employee, Attendance
from .serializers import EmployeeSerializer, AttendanceSerializer
from rest_framework.views import APIView
from django.utils import timezone


class DashboardStatsView(APIView):
    def get(self, request):
        today = timezone.now().date()
        
        total_employees = Employee.objects.count()
        present_today = Attendance.objects.filter(date=today, status='Present').count()
        absent_today = Attendance.objects.filter(date=today, status='Absent').count()
        
        unmarked = total_employees - (present_today + absent_today)
        
        return Response({
            "total_employees": total_employees,
            "present_today": present_today,
            "absent_today": absent_today,
            "unmarked": max(0, unmarked) 
        })

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('-created_at')
    serializer_class = EmployeeSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"error": "Attendance for this employee on this date already exists or invalid data."},
                status=status.HTTP_400_BAD_REQUEST
            )