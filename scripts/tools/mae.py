# Define the true and predicted values
y_true = [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1,
          1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
y_pred = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
          1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

# Calculate the absolute errors
absolute_errors = [abs(true - pred) for true, pred in zip(y_true, y_pred)]

# Calculate the Mean Absolute Error (MAE)
mae = sum(absolute_errors) / len(y_true)

# Print the result
print(f"Mean Absolute Error (MAE): {mae}")
