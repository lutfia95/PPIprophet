import argparse
import pandas as pd

def main():
    ap = argparse.ArgumentParser(description="Summarize coverage of WD>0 pairs in correlation vs CoMigratorScore.")
    ap.add_argument("--infile", required=True, help="ppiprophet_vs-comigrator.tsv")
    ap.add_argument("--out_prefix", default="report", help="Prefix for output txt files")
    ap.add_argument("--comi_thresh", type=float, default=0.93, help="Threshold for CoMigratorScore (default: 0.93)")
    args = ap.parse_args()

    df = pd.read_csv(args.infile, sep="\t", dtype=str).fillna("")

    need = ["ProtA", "ProtB", "WD", "correlation", "CoMigratorScore"]
    missing_cols = [c for c in need if c not in df.columns]
    if missing_cols:
        raise SystemExit(f"Missing columns in input: {missing_cols}")

    df["WD_num"] = pd.to_numeric(df["WD"], errors="coerce").fillna(0.0)
    df["CoMi_num"] = pd.to_numeric(df["CoMigratorScore"], errors="coerce")  # NaN for notFound/etc

    wd_pos = df["WD_num"] > 0
    wd_zero = df["WD_num"] == 0

    corr_found = df["correlation"].astype(str).str.strip().ne("notFound") & df["correlation"].astype(str).str.strip().ne("")
    comi_found = df["CoMigratorScore"].astype(str).str.strip().ne("notFound") & df["CoMigratorScore"].astype(str).str.strip().ne("")

    # WD>0 counts
    n_wd_pos = int(wd_pos.sum())
    n_wd_pos_corr = int((wd_pos & corr_found).sum())
    n_wd_pos_comi = int((wd_pos & comi_found).sum())
    n_wd_pos_missing_both = int((wd_pos & ~corr_found & ~comi_found).sum())

    # WD>0 corr yes, comi no
    wdpos_corr_only = wd_pos & corr_found & ~comi_found
    n_wdpos_corr_only = int(wdpos_corr_only.sum())

    # WD==0 counts
    n_wd_zero = int(wd_zero.sum())
    n_wd_zero_missing_both = int((wd_zero & ~corr_found & ~comi_found).sum())
    n_wd_zero_corr_or_comi = int((wd_zero & (corr_found | comi_found)).sum())
    n_wd_zero_corr_found = int((wd_zero & corr_found).sum())
    n_wd_zero_comi_found = int((wd_zero & comi_found).sum())

    # NEW: WD==0 and CoMigratorScore >= threshold (must be numeric)
    wdzero_comi_ge = wd_zero & df["CoMi_num"].notna() & (df["CoMi_num"] >= args.comi_thresh)
    n_wdzero_comi_ge = int(wdzero_comi_ge.sum())

    def write_pairs(mask, path):
        df.loc[mask, ["ProtA", "ProtB"]].to_csv(path, sep="\t", index=False)

    # WD>0 lists
    write_pairs(wd_pos & ~corr_found & ~comi_found, f"{args.out_prefix}.wdpos_missing_both.txt")
    write_pairs(wd_pos & ~comi_found, f"{args.out_prefix}.wdpos_missing_comigrator.txt")
    write_pairs(wd_pos & ~corr_found, f"{args.out_prefix}.wdpos_missing_correlation.txt")
    write_pairs(wdpos_corr_only, f"{args.out_prefix}.wdpos_corr_not_comigrator.txt")

    # WD==0 lists
    write_pairs(wd_zero & ~corr_found & ~comi_found, f"{args.out_prefix}.wdzero_missing_both.txt")
    write_pairs(wd_zero & (corr_found | comi_found), f"{args.out_prefix}.wdzero_has_corr_or_comigrator.txt")

    write_pairs(wdzero_comi_ge, f"{args.out_prefix}.wdzero_comigrator_ge_{args.comi_thresh:.2f}.txt")

    print("=== SUMMARY ===")
    print(f"Total rows: {len(df)}")
    print("")
    print(f"WD > 0: {n_wd_pos}")
    print(f"WD > 0 with correlation found: {n_wd_pos_corr}")
    print(f"WD > 0 with CoMigratorScore found: {n_wd_pos_comi}")
    print(f"WD > 0 missing BOTH (correlation + CoMigratorScore): {n_wd_pos_missing_both}")
    print(f"WD > 0 correlation found BUT CoMigratorScore notFound: {n_wdpos_corr_only}")
    print("")
    print(f"WD == 0: {n_wd_zero}")
    print(f"WD == 0 missing BOTH (notFound in both): {n_wd_zero_missing_both}")
    print(f"WD == 0 with correlation OR CoMigratorScore found: {n_wd_zero_corr_or_comi}")
    print(f"  WD == 0 with correlation found: {n_wd_zero_corr_found}")
    print(f"  WD == 0 with CoMigratorScore found: {n_wd_zero_comi_found}")
    print(f"WD == 0 with CoMigratorScore >= {args.comi_thresh:.2f}: {n_wdzero_comi_ge}")
    print("")
    print("Wrote:")
    print(f"  {args.out_prefix}.wdpos_missing_both.txt")
    print(f"  {args.out_prefix}.wdpos_missing_comigrator.txt")
    print(f"  {args.out_prefix}.wdpos_missing_correlation.txt")
    print(f"  {args.out_prefix}.wdpos_corr_not_comigrator.txt")
    print(f"  {args.out_prefix}.wdzero_missing_both.txt")
    print(f"  {args.out_prefix}.wdzero_has_corr_or_comigrator.txt")
    print(f"  {args.out_prefix}.wdzero_comigrator_ge_{args.comi_thresh:.2f}.txt")

if __name__ == "__main__":
    main()
