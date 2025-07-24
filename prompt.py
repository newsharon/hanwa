def build_prompt(customer, 목적="가입유도", report_summary=None, events=None, history=None):
    이벤트들 = events if events is not None else [k for k in customer.keys() if customer[k] == "Y" and "여부" in k]
    이벤트_str = ", ".join(이벤트들) if 이벤트들 else "없음"
    history_str = ""
    if history is not None and len(history) > 0:
        for h in history:
            history_str += f"- {h['RFDT'].date()} | {h['채널구분']} | {h['업무구분']} | {h['BSWR_NM']}\n"
    else:
        history_str = "- 내역 없음\n"
    report_str = report_summary if report_summary else "고객의 최근 접점 및 이벤트 정보를 참고하세요."
    return f"""
당신은 생명보험 설계사를 위한 AI 비서입니다.
아래 고객 정보를 참고하여 {목적}을 위한 고객 메시지를 3가지 버전으로 작성하세요.

[고객 정보]
- 고객 ID: {customer['POLR_CUST_ID']}
- FP ID: {customer['FP_UNIQ_NO']}
- 최근 접점일: {customer['RFDT'].date()}
- 채널구분: {customer['채널구분']}, 업무구분: {customer['업무구분']}, BSWR 명: {customer['BSWR_NM']}

[이벤트 발생]
- {이벤트_str}

[이전 접점 내역]
{history_str}
[리포트 요약]
{report_str}

[작성 지침]
- 공손하고 짧은 고객 메시지를 3가지 버전으로 작성
- 각 메시지는 3줄 이내
- 직접 보낼 수 있는 말투로 작성
"""
