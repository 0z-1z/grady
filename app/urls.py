from django.urls import path
from .views import (
  IndexView, RoleBasedLoginView, LogoutView, TeacherDashboardView, 
  GradeEditorView, ResultCheckerView, ResultView, AdminResultFilterView,
  AdminPermissionFilterView, AdminResultComputeView
  )

urlpatterns = [
  path('', IndexView.as_view(), name='index'),
    path('login/', RoleBasedLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('teacher-dashboard/', TeacherDashboardView.as_view(), name='teacher_dashboard'),
    path('grade-editor/<str:school>/<str:session>/<str:term>/<str:class_assigned>/<str:subject>/', GradeEditorView.as_view(), name='grade_editor'),
    path('result-checker/', ResultCheckerView.as_view(), name='result_checker'),
    path('result/<int:result_id>/', ResultView.as_view(), name='result'),
    path('admin/result-filter/', AdminResultFilterView.as_view(), name='admin_dashboard'),
    path('admin/permission-filter/', AdminPermissionFilterView.as_view(), name='admin_permission_filter'),
    path('admin/result-compute/', AdminResultComputeView.as_view(), name='admin_result_compute')
]
