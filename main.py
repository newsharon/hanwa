from dataset import create_fake_merged
from recommendation import get_top_customers_by_role
from prompt import build_prompt

merged = create_fake_merged()
fp_id = "F001"

top5_join, top5_leave = get_top_customers_by_role(fp_id, merged)

print("✅ [가입 유도 고객]")
for c in top5_join:
    print(build_prompt(c, 목적="가입유도"))
    print("-" * 80)

print("✅ [이탈 방지 고객]")
for c in top5_leave:
    print(build_prompt(c, 목적="이탈방지"))
    print("-" * 80)
