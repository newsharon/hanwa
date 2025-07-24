import pandas as pd
import numpy as np

def create_fake_merged(n_customers=30):
    np.random.seed(42)
    data = {
        "FP_UNIQ_NO": np.random.choice(["F001", "F002"], size=n_customers),
        "POLR_CUST_ID": [f"C{1000+i}" for i in range(n_customers)],
        "터치_가입률": np.random.uniform(0.05, 0.25, size=n_customers),
        "미터치_가입률": np.random.uniform(0.02, 0.2, size=n_customers),
        "이탈률_차이": np.random.uniform(-0.05, 0.05, size=n_customers),
        "터치_지연일": np.random.randint(0, 60, size=n_customers),
        "채널구분": np.random.choice(["앱", "콜센터", "홈페이지"], size=n_customers),
        "업무구분": np.random.choice(["청구", "계약", "대출"], size=n_customers),
        "BSWR_NM": np.random.choice(["실손청구", "대출상환", "가입설계"], size=n_customers),
        "RFDT": pd.date_range("2025-03-01", periods=n_customers, freq="D"),
        "생일7일전여부": np.random.choice(["Y", "N"], size=n_customers),
        "계약기념일7일전여부": np.random.choice(["Y", "N"], size=n_customers),
        "만기15일전여부": np.random.choice(["Y", "N"], size=n_customers),
        "당월_캠페인대상여부": np.random.choice(["Y", "N"], size=n_customers),
        "당월_청구여부": np.random.choice(["Y", "N"], size=n_customers),
        "당월_입원여부": np.random.choice(["Y", "N"], size=n_customers),
        "당월_수술여부": np.random.choice(["Y", "N"], size=n_customers),
        "당월_재해여부": np.random.choice(["Y", "N"], size=n_customers),
        "당월_교통재해여부": np.random.choice(["Y", "N"], size=n_customers),
        "전월_보험금청구_접점발생여부": np.random.choice(["Y", "N"], size=n_customers),
        "전월_접점발생여부": np.random.choice(["Y", "N"], size=n_customers),
        "당월_질병여부": np.random.choice(["Y", "N"], size=n_customers),
        "당월_대출_접점발생여부": np.random.choice(["Y", "N"], size=n_customers),
    }
    df = pd.DataFrame(data)
    df["가입률_차이"] = df["터치_가입률"] - df["미터치_가입률"]
    return df 