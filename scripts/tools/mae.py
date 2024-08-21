def calculate_mae(y_true, y_pred):
    absolute_errors = [abs(true - pred) for true, pred in zip(y_true, y_pred)]
    return sum(absolute_errors) / len(y_true)


# Example y_true lists
y_true_list = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # hani cf
    [1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # hani cbf
    [1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # hani cf cbf
    [1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # hani cbf cf
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Fixed y_pred list
y_pred = [1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1]

# Calculate MAE for each y_true list
mae_list = [calculate_mae(y_true, y_pred) for y_true in y_true_list]

# Print MAE for each y_true list
for i, mae in enumerate(mae_list, 1):
    print(f"MAE for y_true list {i}: {mae}")
