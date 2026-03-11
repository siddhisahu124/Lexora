import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os


def generate_revenue_chart(values, doc_id):
    nums = []
    labels = []

    for i, v in enumerate(values):
        try:
            cleaned = v.replace("$", "").replace(",", "").replace("€", "").replace("£", "")
            nums.append(float(cleaned))
            labels.append(f"#{i+1}")
        except:
            continue

    if not nums:
        return None

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(labels, nums, marker="o", linewidth=2, color="#2563eb", markersize=8)
    ax.fill_between(range(len(nums)), nums, alpha=0.1, color="#2563eb")

    ax.set_title("Revenue Mentions Trend", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Occurrence", fontsize=11)
    ax.set_ylabel("Value (USD)", fontsize=11)

    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"${x:,.0f}")
    )

    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()

    path = f"vectorstore/{doc_id}/revenue_chart.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    plt.savefig(path, dpi=150)
    plt.close()

    return path