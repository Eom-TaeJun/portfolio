
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import os

def process_ois():
    """
    Calculates the cumulative basis points to the next FOMC meeting from OIS data.
    """
    # Define paths
    home_dir = os.path.expanduser("~")
    ois_path = os.path.join(home_dir, "data", "usd-sofr-ois-compound.csv")
    fomc_path = os.path.join(home_dir, "data", "fomc_dates.csv")
    output_path = os.path.join(home_dir, "data", "ois_cum_bps_daily.csv")

    # Check for input files
    if not os.path.exists(ois_path):
        print(f"Error: Input file not found at {ois_path}")
        return
    if not os.path.exists(fomc_path):
        print(f"Error: Input file not found at {fomc_path}")
        return

    # Read FOMC dates
    fomc_dates = pd.to_datetime(pd.read_csv(fomc_path).iloc[:, 0])

    # Read OIS data
    ois_df = pd.read_csv(ois_path)

    # Handle wide vs long format
    if "Curve Date" in ois_df.columns:
        # Long format
        ois_df = ois_df.rename(columns={"Curve Date": "date", "Tenor": "tenor", "ZeroRate": "rate"})
        ois_df["date"] = pd.to_datetime(ois_df["date"])
        # Pivot to wide format
        ois_df = ois_df.pivot(index="date", columns="tenor", values="rate")
    else:
        # Assume wide format with a date column
        date_col = [col for col in ois_df.columns if "date" in col.lower()][0]
        ois_df = ois_df.rename(columns={date_col: "date"})
        ois_df["date"] = pd.to_datetime(ois_df["date"])
        ois_df = ois_df.set_index("date")

    # Convert tenors to years
    def tenor_to_years(tenor):
        tenor = tenor.upper()
        if "D" in tenor:
            return int(tenor.replace("D", "")) / 365.0
        if "W" in tenor:
            return int(tenor.replace("W", "")) / 52.0
        if "M" in tenor:
            return int(tenor.replace("M", "")) / 12.0
        if "Y" in tenor:
            return int(tenor.replace("Y", ""))
        return np.nan

    ois_df.columns = [tenor_to_years(c) for c in ois_df.columns]
    ois_df = ois_df.sort_index(axis=1)

    results = []
    for d, row in ois_df.iterrows():
        next_fomc = fomc_dates[fomc_dates > d].min()
        if pd.isnull(next_fomc):
            continue

        h = (next_fomc - d).days / 365.0
        delta = 30 / 365.0

        valid_points = row.dropna()
        if len(valid_points) < 2:
            continue
            
        tenors = valid_points.index.values
        rates = valid_points.values / 100.0 # Assuming rates are in percent

        # Convert rates to discount factors
        dfs = np.exp(-rates * tenors)
        log_dfs = np.log(dfs)

        # Linear interpolation of log-discount factors
        interp_func = interp1d(tenors, log_dfs, kind="linear", fill_value="extrapolate")

        log_df_h = interp_func(h)
        log_df_h_delta = interp_func(h + delta)

        df_h = np.exp(log_df_h)
        df_h_delta = np.exp(log_df_h_delta)

        r_pre = -log_df_h / h if h > 0 else 0
        r_post = -np.log(df_h_delta / df_h) / delta if h > 0 and df_h > 0 else 0
        
        cum_bps = (r_post - r_pre) * 10000

        results.append({
            "date": d.strftime("%Y-%m-%d"),
            "next_fomc_date": next_fomc.strftime("%Y-%m-%d"),
            "cum_bps_to_next": cum_bps,
            "pre_annualized_%": r_pre * 100,
            "post_annualized_%": r_post * 100,
            "method": "log-DF interp (Δ=30d)"
        })

    result_df = pd.DataFrame(results)
    result_df.to_csv(output_path, index=False)
    print(f"Successfully created {output_path}")
    # Validation
    print("\n--- Validation ---")
    print(f"File: {output_path}")
    print(f"Row count: {len(result_df)}")
    if not result_df.empty:
        print(f"Min date: {result_df['date'].min()}")
        print(f"Max date: {result_df['date'].max()}")
        missing_pct = result_df['cum_bps_to_next'].isnull().sum() / len(result_df) * 100
        print(f"% missing (cum_bps_to_next): {missing_pct:.2f}%")


if __name__ == "__main__":
    process_ois()
