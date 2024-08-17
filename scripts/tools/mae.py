def calculate_mae(y_true, y_pred):
    absolute_errors = [abs(true - pred) for true, pred in zip(y_true, y_pred)]
    return sum(absolute_errors) / len(y_true)


# Example lists
y_true_list = [
    [1, 1, 1, 0, 1, 1, 1, 0, 1, 1],  # syifa
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 1]
]

y_pred_list = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Calculate MAE for each pair
mae_list = [calculate_mae(y_true, y_pred)
            for y_true, y_pred in zip(y_true_list, y_pred_list)]

# Print MAE for each pair
for i, mae in enumerate(mae_list, 1):
    print(f"MAE for pair {i}: {mae}")
