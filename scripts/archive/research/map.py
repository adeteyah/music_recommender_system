def precision_at_k(relevances, k):
    """Calculate precision at rank k."""
    relevant_items = relevances[:k]
    return sum(relevant_items) / k


def average_precision(relevances):
    """Calculate Average Precision (AP) for a single user."""
    precisions = []
    num_relevant = 0

    for i, relevance in enumerate(relevances):
        if relevance == 1:
            num_relevant += 1
            precisions.append(precision_at_k(relevances, i + 1))

    if num_relevant == 0:
        return 0.0

    return sum(precisions) / num_relevant


def mean_average_precision(recommendations, relevances):
    """Calculate Mean Average Precision (MAP) for all users."""
    ap_scores = []

    for relevance in relevances:
        ap_scores.append(average_precision(relevance))

    return sum(ap_scores) / len(ap_scores)

# Example usage:
# Assuming 3 users, with 5 recommendations each
# Relevance lists: 1 means relevant, 0 means not relevant


relevances = [
    [1, 0, 1, 0, 0],  # Hani
    [0, 1, 0, 1, 0],  # User 2 relevances
    [0, 0, 0, 0, 1]   # User 3 relevances
]

# Calculate MAP
map_score = mean_average_precision(recommendations=None, relevances=relevances)
print(f"Mean Average Precision (MAP): {map_score:.4f}")
