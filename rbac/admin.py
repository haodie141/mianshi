from django.contrib import admin
from rbac.models import Role, Permission, User

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'permissions_count')
    # ① 权限字段只读（Gradio 写的，Admin 不许改）
    readonly_fields = ('permissions',)
    # ② 仍然用横向筛选框展示，但灰色不可操作
    filter_horizontal = ('permissions',)

    def permissions_count(self, obj):
        return obj.permissions.count()
    permissions_count.short_description = "权限数"


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    # 代码字段也锁死，防止人工改代号
    readonly_fields = ('code', 'name')