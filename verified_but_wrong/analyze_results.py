from stats_summary import build_stats_summary

if __name__ == "__main__":
    result = build_stats_summary()
    print(result["wilson_95_intervals"])
