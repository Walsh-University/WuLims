from django.urls import path

from . import views

app_name = "results"

urlpatterns = [
    # Основные страницы
    path("", views.results_list, name="list"),
    path("add/", views.result_add, name="add"),
    path("<int:pk>/edit/", views.results_edit, name="edit"),
    path("<int:pk>/", views.result_detail, name="detail"),
    path("<int:pk>/tab/", views.result_detail_tab, name="result_detail_tab"),
    path("table/", views.results_table, name="table"),
    # Модальные окна
    path("<int:pk>/approve_modal/", views.approve_modal, name="approve_modal"),
    path("<int:pk>/submit_modal/", views.submit_modal, name="submit_modal"),
    # Действия над результатами
    path("<int:pk>/submit_result/", views.submit_result, name="submit_result"),
    path("<int:pk>/approve_result/", views.approve_result, name="approve_result"),
    path("<int:pk>/reject_result/", views.reject_result, name="reject_result"),
    # Дополнительные имена URL для тестов (чтобы reverse("submit") и т.д. работали)
    path("<int:pk>/submit_result/", views.submit_result, name="submit"),
    path("<int:pk>/approve_result/", views.approve_result, name="approve"),
    path("<int:pk>/reject_result/", views.reject_result, name="reject"),
]
