import os
import django

# 一定要先设置settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clinic.settings")
django.setup()

from rbac.models import User, Role, Permission

# 1. 权限字典
perms = [
    ("case:delete", "可删除病例"),
    ("case:note:create", "可创建笔记"),
    ("canvas:block:create", "可添加画布块"),
]
for code, name in perms:
    Permission.objects.get_or_create(code=code, defaults={"name": name})

# 2. 超级管理员
admin, _ = User.objects.get_or_create(username="admin", defaults={"plan": "pro"})
admin.set_password("admin")
admin.is_superuser = True
admin.is_staff = True
admin.save()

# 3. 示例普通用户
u2, _ = User.objects.get_or_create(username="member", defaults={"plan": "free"})
u2.set_password("member")
u2.save()

print("✅ 权限字典 & 演示账号  admin/admin  member/member 已生成")