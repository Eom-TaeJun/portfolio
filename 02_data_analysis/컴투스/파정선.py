from scipy.stats import binom
import matplotlib.pyplot as plt

# Parameters
total_balls = 75
remaining_balls = total_balls - 6  # Remaining balls after assigning 1 ball to each bin
max_k_with_min = remaining_balls // 6 + 1  # Maximum value for e or f with minimum constraint

# Calculate exact probabilities for a + b + c = k and a + b + c >= k for k from 38 to 52
probabilities_exact_abc = {}
probabilities_gte_abc = {}

for threshold in range(38, 55):
    prob_for_exact_threshold = 0  # Reset probability for exact threshold
    prob_for_gte_threshold = 0  # Reset probability for greater or equal threshold
    
    for k1 in range(1, max_k_with_min + 1):
        for k2 in range(1, k1 + 1):  # k2 <= k1
            remaining_after_ef = remaining_balls - k1 - k2
            
            if remaining_after_ef < 0:
                continue
            
            # Probability of e = k1 and f = k2
            prob_ef = 1 / ((max_k_with_min) * (max_k_with_min + 1) / 2)  # Uniform distribution of (e, f) pairs
            
            # Probability of a + b + c = threshold given e = k1, f = k2
            prob_abc_exact = binom.pmf(threshold, remaining_after_ef, 3/4)
            prob_for_exact_threshold += prob_ef * prob_abc_exact
            
            # Probability of a + b + c >= threshold given e = k1, f = k2
            prob_abc_gte = 1 - binom.cdf(threshold - 1, remaining_after_ef, 3/4)
            prob_for_gte_threshold += prob_ef * prob_abc_gte
    
    # Store the results
    probabilities_exact_abc[threshold] = prob_for_exact_threshold
    probabilities_gte_abc[threshold] = prob_for_gte_threshold

# Prepare data for output and graphing
exact_thresholds_abc = list(probabilities_exact_abc.keys())
exact_probabilities_abc = [p * 100 for p in probabilities_exact_abc.values()]  # Convert to percentages
gte_probabilities_abc = [p * 100 for p in probabilities_gte_abc.values()]  # Convert to percentages

# Print probabilities as percentages
print("Threshold | P(a + b + c = k) (%) | P(a + b + c >= k) (%)")
print("-------------------------------------------------------")
for threshold in exact_thresholds_abc:
    exact = probabilities_exact_abc[threshold] * 100
    gte = probabilities_gte_abc[threshold] * 100
    print(f"   {threshold:>2}       |    {exact:>6.2f}%         |    {gte:>6.2f}%")

# Plotting the graph
plt.figure(figsize=(12, 8))

# Plot exact probabilities
plt.bar(exact_thresholds_abc, exact_probabilities_abc, color='skyblue', edgecolor='black', alpha=0.7, label='P(a + b + c = k) (%)')

# Plot cumulative probabilities (k or greater)
plt.plot(exact_thresholds_abc, gte_probabilities_abc, marker='o', color='orange', label='P(a + b + c >= k) (%)')

plt.title("Probability of a + b + c = k and a + b + c >= k", fontsize=16)
plt.xlabel("k (a + b + c)", fontsize=14)
plt.ylabel("Probability (%)", fontsize=14)
plt.xticks(exact_thresholds_abc)  # Show all thresholds on the x-axis
plt.grid(axis='y', alpha=0.5)
plt.legend(fontsize=12)
plt.tight_layout()
plt.show()
