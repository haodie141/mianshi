import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clinic.settings")
import django
django.setup()

import gradio as gr
from rbac.models import User, Role, Permission
from django.contrib.auth import authenticate

# ========== 工具函数 ==========
def get_all_perms():
    return [(f"{p.name}({p.code})", p.code) for p in Permission.objects.all()]

def save_role(role_name, perm_codes):
    if not role_name:
        return "❗ 角色名称不能为空"
    role, created = Role.objects.get_or_create(name=role_name)
    role.permissions.set(Permission.objects.filter(code__in=perm_codes))
    return f"✅ 角色「{role_name}」已保存（权限：{len(perm_codes)} 个）"

def list_roles():
    return [r.name for r in Role.objects.all()]

def assign_roles(username, roles):
    user = User.objects.filter(username=username).first()
    if not user:
        return "❗ 用户不存在"
    role_objs = Role.objects.filter(name__in=roles)
    user.roles.set(role_objs)
    return f"✅ 用户 {username} 已分配角色：{','.join(roles)}"

def my_permissions(username: str):
    user = User.objects.filter(username=username).first()
    if not user:
        return []
    role_ids = user.roles.values_list("id", flat=True)
    if not role_ids:
        return []
    codes = Permission.objects.filter(
        role__id__in=role_ids
    ).values_list("code", flat=True).distinct()
    return sorted(codes)

# ========== 前端 Wrapper（带空权限提示） ==========
def query_perms_wrapper(username):
    perms = my_permissions(username)
    if not perms:
        return "该用户尚未分配任何角色", []
    return f"用户：{username}", perms

# ========== Gradio 界面 ==========
with gr.Blocks(title="Clinic RBAC - MySQL版") as demo:
    gr.Markdown("## Clinic 角色与权限管理")

    # ① 角色管理
    with gr.Tab("① 角色管理"):
        name_inp = gr.Textbox(label="角色名称", placeholder="实习生")
        perm_chk = gr.CheckboxGroup(choices=get_all_perms(), label="权限（不勾=清空）")
        save_btn = gr.Button("保存", variant="primary")
        out_msg = gr.Textbox(label="结果", interactive=False)
        save_btn.click(save_role, inputs=[name_inp, perm_chk], outputs=out_msg)

    # ② 成员分配
    with gr.Tab("② 成员分配"):
        user_dd = gr.Dropdown(choices=[u.username for u in User.objects.all()], label="选择用户")
        role_chk = gr.CheckboxGroup(choices=list_roles(), label="角色")
        assign_btn = gr.Button("更新角色", variant="primary")
        assign_out = gr.Textbox(label="结果", interactive=False)
        assign_btn.click(assign_roles, inputs=[user_dd, role_chk], outputs=assign_out)

    # ③ 权限查看（中文+过滤空角色）
    with gr.Tab("③ 权限查看"):
        # 只取“有角色”的用户，显示 first_name（中文）
        role_users = [
            (u.first_name or u.username, u.username)
            for u in User.objects.filter(roles__permissions__isnull=False).distinct()
        ]
        user_dd2 = gr.Dropdown(choices=role_users, label="选择用户")
        check_btn = gr.Button("查询权限")
        info_tx = gr.Textbox(label="基本信息", interactive=False)
        perm_df = gr.JSON(label="权限列表")
        demo_delete_btn = gr.Button("尝试删除病例", variant="stop")


        def query_perms_wrapper(username):
            perms = my_permissions(username)
            if not perms:
                return "该用户尚未分配任何角色", []
            return f"用户：{username}", perms


        def refresh_del_btn(username):
            return "case:delete" in my_permissions(username)


        check_btn.click(query_perms_wrapper, inputs=user_dd2, outputs=[info_tx, perm_df])
        check_btn.click(refresh_del_btn, inputs=user_dd2, outputs=demo_delete_btn)
        user_dd2.change(refresh_del_btn, inputs=user_dd2, outputs=demo_delete_btn)

# ========== 启动（由 run.py 调用时不再 launch） ==========
# if __name__ == "__main__":
#     demo.queue().launch(server_name="0.0.0.0", server_port=7860,
#                         auth=lambda u, p: authenticate(username=u, password=p))