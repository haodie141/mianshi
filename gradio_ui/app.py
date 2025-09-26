import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clinic.settings")
import django
django.setup()

import gradio as gr
from rbac.models import User, Role, Permission
from django.contrib.auth import authenticate

# ===== 工具函数 =====
def get_all_perms():
    return [(f"{p.name}({p.code})", p.code) for p in Permission.objects.all()]

def save_role(role_name, perm_codes):
    if not role_name:
        return "❗ 角色名称不能为空"
    role, _ = Role.objects.get_or_create(name=role_name)
    role.permissions.set(Permission.objects.filter(code__in=perm_codes))
    return f"✅ 角色「{role_name}」已保存/更新"

def list_roles():
    return [r.name for r in Role.objects.all()]

def assign_roles(username, roles):
    user = User.objects.filter(username=username).first()
    if not user:
        return "❗ 用户不存在"
    role_objs = Role.objects.filter(name__in=roles)
    user.roles.set(role_objs)
    return f"✅ 用户 {username} 已分配角色：{','.join(roles)}"

def my_permissions(username):
    user = User.objects.filter(username=username).first()
    if not user:
        return "❗ 用户不存在", []
    perms = set()
    for role in user.roles.all():
        perms.update(role.permissions.values_list("code", flat=True))
    return f"当前用户：{username}", sorted(perms)

# ===== Gradio界面 =====
with gr.Blocks(title="Clinic RBAC - MySQL版") as demo:
    gr.Markdown("## Clinic 角色与权限管理")

    with gr.Tab("① 角色管理"):
        name_inp = gr.Textbox(label="角色名称", placeholder="实习生")
        perm_chk = gr.CheckboxGroup(choices=get_all_perms(), label="权限")
        save_btn = gr.Button("保存", variant="primary")
        out_msg = gr.Textbox(label="结果", interactive=False)
        save_btn.click(save_role, inputs=[name_inp, perm_chk], outputs=out_msg)

    with gr.Tab("② 成员分配"):
        user_dd = gr.Dropdown(choices=[u.username for u in User.objects.all()], label="选择用户")
        role_chk = gr.CheckboxGroup(choices=list_roles(), label="角色")
        assign_btn = gr.Button("更新角色", variant="primary")
        assign_out = gr.Textbox(label="结果", interactive=False)
        assign_btn.click(assign_roles, inputs=[user_dd, role_chk], outputs=assign_out)

    with gr.Tab("③ 权限查看"):
        user_dd2 = gr.Dropdown(choices=[u.username for u in User.objects.all()], label="选择用户")
        check_btn = gr.Button("查询权限")
        info_tx = gr.Textbox(label="基本信息", interactive=False)
        perm_df = gr.JSON(label="权限列表")
        check_btn.click(my_permissions, inputs=user_dd2, outputs=[info_tx, perm_df])

# ===== 启动 =====
# if __name__ == "__main__":
#     demo.launch(server_name="0.0.0.0", server_port=7860,
#                 auth=lambda u, p: authenticate(username=u, password=p))