from src.crew import run_daily_ai_radar


if __name__ == "__main__":
    output_paths = run_daily_ai_radar()
    print("Daily AI Radar complete.")
    for label, path in output_paths.items():
        print(f"{label}: {path}")
