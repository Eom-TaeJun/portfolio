from scipy.stats import binom
import matplotlib.pyplot as plt

# Parameters
total_balls = 75
remaining_balls = total_balls - 6  # Remaining balls after assigning 1 ball to each bin
max_k_with_min = remaining_balls // 6 + 1  # Maximum value for e or f with minimum constraint

# Calculate exact probabilities for b + c = k and b + c >= k for k from 25 to 40
probabilities_exact_bc = {}
probabilities_gte_bc = {}

for threshold in range(25, 41):
    prob_for_exact_threshold = 0  # Reset probability for exact threshold
    prob_for_gte_threshold = 0  # Reset probability for greater or equal threshold
    
    for k1 in range(1, max_k_with_min + 1):
        for k2 in range(1, k1 + 1):  # k2 <= k1
            remaining_after_ef = remaining_balls - k1 - k2
            
            if remaining_after_ef < 0:
                continue
            
            # Probability of e = k1 and f = k2
            prob_ef = 1 / ((max_k_with_min) * (max_k_with_min + 1) / 2)  # Uniform distribution of (e, f) pairs
            
            # Probability of b + c = threshold given e = k1, f = k2
            prob_bc_exact = binom.pmf(threshold, remaining_after_ef, 2/4)
            prob_for_exact_threshold += prob_ef * prob_bc_exact
            
            # Probability of b + c >= threshold given e = k1, f = k2
            prob_bc_gte = 1 - binom.cdf(threshold - 1, remaining_after_ef, 2/4)
            prob_for_gte_threshold += prob_ef * prob_bc_gte
    
    # Store the results
    probabilities_exact_bc[threshold] = prob_for_exact_threshold
    probabilities_gte_bc[threshold] = prob_for_gte_threshold

# Prepare data for output and graphing
exact_thresholds_bc = list(probabilities_exact_bc.keys())
exact_probabilities_bc = [p * 100 for p in probabilities_exact_bc.values()]  # Convert to percentages
gte_probabilities_bc = [p * 100 for p in probabilities_gte_bc.values()]  # Convert to percentages

# Print probabilities as percentages
print("Threshold | P(b + c = k) (%) | P(b + c >= k) (%)")
print("------------------------------------------------")
for threshold in exact_thresholds_bc:
    exact = probabilities_exact_bc[threshold] * 100
    gte = probabilities_gte_bc[threshold] * 100
    print(f"   {threshold:>2}       |    {exact:>6.2f}%         |    {gte:>6.2f}%")

# Plotting the graph
plt.figure(figsize=(12, 8))

# Plot exact probabilities
plt.bar(exact_thresholds_bc, exact_probabilities_bc, color='lightblue', edgecolor='black', alpha=0.7, label='P(b + c = k) (%)')

# Plot cumulative probabilities (k or greater)
plt.plot(exact_thresholds_bc, gte_probabilities_bc, marker='o', color='orange', label='P(b + c >= k) (%)')

plt.title("Probability of b + c = k and b + c >= k", fontsize=16)
plt.xlabel("k (b + c)", fontsize=14)
plt.ylabel("Probability (%)", fontsize=14)
plt.xticks(exact_thresholds_bc)  # Show all thresholds on the x-axis
plt.grid(axis='y', alpha=0.5)
plt.legend(fontsize=12)
plt.tight_layout()
plt.show()


import math

# Existing cumulative probabilities for b + c >= k
cumulative_probabilities = {
    30: 0.3648, 31: 0.2872, 32: 0.2187, 33: 0.1609,
    34: 0.1143, 35: 0.0782, 36: 0.0515, 37: 0.0326,
    38: 0.0198, 39: 0.0115, 40: 0.0064
}

# Failure thresholds
failure_thresholds = [0.1, 0.2, 0.3, 0.4, 0.5]

# Calculate minimum attempts for all k-values and thresholds
minimum_attempts_results = {}

for k, p in cumulative_probabilities.items():
    q = 1 - p  # Failure probability
    minimum_attempts_results[k] = {}
    for t in failure_thresholds:
        # Calculate minimum attempts
        if q > 0:
            m = math.ceil(math.log(t) / math.log(q))
        else:
            m = 1  # If success probability is 1, only one attempt is needed
        minimum_attempts_results[k][t] = m

# Display the results
print("Minimum attempts (m) for given failure thresholds:")
print("변구합 | 실패할 확률 | 최소한의 재분배 수")
print("----------------------------------------")
for k, thresholds in minimum_attempts_results.items():
    for t, m in thresholds.items():
        print(f"   {k:>2}     |    {t*100:>3.0f}%     |     {m}")

