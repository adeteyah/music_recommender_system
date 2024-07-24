import math


def precision_at_k(recommended, relevant, k):
    recommended_at_k = recommended[:k]
    relevant_set = set(relevant)
    recommended_set = set(recommended_at_k)
    intersection = recommended_set.intersection(relevant_set)
    precision = len(intersection) / k
    return precision


def recall_at_k(recommended, relevant, k):
    relevant_set = set(relevant)
    recommended_set = set(recommended[:k])
    intersection = recommended_set.intersection(relevant_set)
    recall = len(intersection) / len(relevant_set)
    return recall


def f1_score_at_k(precision, recall):
    if precision + recall == 0:
        return 0
    return 2 * (precision * recall) / (precision + recall)


def mean_absolute_error(recommended_ratings, actual_ratings):
    errors = [abs(pred - actual)
              for pred, actual in zip(recommended_ratings, actual_ratings)]
    return sum(errors) / len(errors)


def root_mean_squared_error(recommended_ratings, actual_ratings):
    squared_errors = [(pred - actual) ** 2 for pred,
                      actual in zip(recommended_ratings, actual_ratings)]
    return math.sqrt(sum(squared_errors) / len(squared_errors))


def evaluate_recommendations(recommended_tracks, relevant_tracks, recommended_ratings, relevant_ratings, k=10):
    # Precision, Recall, and F1 Score
    precision = precision_at_k(recommended_tracks, relevant_tracks, k)
    recall = recall_at_k(recommended_tracks, relevant_tracks, k)
    f1 = f1_score_at_k(precision, recall)

    # MAE and RMSE
    mae = mean_absolute_error(recommended_ratings, relevant_ratings)
    rmse = root_mean_squared_error(recommended_ratings, relevant_ratings)

    return precision, recall, f1, mae, rmse


if __name__ == "__main__":
    # Example inputs
    recommended_tracks = ['track1', 'track2', 'track3', 'track4', 'track5']
    relevant_tracks = ['track2', 'track3', 'track6']
    # Predicted ratings for recommended tracks
    recommended_ratings = [4.5, 4.0, 3.5, 3.0, 2.5]
    relevant_ratings = [4.0, 4.5, 3.0]  # Actual ratings for relevant tracks

    # Evaluate recommendations
    precision, recall, f1, mae, rmse = evaluate_recommendations(
        recommended_tracks, relevant_tracks, recommended_ratings, relevant_ratings, k=3)

    # Print the evaluation metrics
    print(f"Precision@3: {precision:.4f}")
    print(f"Recall@3: {recall:.4f}")
    print(f"F1 Score@3: {f1:.4f}")
    print(f"Mean Absolute Error: {mae:.4f}")
    print(f"Root Mean Squared Error: {rmse:.4f}")
