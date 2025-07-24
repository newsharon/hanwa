def get_top_customers_by_role(fp_id, df):
    df = df[df["FP_UNIQ_NO"] == fp_id].copy()
    if df.empty:
        return [], []

    event_join = ["계약기념일7일전여부", "당월_캠페인대상여부", "만기15일전여부", "생일7일전여부"]
    event_leave = [
        "당월_청구여부", "당월_질병여부", "전월_보험금청구_접점발생여부", "당월_입원여부",
        "당월_교통재해여부", "당월_수술여부", "전월_접점발생여부", "당월_재해여부", "당월_대출_접점발생여부"
    ]

    df["가입유도_이벤트_개수"] = df[event_join].eq("Y").sum(axis=1)
    df["이탈방지_이벤트_개수"] = df[event_leave].eq("Y").sum(axis=1)

    df["가입유도_점수"] = df["터치_가입률"].fillna(0) * 1.5 + df["가입유도_이벤트_개수"] * 2.0
    df["이탈방지_점수"] = -df["이탈률_차이"].fillna(0) * 1.5 + df["이탈방지_이벤트_개수"] * 2.0

    top5_join = df.sort_values("가입유도_점수", ascending=False).head(5).to_dict(orient="records")
    top5_leave = df.sort_values("이탈방지_점수", ascending=False).head(5).to_dict(orient="records")

    return top5_join, top5_leave
