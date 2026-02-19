from rest_framework import serializers
from .models import Employee, Attendance
import re

class EmployeeSerializer(serializers.ModelSerializer):
    total_present_days = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = '__all__'

    def get_total_present_days(self, obj):
        return obj.attendance_records.filter(status='Present').count()

    def validate_full_name(self, value):
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise serializers.ValidationError("Full name can only contain letters and spaces (no numbers or special characters).")
        return value

    def validate_mobile_number(self, value):
        if value and not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Mobile number must be exactly 10 digits.")
        return value

    def validate(self, data):
        current_id = self.instance.id if self.instance else None
        
        if 'employee_id' in data:
            if Employee.objects.filter(employee_id=data['employee_id']).exclude(id=current_id).exists():
                raise serializers.ValidationError({"employee_id": "This Employee ID is already assigned."})

        if 'email' in data:
            if Employee.objects.filter(email=data['email']).exclude(id=current_id).exists():
                raise serializers.ValidationError({"email": "This Email is already in use."})

        if 'mobile_number' in data and data['mobile_number']:
            if Employee.objects.filter(mobile_number=data['mobile_number']).exclude(id=current_id).exists():
                raise serializers.ValidationError({"mobile_number": "This Mobile Number is already in use."})

        return data

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_name', 'date', 'status']

    def validate_date(self, value):
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("Attendance cannot be marked for future dates.")
        return value